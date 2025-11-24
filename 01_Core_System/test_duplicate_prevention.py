#!/usr/bin/env python3
"""
Test Duplicate Lead Prevention

This script tests the duplicate lead prevention feature:
1. Creates a test campaign
2. Adds a lead successfully
3. Attempts to add the same phone number again (should fail)
4. Tests bulk import with duplicates (should skip duplicates)
5. Verifies the database constraint is working
"""

import asyncio
import sys
from loguru import logger
from dialer_db_async import AsyncDialerDB


async def test_duplicate_prevention():
    """Test duplicate lead prevention feature."""

    logger.info("=" * 80)
    logger.info("🧪 DUPLICATE LEAD PREVENTION TEST")
    logger.info("=" * 80)

    # Initialize database
    db = AsyncDialerDB("dialer.db")
    await db.init()

    test_campaign_name = "TEST_DUPLICATE_PREVENTION"
    test_phone = "5551234567"
    campaign_id = None
    campaign_id_2 = None

    try:
        # Step 1: Create test campaign
        logger.info("\n📊 Step 1: Creating test campaign...")
        campaign_id = await db.create_campaign(
            name=test_campaign_name,
            description="Test campaign for duplicate prevention",
        )
        logger.info(f"✅ Campaign created with ID: {campaign_id}")

        # Step 2: Add first lead (should succeed)
        logger.info(f"\n📊 Step 2: Adding lead with phone {test_phone} (first time)...")
        lead_id_1 = await db.add_lead(
            campaign_id=campaign_id,
            phone_number=test_phone,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        if lead_id_1:
            logger.info(f"✅ First lead added successfully with ID: {lead_id_1}")
        else:
            logger.error("❌ First lead was not added (unexpected)")
            return False

        # Step 3: Try to add same phone number again (should return None)
        logger.info(
            f"\n📊 Step 3: Attempting to add duplicate lead with phone {test_phone}..."
        )
        lead_id_2 = await db.add_lead(
            campaign_id=campaign_id,
            phone_number=test_phone,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )

        if lead_id_2 is None:
            logger.info("✅ Duplicate correctly rejected (returned None)")
        else:
            logger.error(f"❌ FAIL: Duplicate lead was added with ID: {lead_id_2}")
            return False

        # Step 4: Verify only one lead exists
        logger.info(f"\n📊 Step 4: Verifying lead count...")
        async with db.db.execute(
            "SELECT COUNT(*) FROM leads WHERE campaign_id = ? AND phone_number = ?",
            (campaign_id, test_phone),
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0]

        if count == 1:
            logger.info(f"✅ Correct: Only 1 lead exists for phone {test_phone}")
        else:
            logger.error(
                f"❌ FAIL: Found {count} leads for phone {test_phone} (expected 1)"
            )
            return False

        # Step 5: Test bulk import with duplicates
        logger.info(f"\n📊 Step 5: Testing bulk import with duplicates...")
        bulk_leads = [
            {"phone_number": "5559876543", "first_name": "Alice", "last_name": "Brown"},
            {
                "phone_number": test_phone,
                "first_name": "Duplicate",
                "last_name": "Entry",
            },  # Duplicate
            {"phone_number": "5559876544", "first_name": "Bob", "last_name": "Green"},
            {
                "phone_number": "5559876543",
                "first_name": "Another",
                "last_name": "Duplicate",
            },  # Duplicate
        ]

        imported = await db.bulk_import_leads(campaign_id, bulk_leads)

        if imported == 2:
            logger.info(
                f"✅ Bulk import correctly imported {imported} leads (skipped 2 duplicates)"
            )
        else:
            logger.error(f"❌ FAIL: Expected 2 imports, got {imported}")
            return False

        # Step 6: Verify final lead count
        logger.info(f"\n📊 Step 6: Verifying final lead count...")
        async with db.db.execute(
            "SELECT COUNT(*) FROM leads WHERE campaign_id = ?", (campaign_id,)
        ) as cursor:
            row = await cursor.fetchone()
            total_count = row[0]

        if total_count == 3:
            logger.info(f"✅ Correct: Total of {total_count} unique leads in campaign")
        else:
            logger.error(f"❌ FAIL: Found {total_count} leads (expected 3)")
            return False

        # Step 7: Test adding same phone to DIFFERENT campaign (should succeed)
        logger.info(f"\n📊 Step 7: Testing same phone in different campaign...")
        campaign_id_2 = await db.create_campaign(
            name="TEST_DUPLICATE_PREVENTION_2", description="Second test campaign"
        )

        lead_id_3 = await db.add_lead(
            campaign_id=campaign_id_2,
            phone_number=test_phone,
            first_name="Cross",
            last_name="Campaign",
        )

        if lead_id_3:
            logger.info(
                f"✅ Same phone added to different campaign successfully (ID: {lead_id_3})"
            )
        else:
            logger.error("❌ FAIL: Should allow same phone in different campaign")
            return False

        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\n📋 Summary:")
        logger.info("  ✓ Duplicate lead prevention working correctly")
        logger.info("  ✓ Database constraint enforced")
        logger.info("  ✓ Bulk import skips duplicates gracefully")
        logger.info("  ✓ Same phone allowed across different campaigns")

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED with exception: {e}", exc_info=True)
        return False

    finally:
        # Cleanup: Delete test campaigns
        logger.info("\n🧹 Cleaning up test data...")
        try:
            if campaign_id is not None:
                await db.delete_campaign(campaign_id)
                logger.info(f"  ✓ Deleted campaign {campaign_id}")
            if campaign_id_2 is not None:
                await db.delete_campaign(campaign_id_2)
                logger.info(f"  ✓ Deleted campaign {campaign_id_2}")
        except Exception as e:
            logger.warning(f"  ⚠️ Cleanup error: {e}")

        await db.close()


if __name__ == "__main__":
    result = asyncio.run(test_duplicate_prevention())
    sys.exit(0 if result else 1)
