#!/usr/bin/env python3
"""
Test script to verify the race condition fix in lead selection.

This script simulates multiple concurrent dialers trying to claim leads
to verify that the atomic UPDATE...RETURNING pattern prevents duplicate
lead assignment.
"""

import asyncio
import sys
from datetime import datetime
from dialer_db_async import AsyncDialerDB
from loguru import logger

# Configure logger for test
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
)


async def simulate_dialer(
    db: AsyncDialerDB, dialer_id: int, campaign_id: int, num_claims: int
):
    """Simulate a dialer process claiming leads."""
    claimed_lead_ids = []

    for i in range(num_claims):
        try:
            leads = await db.claim_next_leads(campaign_id, limit=5)

            for lead in leads:
                lead_id = lead["id"]
                claimed_lead_ids.append(lead_id)
                logger.info(
                    f"Dialer {dialer_id}: Claimed lead {lead_id} (phone: {lead['phone_number']})"
                )

            # Small delay to simulate processing
            await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(f"Dialer {dialer_id}: Error claiming leads: {e}")

    return dialer_id, claimed_lead_ids


async def test_race_condition():
    """Test that concurrent dialers don't claim the same lead."""
    logger.info("=" * 80)
    logger.info("RACE CONDITION TEST - Atomic Lead Claiming")
    logger.info("=" * 80)

    # Initialize database
    db = AsyncDialerDB("test_dialer.db")
    await db.init()

    # Create test campaign
    logger.info("\n1. Creating test campaign...")
    campaign_id = await db.create_campaign(
        name="Test Campaign - Race Condition",
        description="Testing atomic lead claiming",
        dial_method="PROGRESSIVE",
    )
    logger.success(f"   Created campaign ID: {campaign_id}")

    # Add test leads
    logger.info("\n2. Adding 50 test leads...")
    for i in range(50):
        await db.add_lead(
            campaign_id=campaign_id,
            phone_number=f"555010{i:04d}",
            first_name=f"Test{i}",
            last_name="User",
        )
    logger.success("   Added 50 test leads")

    # Start campaign
    await db.start_campaign(campaign_id)
    logger.info(f"   Started campaign {campaign_id}")

    # Simulate 5 concurrent dialers each trying to claim 5 batches of 5 leads
    logger.info("\n3. Simulating 5 concurrent dialers (each claiming 5 batches)...")
    logger.info("   Expected: Each lead claimed exactly once, no duplicates")

    # Launch concurrent dialers
    tasks = [
        simulate_dialer(db, dialer_id=i, campaign_id=campaign_id, num_claims=5)
        for i in range(5)
    ]

    results = await asyncio.gather(*tasks)

    # Analyze results
    logger.info("\n4. Analyzing results...")
    all_claimed_leads = []
    for dialer_id, claimed_leads in results:
        logger.info(f"   Dialer {dialer_id}: Claimed {len(claimed_leads)} leads")
        all_claimed_leads.extend(claimed_leads)

    # Check for duplicates
    unique_leads = set(all_claimed_leads)
    total_claimed = len(all_claimed_leads)
    total_unique = len(unique_leads)

    logger.info(f"\n5. Results:")
    logger.info(f"   Total leads claimed: {total_claimed}")
    logger.info(f"   Unique leads claimed: {total_unique}")
    logger.info(f"   Duplicates: {total_claimed - total_unique}")

    if total_claimed == total_unique:
        logger.success(
            "\n✅ PASS: No race condition detected! Each lead was claimed exactly once."
        )
    else:
        logger.error(
            f"\n❌ FAIL: Race condition detected! {total_claimed - total_unique} duplicate claims."
        )

        # Find duplicates
        from collections import Counter

        duplicates = [
            lead_id
            for lead_id, count in Counter(all_claimed_leads).items()
            if count > 1
        ]
        logger.error(f"   Duplicate lead IDs: {duplicates}")

    # Verify database state
    logger.info("\n6. Verifying database state...")
    async with db.db.execute(
        "SELECT COUNT(*) FROM leads WHERE campaign_id = ? AND status = 'CALLING'",
        (campaign_id,),
    ) as cursor:
        result = await cursor.fetchone()
        calling_count = result[0]

    logger.info(f"   Leads in CALLING status: {calling_count}")
    logger.info(f"   Expected: {total_unique}")

    if calling_count == total_unique:
        logger.success("   Database state is consistent!")
    else:
        logger.error(
            f"   Database inconsistency! Expected {total_unique}, got {calling_count}"
        )

    # Cleanup
    await db.delete_campaign(campaign_id)
    await db.close()

    logger.info("\n" + "=" * 80)
    return total_claimed == total_unique


