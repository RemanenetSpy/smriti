# ============================================================
# Smriti × Supabase — End-to-End Test Script
# ============================================================
# Fill in your credentials below, then run this entire file
# in PowerShell. Nothing is sent anywhere except to Smriti API.
# ============================================================

# --- FILL THESE IN ---
$SMRITI_API_KEY   = "chrn_YOUR_KEY_HERE"          # From smriti-kaal.vercel.app → Dashboard
$SUPABASE_DB_URL  = "postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres"
# ----------------------
# Use the SESSION POOLER URL (not the direct connection URL).
# In Supabase dashboard: Project Settings → Database → Connection Pooling
# Set Pool mode = Session, then copy the connection string shown there.
#
# ⚠️  The direct URL (db.xxxx.supabase.co) will FAIL on cloud hosts (HF Spaces, Railway, Render).
#     The Session Pooler URL works everywhere.


$API_BASE = "https://spy9191-chronos-api-backend.hf.space"
$HEADERS_DEFAULT  = @{ "X-API-Key" = $SMRITI_API_KEY; "Content-Type" = "application/json" }
$HEADERS_SUPABASE = @{ "X-API-Key" = $SMRITI_API_KEY; "Content-Type" = "application/json"; "X-Supabase-Url" = $SUPABASE_DB_URL }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SMRITI × SUPABASE — INTEGRATION TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# ------------------------------------------------------------
# TEST 1: Health check (no API key needed)
# ------------------------------------------------------------
Write-Host ""
Write-Host "[ TEST 1 ] Health check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$API_BASE/health" -Method GET -UseBasicParsing
Write-Host "  ✅ Status: $($health.status)" -ForegroundColor Green
Write-Host "  ✅ Events in Smriti DB: $($health.stores.postgres_events)"
Write-Host "  ✅ Vectors: $($health.stores.pgvector_embeddings)"

# ------------------------------------------------------------
# TEST 2: Ingest to DEFAULT Smriti DB (no Supabase header)
# ------------------------------------------------------------
Write-Host ""
Write-Host "[ TEST 2 ] Ingest to DEFAULT Smriti DB (no Supabase header)..." -ForegroundColor Yellow
$body = '{"source_id":"terminal-test","events":[{"text":"Reman tested the Smriti default storage today"}]}'
$ingest1 = Invoke-RestMethod -Uri "$API_BASE/ingest" -Method POST -Headers $HEADERS_DEFAULT -Body $body -UseBasicParsing
Write-Host "  ✅ Ingested: $($ingest1.ingested_count) event(s)" -ForegroundColor Green
Write-Host "  ✅ Event IDs: $($ingest1.event_ids)"
Write-Host "  ✅ SVO: $($ingest1.svo_tuples | ConvertTo-Json -Compress)"

# ------------------------------------------------------------
# TEST 3: Ingest to YOUR SUPABASE DB (with X-Supabase-Url)
# ------------------------------------------------------------
Write-Host ""
Write-Host "[ TEST 3 ] Ingest to YOUR SUPABASE DB..." -ForegroundColor Yellow
$body2 = '{"source_id":"supabase-test","events":[{"text":"Alice joined the engineering team on Monday"}]}'
try {
    $ingest2 = Invoke-RestMethod -Uri "$API_BASE/ingest" -Method POST -Headers $HEADERS_SUPABASE -Body $body2 -UseBasicParsing
    Write-Host "  ✅ Ingested to Supabase: $($ingest2.ingested_count) event(s)" -ForegroundColor Green
    Write-Host "  ✅ Event IDs: $($ingest2.event_ids)"
    Write-Host "  ✅ SVO extracted: $($ingest2.svo_tuples | ConvertTo-Json -Compress)"
    $supabaseEventId = $ingest2.event_ids[0]
} catch {
    Write-Host "  ❌ Supabase ingest failed: $_" -ForegroundColor Red
    Write-Host "     → Did you run the migration SQL in Supabase SQL Editor?" -ForegroundColor DarkYellow
    Write-Host "     → Is the password correct in SUPABASE_DB_URL?" -ForegroundColor DarkYellow
    exit 1
}

# ------------------------------------------------------------
# TEST 4: Query from YOUR SUPABASE DB
# ------------------------------------------------------------
Write-Host ""
Write-Host "[ TEST 4 ] Query from YOUR SUPABASE DB..." -ForegroundColor Yellow
$qbody = '{"query":"Who joined the team?","max_results":5}'
try {
    $query = Invoke-RestMethod -Uri "$API_BASE/query" -Method POST -Headers $HEADERS_SUPABASE -Body $qbody -UseBasicParsing
    Write-Host "  ✅ Results returned: $($query.results.Count)" -ForegroundColor Green
    foreach ($r in $query.results) {
        Write-Host "     → [$($r.subject)] [$($r.verb)] [$($r.object)]"
    }
} catch {
    Write-Host "  ❌ Supabase query failed: $_" -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------
# TEST 5: Confirm DEFAULT path still untouched
# ------------------------------------------------------------
Write-Host ""
Write-Host "[ TEST 5 ] Query from DEFAULT Smriti DB (no Supabase header)..." -ForegroundColor Yellow
$qbody2 = '{"query":"Reman tested storage","max_results":3}'
$query2 = Invoke-RestMethod -Uri "$API_BASE/query" -Method POST -Headers $HEADERS_DEFAULT -Body $qbody2 -UseBasicParsing
Write-Host "  ✅ Default DB results: $($query2.results.Count)" -ForegroundColor Green

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ALL TESTS PASSED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Now open Supabase → Table Editor → events" -ForegroundColor White
Write-Host "  You should see 1 row with Alice's memory stored there." -ForegroundColor White
Write-Host ""
Write-Host "  To eject: just remove X-Supabase-Url from your requests." -ForegroundColor DarkGray
Write-Host ""
