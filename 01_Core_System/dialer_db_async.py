#!/usr/bin/env python3
"""
Async Dialer Database Interface - Async/await version with aiosqlite.

Provides async Python API for:
- Campaign management
- Lead operations
- Call logging
- Statistics queries
- DNC list management

Usage:
    db = AsyncDialerDB("dialer.db")
    await db.init()
    campaign_id = await db.create_campaign("Test Campaign")
    await db.add_lead(campaign_id, "5551234567", "John", "Doe")
"""

import aiosqlite
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger

try:
    from dialer_logging import get_logger, PerformanceLogger

    struct_logger = get_logger("dialer_db_async")
    STRUCTURED_LOGGING = True
except ImportError:
    STRUCTURED_LOGGING = False
    struct_logger = None


class AsyncDialerDB:
    """Async database interface for Exodus dialer."""

    def __init__(self, db_path: str = "dialer.db"):
        """Initialize async database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db = None
        logger.info(f"🔗 Async database interface initialized: {db_path}")

    async def init(self):
        """Initialize database connection and schema."""
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row

        # AGGRESSIVE SQLite optimization for high-concurrency dialing
        await self.db.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        await self.db.execute("PRAGMA busy_timeout=60000")  # 60 second wait
        await self.db.execute("PRAGMA cache_size=-128000")  # 128MB cache (doubled)
        await self.db.execute("PRAGMA temp_store=MEMORY")  # RAM for temp tables
        await self.db.execute("PRAGMA synchronous=NORMAL")  # Fast but safe (WAL mode)
        await self.db.execute(
            "PRAGMA wal_autocheckpoint=1000"
        )  # Checkpoint every 1000 pages
        await self.db.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        await self.db.commit()

        await self._init_database()
        logger.info(
            f"✅ Async database connected: {self.db_path} (HIGH-CONCURRENCY MODE)"
        )

    async def _init_database(self):
        """Initialize database schema if not exists."""
        try:
            # Check if campaigns table exists
            async with self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'"
            ) as cursor:
                if await cursor.fetchone():
                    logger.info(f"✅ Database already initialized")
                    return

            # Database doesn't exist, create it
            with open("dialer_database.sql", "r") as f:
                schema_sql = f.read()

            await self.db.executescript(schema_sql)
            await self.db.commit()
            logger.info(f"✅ Database schema created")
        except FileNotFoundError:
            logger.error(f"❌ Schema file not found: dialer_database.sql")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            logger.info("🔗 Async database connection closed")

    # ========================================================================
    # CAMPAIGN OPERATIONS
    # ========================================================================

    async def create_campaign(
        self,
        name: str,
        description: str = "",
        dial_method: str = "PROGRESSIVE",
        dial_ratio: float = 3.0,
        max_dial_ratio: float = 5.0,
        stt_provider: str = "deepgram",
        enable_recording: bool = False,
        max_attempts: int = 3,
        retry_delay: int = 300,
        call_timeout: int = 45,
        working_hours_start: str = "09:00",
        working_hours_end: str = "21:00",
    ) -> int:
        """Create a new campaign.

        Args:
            name: Campaign name (must be unique)
            description: Campaign description
            dial_method: PROGRESSIVE, PREDICTIVE, POWER, or PREVIEW
            dial_ratio: Initial dial ratio (calls per bot)
            max_dial_ratio: Maximum dial ratio
            stt_provider: STT service to use (deepgram or groq)
            enable_recording: Enable call recordings
            max_attempts: Maximum call attempts per lead
            retry_delay: Seconds between retry attempts
            call_timeout: Seconds before timing out a call
            working_hours_start: Start of working hours (HH:MM format)
            working_hours_end: End of working hours (HH:MM format)

        Returns:
            Campaign ID
        """
        logger.debug(
            f"📊 DB: Creating campaign '{name}', method={dial_method}, ratio={dial_ratio}, "
            f"max_attempts={max_attempts}, retry_delay={retry_delay}, call_timeout={call_timeout}, "
            f"working_hours={working_hours_start}-{working_hours_end}"
        )

        try:
            async with self.db.execute(
                """
                INSERT INTO campaigns (
                    name, description, dial_method, dial_ratio, max_dial_ratio, 
                    stt_provider, enable_recording, max_attempts, retry_delay, 
                    call_timeout, working_hours_start, working_hours_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    description,
                    dial_method,
                    dial_ratio,
                    max_dial_ratio,
                    stt_provider,
                    1 if enable_recording else 0,
                    max_attempts,
                    retry_delay,
                    call_timeout,
                    working_hours_start,
                    working_hours_end,
                ),
            ) as cursor:
                campaign_id = cursor.lastrowid

            await self.db.commit()
            logger.info(f"✅ DB: Campaign created: {name} (ID: {campaign_id})")
            return campaign_id
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to create campaign '{name}': {str(e)}", exc_info=True
            )
            raise

    async def start_campaign(self, campaign_id: int):
        """Start a campaign (set status to ACTIVE)."""
        logger.debug(f"📊 DB: Starting campaign ID={campaign_id}")
        try:
            await self.db.execute(
                "UPDATE campaigns SET status = 'ACTIVE', started_at = CURRENT_TIMESTAMP WHERE id = ?",
                (campaign_id,),
            )
            await self.db.commit()
            logger.info(f"▶️ DB: Campaign {campaign_id} started")
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to start campaign {campaign_id}: {str(e)}",
                exc_info=True,
            )
            raise

    async def pause_campaign(self, campaign_id: int):
        """Pause a campaign (set status to PAUSED)."""
        logger.debug(f"📊 DB: Pausing campaign ID={campaign_id}")
        try:
            await self.db.execute(
                "UPDATE campaigns SET status = 'PAUSED' WHERE id = ?", (campaign_id,)
            )
            await self.db.commit()
            logger.info(f"⏸️ DB: Campaign {campaign_id} paused")
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to pause campaign {campaign_id}: {str(e)}",
                exc_info=True,
            )
            raise

    async def get_campaign(self, campaign_id: int) -> Optional[Dict]:
        """Get campaign details."""
        async with self.db.execute(
            "SELECT * FROM campaigns WHERE id = ?", (campaign_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns."""
        async with self.db.execute(
            "SELECT * FROM campaigns WHERE status = 'ACTIVE'"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ========================================================================
    # SECURITY: Whitelist for update_campaign fields (SQL injection protection)
    # ========================================================================
    ALLOWED_CAMPAIGN_FIELDS = {
        "name",
        "description",
        "dial_method",
        "dial_ratio",
        "max_dial_ratio",
        "stt_provider",
        "enable_recording",
        "status",
        "started_at",
        "updated_at",
        "max_attempts",
        "retry_delay",
        "call_timeout",
        "working_hours_start",
        "working_hours_end",
    }

    async def update_campaign(self, campaign_id: int, campaign_data: dict):
        """Update campaign details with field validation (SQL injection protection)."""
        # Build UPDATE query from provided fields
        fields = []
        values = []

        for key, value in campaign_data.items():
            if key != "id":  # Don't allow updating ID
                # SECURITY: Validate field names against whitelist
                if key not in self.ALLOWED_CAMPAIGN_FIELDS:
                    logger.warning(
                        f"⚠️ SECURITY: Attempted to update invalid campaign field: {key}"
                    )
                    raise ValueError(
                        f"Invalid campaign field: {key}. Allowed fields: {', '.join(sorted(self.ALLOWED_CAMPAIGN_FIELDS))}"
                    )

                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return

        values.append(campaign_id)
        query = f"UPDATE campaigns SET {', '.join(fields)} WHERE id = ?"

        await self.db.execute(query, tuple(values))
        await self.db.commit()
        logger.info(f"📝 Campaign {campaign_id} updated")

    async def delete_campaign(self, campaign_id: int):
        """Delete a campaign and all associated leads."""
        # Delete associated leads first
        await self.db.execute("DELETE FROM leads WHERE campaign_id = ?", (campaign_id,))

        # Delete campaign
        await self.db.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))

        await self.db.commit()
        logger.info(f"🗑️  Campaign {campaign_id} deleted")

    # ========================================================================
    # LEAD OPERATIONS
    # ========================================================================

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format (+1XXXXXXXXXX for US).

        Prevents double +1 prefix bugs.

        Args:
            phone: Raw phone number in any format

        Returns:
            Normalized phone number in E.164 format
        """
        # Remove all non-digits
        digits = "".join(c for c in phone if c.isdigit())

        # Apply normalization rules
        if len(digits) == 10:
            # 10 digits - US number without country code
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("1"):
            # 11 digits starting with 1 - already has country code
            return f"+{digits}"
        elif len(digits) == 11 and not digits.startswith("1"):
            # 11 digits NOT starting with 1 - add +1
            return f"+1{digits}"
        else:
            # International or other - just add +
            return f"+{digits}"

    async def add_lead(
        self,
        campaign_id: int,
        phone_number: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        company: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        timezone: str = "America/New_York",
        custom_data: Dict = None,
    ) -> int:
        """Add a lead to a campaign.

        Args:
            campaign_id: Campaign ID
            phone_number: Lead's phone number
            first_name: First name
            last_name: Last name
            email: Email address
            company: Company name
            city: City
            state: State
            zip_code: ZIP code
            timezone: Timezone (default: America/New_York)
            custom_data: Additional data as dictionary

        Returns:
            Lead ID
        """
        # Normalize phone number to prevent +11... bugs
        phone_number = self._normalize_phone(phone_number)
        logger.debug(f"📊 DB: Normalized phone number to {phone_number}")

        # Check DNC list
        logger.debug(f"📊 DB: Checking DNC status for {phone_number}")
        if await self.is_in_dnc(phone_number):
            logger.warning(f"⚠️ DB: Phone {phone_number} is in DNC list, not adding")
            if STRUCTURED_LOGGING:
                struct_logger.warning(
                    "lead_rejected_dnc", phone=phone_number, campaign_id=campaign_id
                )
            return None

        custom_json = json.dumps(custom_data) if custom_data else None

        logger.debug(f"📊 DB: Adding lead {phone_number} to campaign {campaign_id}")
        try:
            async with self.db.execute(
                """
                INSERT INTO leads (campaign_id, phone_number, first_name, last_name, email, company, city, state, zip_code, timezone, custom_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    phone_number,
                    first_name,
                    last_name,
                    email,
                    company,
                    city,
                    state,
                    zip_code,
                    timezone,
                    custom_json,
                ),
            ) as cursor:
                lead_id = cursor.lastrowid

            await self.db.commit()

            logger.info(
                f"✅ DB: Lead added - ID={lead_id}, Phone={phone_number}, Campaign={campaign_id}"
            )
            if STRUCTURED_LOGGING:
                struct_logger.info(
                    "lead_added",
                    lead_id=lead_id,
                    phone=phone_number,
                    campaign_id=campaign_id,
                )

            return lead_id
        except Exception as e:
            # Handle duplicate lead constraint violation
            error_msg = str(e)
            if "UNIQUE constraint" in error_msg and (
                "idx_campaign_phone" in error_msg or "campaign_id" in error_msg
            ):
                logger.warning(
                    f"⚠️ DB: Duplicate lead - {phone_number} already exists in campaign {campaign_id}"
                )
                if STRUCTURED_LOGGING:
                    struct_logger.warning(
                        "lead_duplicate",
                        phone=phone_number,
                        campaign_id=campaign_id,
                    )
                return None  # Return None instead of raising error

            logger.error(
                f"❌ DB: Failed to add lead {phone_number}: {str(e)}", exc_info=True
            )
            raise

    async def claim_next_leads(self, campaign_id: int, limit: int = 10) -> List[Dict]:
        """Atomically claim and return next available leads.

        Uses UPDATE...RETURNING pattern to prevent race conditions where multiple
        dialers could get the same lead. This operation is atomic and thread-safe.

        Prioritizes:
        1. Scheduled callbacks (next_call_time <= now)
        2. New leads (status=NEW)

        Args:
            campaign_id: Campaign ID
            limit: Maximum number of leads to claim

        Returns:
            List of claimed lead dictionaries with status already set to CALLING
        """
        logger.debug(
            f"📊 DB: Atomically claiming next {limit} leads for campaign {campaign_id}"
        )

        # Use UPDATE...RETURNING for atomic operation
        # This prevents race conditions by updating and returning in a single transaction
        query = """
            UPDATE leads
            SET status = 'CALLING', 
                attempts = attempts + 1,
                last_call_time = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id IN (
                SELECT id FROM leads
                WHERE campaign_id = ?
                AND status IN ('NEW', 'CALLBACK')
                AND attempts < max_attempts
                AND (next_call_time IS NULL OR next_call_time <= CURRENT_TIMESTAMP)
                ORDER BY
                    CASE WHEN status = 'CALLBACK' THEN 0 ELSE 1 END,
                    next_call_time ASC,
                    created_at ASC
                LIMIT ?
            )
            RETURNING *
        """

        try:
            async with self.db.execute(query, (campaign_id, limit)) as cursor:
                rows = await cursor.fetchall()
                await self.db.commit()

                leads = [dict(row) for row in rows]

            if leads:
                # Note: After UPDATE, status is already CALLING, so we can't count by original status
                # Instead, count callbacks by checking if attempts > 1 or next_call_time was set
                callback_count = sum(
                    1
                    for lead in leads
                    if lead.get("attempts", 0) > 1 or lead.get("next_call_time")
                )
                new_count = len(leads) - callback_count
                logger.info(
                    f"✅ DB: Atomically claimed {len(leads)} leads - {callback_count} callbacks, {new_count} new"
                )
            else:
                logger.info(f"ℹ️ DB: No available leads for campaign {campaign_id}")

            return leads
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to claim leads for campaign {campaign_id}: {str(e)}",
                exc_info=True,
            )
            await self.db.rollback()
            raise

    async def get_next_leads(self, campaign_id: int, limit: int = 10) -> List[Dict]:
        """Get next leads to dial for a campaign.

        Prioritizes:
        1. Scheduled callbacks (next_call_time <= now)
        2. New leads (status=NEW)

        Args:
            campaign_id: Campaign ID
            limit: Maximum number of leads to return

        Returns:
            List of lead dictionaries
        """
        logger.debug(f"📊 DB: Getting next {limit} leads for campaign {campaign_id}")

        query = """
            SELECT * FROM leads
            WHERE campaign_id = ?
            AND status IN ('NEW', 'CALLBACK')
            AND (
                status = 'NEW'
                OR (status = 'CALLBACK' AND (next_call_time IS NULL OR next_call_time <= CURRENT_TIMESTAMP))
            )
            ORDER BY
                CASE WHEN status = 'CALLBACK' THEN 0 ELSE 1 END,
                next_call_time ASC,
                created_at ASC
            LIMIT ?
        """

        try:
            async with self.db.execute(query, (campaign_id, limit)) as cursor:
                rows = await cursor.fetchall()
                leads = [dict(row) for row in rows]

            if leads:
                callback_count = sum(
                    1 for lead in leads if lead["status"] == "CALLBACK"
                )
                new_count = sum(1 for lead in leads if lead["status"] == "NEW")
                logger.info(
                    f"✅ DB: Retrieved {len(leads)} leads - {callback_count} callbacks, {new_count} new"
                )
            else:
                logger.info(f"ℹ️ DB: No available leads for campaign {campaign_id}")

            return leads
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to get next leads for campaign {campaign_id}: {str(e)}",
                exc_info=True,
            )
            raise

    async def mark_lead_calling(self, lead_id: int):
        """Mark lead as currently being called."""
        logger.debug(f"📊 DB: Marking lead {lead_id} as CALLING")

        try:
            await self.db.execute(
                """
                UPDATE leads
                SET status = 'CALLING', attempts = attempts + 1
                WHERE id = ?
                """,
                (lead_id,),
            )
            await self.db.commit()
            logger.debug(f"📞 DB: Lead {lead_id} marked as CALLING")
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to mark lead {lead_id} as calling: {str(e)}",
                exc_info=True,
            )
            await self.db.rollback()
            raise

    async def mark_leads_calling_batch(self, lead_ids):
        """Batch update leads to CALLING status - reduces lock contention"""
        if not lead_ids:
            return

        try:
            placeholders = ",".join(["?"] * len(lead_ids))
            await self.db.execute(
                f"UPDATE leads SET status='CALLING', attempts=attempts+1, updated_at=CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
                lead_ids,
            )
            await self.db.commit()
            logger.debug(f"📊 DB: Marked {len(lead_ids)} leads as CALLING")
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to mark leads as calling: {str(e)}", exc_info=True
            )
            await self.db.rollback()
            raise

    async def update_lead_after_call(
        self, lead_id: int, disposition: str, callback_days: int = None
    ):
        """Update lead status after call completes.

        Args:
            lead_id: Lead ID
            disposition: Call disposition (ANSWERED, NO_ANSWER, BUSY, FAILED, etc.)
                       or sales disposition (INTERESTED, CALLBACK, DNC, etc.)
            callback_days: Days until callback (if applicable)
        """
        # Handle call statuses (from hangup handler)
        if disposition == "ANSWERED":
            status = "COMPLETED"  # Call was successful
            next_call_time = None
        elif disposition in ("NO_ANSWER", "BUSY", "FAILED", "ABANDONED"):
            status = "NEW"  # Try again later
            next_call_time = None
        # Handle sales dispositions (from agent/API)
        elif disposition in ("INTERESTED", "CALLBACK"):
            status = "CALLBACK"
            next_call_time = datetime.now() + timedelta(days=callback_days or 3)
        elif disposition == "DNC":
            status = "DNC"
            next_call_time = None
            # Add to DNC list
            async with self.db.execute(
                "SELECT phone_number FROM leads WHERE id = ?", (lead_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    await self.add_to_dnc(row[0], "Lead requested DNC")
        elif disposition in ("NOT_INTERESTED", "WRONG_NUMBER"):
            status = "COMPLETED"
            next_call_time = None
        else:
            status = "NEW"  # Retry later (unknown disposition)
            next_call_time = None

        await self.db.execute(
            """
            UPDATE leads
            SET status = ?, next_call_time = ?
            WHERE id = ?
            """,
            (status, next_call_time, lead_id),
        )
        await self.db.commit()

    # ========================================================================
    # CALL LOGGING
    # ========================================================================

    async def log_call(
        self,
        lead_id: int,
        campaign_id: int,
        call_uuid: str,
        bot_port: int,
        start_time: datetime,
        end_time: datetime,
        call_status: str,
        disposition: str = None,
        transcript: str = None,
        recording_url: str = None,
        was_dropped: bool = False,
    ):
        """Log a completed call."""
        duration = (end_time - start_time).total_seconds()

        logger.debug(
            f"📊 DB: Logging call {call_uuid} - Lead={lead_id}, Status={call_status}, Duration={duration:.1f}s"
        )

        try:
            await self.db.execute(
                """
                INSERT OR REPLACE INTO call_log (
                    lead_id, campaign_id, call_uuid, bot_port,
                    start_time, end_time, duration_seconds,
                    call_status, disposition_code, transcription_text, recording_url, was_dropped
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lead_id,
                    campaign_id,
                    call_uuid,
                    bot_port,
                    start_time,
                    end_time,
                    duration,
                    call_status,
                    disposition,
                    transcript,
                    recording_url,
                    was_dropped,
                ),
            )
            await self.db.commit()

            logger.info(f"✅ DB: Call logged - {call_uuid} ({call_status})")
            if was_dropped:
                logger.warning(f"   ⚠️ Call was dropped (TCPA concern)")
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to log call {call_uuid}: {str(e)}", exc_info=True
            )
            raise

    async def update_call_transcript(
        self, call_uuid: str, transcript: str, disposition: str
    ):
        """Update call log with transcript and disposition.

        Args:
            call_uuid: Call UUID to update
            transcript: Full conversation transcript
            disposition: Auto-analyzed disposition code
        """
        logger.debug(
            f"📝 DB: Updating transcript for call {call_uuid}, disposition={disposition}"
        )

        try:
            await self.db.execute(
                """
                UPDATE call_log
                SET transcription_text = ?, disposition_code = ?
                WHERE call_uuid = ?
                """,
                (transcript, disposition, call_uuid),
            )
            await self.db.commit()
            logger.info(
                f"✅ DB: Updated transcript for call {call_uuid}: {disposition}"
            )
        except Exception as e:
            logger.error(
                f"❌ DB: Failed to update transcript for call {call_uuid}: {str(e)}",
                exc_info=True,
            )
            raise

    # ========================================================================
    # STATISTICS
    # ========================================================================

    async def get_campaign_stats_today(self, campaign_id: int) -> Optional[Dict]:
        """Get today's statistics for a campaign."""
        query = """
            SELECT * FROM v_todays_stats
            WHERE campaign_id = ?
        """

        async with self.db.execute(query, (campaign_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    # ========================================================================
    # DNC LIST
    # ========================================================================

    async def is_in_dnc(self, phone_number: str) -> bool:
        """Check if phone number is in DNC list."""
        async with self.db.execute(
            "SELECT COUNT(*) FROM dnc_list WHERE phone_number = ?", (phone_number,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] > 0

    async def add_to_dnc(self, phone_number: str, reason: str = "Manual"):
        """Add phone number to DNC list."""
        try:
            await self.db.execute(
                "INSERT INTO dnc_list (phone_number, reason) VALUES (?, ?)",
                (phone_number, reason),
            )
            await self.db.commit()
            logger.info(f"🚫 Added to DNC: {phone_number}")
        except Exception as e:
            logger.error(f"Failed to add to DNC: {e}")

    async def bulk_import_leads(self, campaign_id: int, leads: List[Dict]) -> int:
        """Bulk import leads for a campaign.

        Args:
            campaign_id: Campaign ID
            leads: List of lead dictionaries

        Returns:
            Number of leads imported (skips duplicates and DNC entries)
        """
        imported = 0
        skipped_duplicates = 0
        skipped_dnc = 0

        for lead_data in leads:
            try:
                lead_id = await self.add_lead(
                    campaign_id=campaign_id,
                    phone_number=lead_data["phone_number"],
                    first_name=lead_data.get("first_name", ""),
                    last_name=lead_data.get("last_name", ""),
                    email=lead_data.get("email", ""),
                    company=lead_data.get("company", ""),
                    city=lead_data.get("city", ""),
                    state=lead_data.get("state", ""),
                    zip_code=lead_data.get("zip_code", ""),
                    timezone=lead_data.get("timezone", "America/New_York"),
                )

                if lead_id is None:
                    # Lead was rejected (DNC or duplicate)
                    skipped_duplicates += 1
                else:
                    imported += 1
            except Exception as e:
                logger.warning(
                    f"Failed to import lead {lead_data.get('phone_number', 'unknown')}: {e}"
                )

        if skipped_duplicates > 0:
            logger.info(
                f"📊 Bulk import summary: {imported} imported, {skipped_duplicates} skipped (duplicates/DNC)"
            )

        return imported

    async def get_leads_by_campaign(
        self, campaign_id: int, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """Get all leads for a specific campaign.

        Args:
            campaign_id: Campaign ID
            limit: Maximum number of leads to return
            offset: Number of leads to skip

        Returns:
            List of lead dictionaries
        """
        async with self.db.execute(
            """
            SELECT id, campaign_id, phone_number, first_name, last_name, email, company,
                   city, state, zip_code, timezone, status, attempts, max_attempts,
                   last_call_time, next_call_time, created_at, updated_at
            FROM leads
            WHERE campaign_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """,
            (campaign_id, limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            leads = []
            for row in rows:
                lead = dict(zip(columns, row))
                # Convert datetime objects to ISO strings
                for key, value in lead.items():
                    if hasattr(value, "isoformat"):
                        lead[key] = value.isoformat()
                leads.append(lead)

            return leads

    async def get_campaign_lead_count(self, campaign_id: int) -> int:
        """Get total count of leads for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Total number of leads
        """
        async with self.db.execute(
            """
            SELECT COUNT(*) FROM leads WHERE campaign_id = ?
        """,
            (campaign_id,),
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def calculate_drop_rate(
        self, campaign_id: Optional[int] = None, days: int = 30
    ) -> float:
        """Calculate drop rate for recent calls (TCPA compliance).

        Args:
            campaign_id: Campaign ID (if None, calculates across all campaigns)
            days: Time window in days (TCPA requires 30-day rolling window)

        Returns:
            Drop rate (0.0-1.0)
        """
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)

        if campaign_id is not None:
            # Single campaign
            async with self.db.execute(
                """
                SELECT
                    CAST(SUM(CASE WHEN was_dropped = 1 THEN 1 ELSE 0 END) AS REAL) /
                    NULLIF(SUM(CASE WHEN call_status = 'ANSWERED' THEN 1 ELSE 0 END), 0) as drop_rate
                FROM call_log
                WHERE campaign_id = ? AND start_time >= ?
                """,
                (campaign_id, cutoff),
            ) as cursor:
                result = await cursor.fetchone()
        else:
            # All campaigns
            async with self.db.execute(
                """
                SELECT
                    CAST(SUM(CASE WHEN was_dropped = 1 THEN 1 ELSE 0 END) AS REAL) /
                    NULLIF(SUM(CASE WHEN call_status = 'ANSWERED' THEN 1 ELSE 0 END), 0) as drop_rate
                FROM call_log
                WHERE start_time >= ?
                """,
                (cutoff,),
            ) as cursor:
                result = await cursor.fetchone()

        return result[0] if result and result[0] else 0.0

    async def get_todays_stats(self) -> dict:
        """Get statistics for today's calls."""
        from datetime import datetime

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Call counts by status
        async with self.db.execute(
            """
            SELECT
                COUNT(*) as total_calls,
                SUM(CASE WHEN call_status = 'ANSWERED' THEN 1 ELSE 0 END) as answered,
                SUM(CASE WHEN call_status = 'NO_ANSWER' THEN 1 ELSE 0 END) as no_answer,
                SUM(CASE WHEN call_status = 'BUSY' THEN 1 ELSE 0 END) as busy,
                SUM(CASE WHEN call_status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN call_status = 'ANSWERED' THEN duration_seconds ELSE NULL END) as avg_duration
            FROM call_log
            WHERE start_time >= ?
            """,
            (today,),
        ) as cursor:
            call_stats = await cursor.fetchone()

        # Disposition breakdown
        dispositions = {}
        async with self.db.execute(
            """
            SELECT disposition_code, COUNT(*) as count
            FROM call_log
            WHERE start_time >= ? AND disposition_code IS NOT NULL
            GROUP BY disposition_code
            """,
            (today,),
        ) as cursor:
            disp_rows = await cursor.fetchall()
            for row in disp_rows:
                dispositions[row[0]] = row[1]

        return {
            "total_calls": call_stats[0] or 0,
            "answered": call_stats[1] or 0,
            "no_answer": call_stats[2] or 0,
            "busy": call_stats[3] or 0,
            "failed": call_stats[4] or 0,
            "avg_duration": round(call_stats[5] or 0, 1),
            "dispositions": dispositions,
        }

    async def get_lead_stats(self) -> dict:
        """Get lead statistics."""
        async with self.db.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as new,
                SUM(CASE WHEN status IN ('CALLED', 'COMPLETED') THEN 1 ELSE 0 END) as called,
                SUM(CASE WHEN status = 'CALLING' THEN 1 ELSE 0 END) as calling,
                SUM(CASE WHEN status = 'SCHEDULED' THEN 1 ELSE 0 END) as scheduled
            FROM leads
            """
        ) as cursor:
            result = await cursor.fetchone()

        return {
            "total": result[0] or 0,
            "new": result[1] or 0,
            "called": result[2] or 0,
            "calling": result[3] or 0,
            "scheduled": result[4] or 0,
        }

    async def get_call_by_id(self, call_id: int):
        """Get call record by ID"""
        try:
            async with self.lock:
                cursor = await self.db.execute(
                    "SELECT * FROM call_log WHERE id = ?", (call_id,)
                )
                row = await cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Failed to get call {call_id}: {e}")
            return None

    async def update_call_disposition(
        self, call_id: int, disposition: str, method: str = "MANUAL"
    ):
        """Update call disposition"""
        try:
            async with self.lock:
                await self.db.execute(
                    "UPDATE call_log SET disposition = ?, disposition_method = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (disposition, method, call_id),
                )
                await self.db.commit()
                logger.info(
                    f"✅ Updated call {call_id} disposition to {disposition} ({method})"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to update disposition for call {call_id}: {e}")
            return False
