# QUICK DEPLOYMENT GUIDE - Database Performance Optimization

## 🚀 Quick Start (5 minutes)

### 1. Backup Database
```bash
cd /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/01_Core_System
cp dialer.db dialer.db.backup
```

### 2. Apply Migrations
```bash
sqlite3 dialer.db < database_performance_migrations.sql
```

### 3. Verify Indexes
```bash
sqlite3 dialer.db "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_leads_campaign%';"
```
**Expected:** 2 (two new indexes for leads table)

### 4. Integration

Add to `dialer_db_async.py`:

**A. Add import at top:**
```python
import time
```

**B. Add QueryTimer class (before AsyncDialerDB):**
Copy from `dialer_db_async_optimized.py` lines 29-66

**C. Replace methods:**
- `bulk_import_leads()` → Copy from `dialer_db_async_optimized.py` lines 71-173
- `get_next_leads()` → Copy from `dialer_db_async_optimized.py` lines 179-287
- `calculate_drop_rate()` → Copy from `dialer_db_async_optimized.py` lines 293-359

### 5. Test
```bash
python3 test_performance_optimizations.py
```

### 6. Restart
```bash
./stop_production.sh && ./start_production.sh
```

---

## 📊 Expected Results

After deployment:
- ✅ Queries complete in <50ms (was 100-500ms)
- ✅ Bulk imports 100 leads in <100ms (was ~5 seconds)
- ✅ No duplicate lead assignments
- ✅ Slow query warnings appear in logs

---

## 🔍 Quick Validation

### Check indexes:
```bash
sqlite3 dialer.db "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite%' ORDER BY name;"
```

### Test query speed:
```bash
sqlite3 dialer.db "EXPLAIN QUERY PLAN SELECT * FROM leads WHERE campaign_id=1 AND status='NEW' AND attempts<3;"
```

Should see: `SEARCH leads USING INDEX idx_leads_campaign_status_attempts`

---

## ⚠️ Rollback (if needed)

```bash
cd /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/01_Core_System
mv dialer.db dialer.db.failed
cp dialer.db.backup dialer.db
./stop_production.sh && ./start_production.sh
```

---

## 📚 Full Documentation

See `DATABASE_PERFORMANCE_OPTIMIZATION_COMPLETE.md` for:
- Detailed performance benchmarks
- Complete implementation guide
- Monitoring instructions
- Troubleshooting

---

**Status:** Ready for deployment  
**Risk:** Low  
**Time:** 15-30 minutes
