# Backend Restart Instructions

## 🚨 You're seeing 422/500 errors because the backend needs to restart with the new code!

## Quick Restart

```bash
# Stop your current backend (press Ctrl+C in the terminal where it's running)

# Then restart using the automated script:
./restart-backend.sh
```

## What This Does

1. ✅ Kills any existing Python backend processes
2. ✅ Frees up port 8765
3. ✅ Activates the virtual environment
4. ✅ Starts backend with error logging to `backend_errors.log`

## If You See Errors

The error messages will be saved to `backend_errors.log` - you can check this file to see what went wrong.

## What's Been Fixed

Your latest code includes:
- ✅ Fixed 422 validation errors (type casting)
- ✅ Fixed budget validation
- ✅ Simplified precious metals
- ✅ Auto profit/loss calculation
- ✅ Database delete methods

**All committed and pushed to:** `claude/cross-platform-setup-scripts-JY0Hx`

## After Restart

Test these endpoints - they should all work:
- ✅ GET /api/expenses/summary (was 422, now fixed!)
- ✅ GET /api/expenses/by-category (was 422, now fixed!)
- ✅ POST /api/expenses (was 500, should work now)
- ✅ PATCH /api/precious-metals/accounts/{id}/current-value (NEW!)
- ✅ POST /api/precious-metals/transactions/simple (NEW!)

## If Problems Persist

Check `backend_errors.log` and let me know what error you see!
