# 🚨 SECURITY INCIDENT - November 16, 2025

## What Happened
API keys and secrets were accidentally committed to git history in the `.env` file across multiple commits (commits fd38a2e, a7db43d, 781b9e1, and others from Nov 9-12, 2025).

## Exposed Credentials
- ✅ OpenAI API Key: `sk-proj-Hrwtm95QfWFt64QEblAo...` 
- ✅ Supabase URL: `https://wwozrhpoxxouedougetm.supabase.co`
- ✅ Supabase Service Role Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- ✅ Database Password: `i*VHAs*)4s2iZvT`

## Actions Taken (Nov 16, 2025)
1. ✅ Removed `.env` from entire git history using `git filter-branch`
2. ✅ Created `.env.example` template file
3. ⏳ **CRITICAL: Must force push to GitHub** (see below)

## Required Immediate Actions

### 1. Rotate ALL Credentials (DO THIS FIRST!)

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Find and revoke the key starting with `sk-proj-Hrwtm95QfWFt64QEblAo`
3. Create a new API key
4. Update `.env` locally with new key
5. Check usage history for unauthorized charges

**Supabase:**
1. Go to Supabase Dashboard → Project Settings → API
2. Click "Reset service_role secret" 
3. Confirm the reset
4. Copy new service_role key to `.env` locally
5. Check Database logs for suspicious activity (Settings → Logs)

**Database Password:**
1. Go to Supabase Dashboard → Project Settings → Database
2. Click "Reset Database Password"
3. Update `.env` locally with new password

### 2. Force Push to GitHub (AFTER rotating keys above!)

```powershell
# WARNING: This will rewrite GitHub history. Coordinate with team first!
git push origin --force --all
git push origin --force --tags
```

### 3. Update Render Deployment

After rotating keys, update environment variables in Render:
1. Go to Render Dashboard → Your Service → Environment
2. Update `OPENAI_API_KEY` with new key
3. Update `SUPABASE_SERVICE_KEY` with new key
4. Update `DB_PASSWORD` if applicable
5. Redeploy service

### 4. Verify Security

**Check for unauthorized usage:**
- OpenAI Usage: https://platform.openai.com/usage
- Supabase Activity: Dashboard → Logs → Database / API logs
- GitHub: Check repo for unauthorized forks/clones (Settings → Insights → Traffic)

**Monitor for next 7 days:**
- Watch OpenAI usage for spikes
- Monitor Supabase database access logs
- Check Render deployment logs

## Prevention Measures

### Already Implemented:
- ✅ `.gitignore` includes `.env`, `*.env`
- ✅ `.env.example` template created (safe to commit)

### Best Practices Going Forward:
1. **Never commit secrets** - Always use `.env` files excluded by `.gitignore`
2. **Use secret scanning** - Enable GitHub secret scanning (Settings → Security → Secret scanning)
3. **Rotate regularly** - Change API keys every 90 days
4. **Limit permissions** - Use least-privilege keys (e.g., Supabase anon key for frontend)
5. **Environment-specific keys** - Use different keys for dev/staging/production

## Timeline

| Date | Event |
|------|-------|
| Nov 9, 2025 | `.env` first committed (commit 781b9e1) |
| Nov 11, 2025 | `.env` updated (commit a7db43d) |
| Nov 12, 2025 | `.env` updated (commit fd38a2e) |
| Nov 16, 2025 | **Security breach discovered** |
| Nov 16, 2025 | `.env` removed from git history |
| **PENDING** | **Force push to GitHub** |
| **PENDING** | **Rotate all credentials** |

## Notes

- The `.env` file was publicly visible on GitHub at `https://github.com/rawleyc/MatchColab`
- Anyone who cloned the repo before the force push still has the old keys in their local history
- Git history is immutable - even after force push, old commits may exist in GitHub's cache for ~24 hours
- **Credential rotation is mandatory** - history cleanup alone is insufficient

## Contact

If you discover unauthorized usage:
- OpenAI Support: https://help.openai.com/
- Supabase Support: https://supabase.com/support
- GitHub Security: security@github.com

---

**Status: ⚠️ INCOMPLETE - Keys not yet rotated, changes not yet pushed**