async def test_old_method_race_condition():
    """Test that the old method DOES have a race condition (for comparison)."""
    logger.info("=" * 80)
    logger.info("CONTROL TEST - Old Method (get_next_leads + mark_lead_calling)")
    logger.info("=" * 80)

    # Initialize database
    db = AsyncDialerDB("test_dialer_old.db")
    await db.init()

    # Create test campaign
    logger.info("\n1. Creating test campaign...")
    campaign_id = await db.create_campaign(
        name="Test Campaign - Old Method",
        description="Testing old non-atomic method",
        dial_method="PROGRESSIVE",
    )
    logger.success(f"   Created campaign ID: {campaign_id}")

    # Add test leads
    logger.info("\n2. Adding 50 test leads...")
    for i in range(50):
        await db.add_lead(
            campaign_id=campaign_id,
            phone_number=f"555020{i:04d}",
            first_name=f"Test{i}",
            last_name="User",
        )
    logger.success("   Added 50 test leads")

    # Start campaign
    await db.start_campaign(campaign_id)

    logger.info("\n3. Using OLD METHOD: get_next_leads() + mark_lead_calling()...")
    logger.info("   Expected: Race conditions may occur with duplicates")

    # Simulate concurrent access using old method
    claimed_leads = []

    async def old_method_dialer(dialer_id: int):
        for _ in range(5):
            # Get leads (not atomic)
            leads = await db.get_next_leads(campaign_id, limit=5)

            # Small delay to increase chance of race condition
            await asyncio.sleep(0.001)

            # Mark leads as calling (separate operation - race condition window!)
            for lead in leads:
                try:
                    await db.mark_lead_calling(lead["id"])
                    claimed_leads.append((dialer_id, lead["id"]))
                    logger.info(
                        f"Old Method Dialer {dialer_id}: Claimed lead {lead['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error: {e}")

    tasks = [old_method_dialer(i) for i in range(5)]
    await asyncio.gather(*tasks)

    # Analyze
    logger.info(f"\n4. Results with old method:")
    logger.info(f"   Total claims: {len(claimed_leads)}")
    unique = len(set(lead_id for _, lead_id in claimed_leads))
    logger.info(f"   Unique leads: {unique}")
    logger.info(f"   Duplicates: {len(claimed_leads) - unique}")

    if len(claimed_leads) > unique:
        logger.warning(
            f"   ⚠️ Race condition detected with old method! {len(claimed_leads) - unique} duplicates."
        )
    else:
        logger.info("   No race condition detected (but old method is still not safe)")

    # Cleanup
    await db.delete_campaign(campaign_id)
    await db.close()

    logger.info("\n" + "=" * 80)


async def main():
    """Run all tests."""
    logger.info("\n🧪 TESTING RACE CONDITION FIX FOR LEAD SELECTION\n")

    # Test new atomic method
    test1_passed = await test_race_condition()

    await asyncio.sleep(1)

    # Test old method (for comparison)
    # await test_old_method_race_condition()

    if test1_passed:
        logger.success("\n✅ ALL TESTS PASSED - Race condition is fixed!")
        return 0
    else:
        logger.error("\n❌ TESTS FAILED - Race condition still exists!")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
