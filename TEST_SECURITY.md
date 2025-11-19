# 🧪 Testing Your Security Implementation

## Quick Test Guide - Is It Working?

---

## ✅ Test 1: Frontend Sends Headers (2 minutes)

### Steps:
1. **Open your app** in browser (production or localhost)
2. **Press F12** to open DevTools
3. Go to **Network** tab
4. **Connect your wallet**
5. **Do any action**: Edit profile, send message, swipe
6. **Click on the API request** in Network tab (e.g., `/api/users/.../profile`)
7. Scroll down to **"Request Headers"** section

### ✅ Success = You see:
```
Request Headers:
  Content-Type: application/json
  X-Wallet-Address: ERjMXMF6AVnMckiQb6zvTEcaCVc7iBpNqmtbNVjeKCpc
```

### ❌ Problem = You DON'T see `X-Wallet-Address`:
- Frontend not deployed yet
- Browser cache issue (hard refresh: Ctrl+Shift+R)
- Check console for errors

---

## ✅ Test 2: Backend Receives Headers (3 minutes)

### Steps:
1. Go to [render.com](https://render.com)
2. Click your backend service
3. Click **"Logs"** tab
4. Perform an action in your app
5. Watch the logs

### ✅ Development Mode (Default):
```
⚠️  Authentication DISABLED - Running in development mode (NOT SECURE FOR PRODUCTION!)
```

**This is NORMAL for testing!** Auth checks are logged but not enforced.

### ✅ Production Mode (After setting REQUIRE_AUTH=true):
```
🔒 Authentication ENABLED - All endpoints require wallet signatures
```

---

## ✅ Test 3: Input Validation Works (5 minutes)

### Test A: Empty Bio (Should Fail)

**Try this in your app:**
1. Open your profile
2. Click Edit
3. **Delete all text** from bio field
4. Click Save

**Expected Result:**
```
❌ Error toast: "Bio cannot be empty"
```

**Backend logs should show:**
```
422 Unprocessable Entity
{"detail": [{"msg": "Bio cannot be empty"}]}
```

---

### Test B: XSS Attempt (Should Fail)

**Try this:**
1. Edit your bio
2. Type: `<script>alert('hack')</script>`
3. Click Save

**Expected Result:**
```
❌ Error toast: "Bio contains invalid content"
```

---

### Test C: Long Message (Should Fail)

**Try this:**
1. Open a chat
2. Paste 6000 characters into message box
3. Try to send

**Expected Result:**
```
❌ Error toast: "Message must be 5000 characters or less"
```

---

## ✅ Test 4: Current Security Status

### Check What Mode You're In:

**Method 1: Check Render Environment Variables**
1. Go to Render → Your Backend Service
2. Click **"Environment"** tab
3. Look for `REQUIRE_AUTH`

**If NOT present or set to `false`:**
- ✅ Development Mode (safe to test)
- ⚠️ Auth logged but not enforced
- ⚠️ NOT secure for production

**If set to `true`:**
- ✅ Production Mode (fully secure)
- ✅ Auth required and enforced
- ✅ Safe for production

---

**Method 2: Check Backend Startup Logs**
1. Render → Logs tab
2. Look at the most recent deployment
3. First few lines show:

```
📁 Using SQLite: smartmoney.db  (or 🐘 Using PostgreSQL)
⚠️  Authentication DISABLED     (or 🔒 Authentication ENABLED)
✅ Database tables initialized
```

---

## ✅ Test 5: End-to-End Security Test

### Current State (Development Mode):

**Try These Actions:**

1. ✅ **Edit Your Own Profile** → Should work
2. ✅ **Send a Message** → Should work
3. ✅ **Swipe on Profiles** → Should work
4. ✅ **View Your Matches** → Should work

**Check Backend Logs:**
- Should see successful 200 OK responses
- May see warnings about wallet checks (this is normal in dev mode)

---

### Future State (Production Mode with REQUIRE_AUTH=true):

**Same Actions:**

1. ✅ **Edit Your Own Profile** → Works (you're authenticated)
2. ✅ **Send a Message** → Works (you're authenticated)
3. ✅ **Swipe on Profiles** → Works (you're authenticated)
4. ✅ **View Your Matches** → Works (you're authenticated)

**Attacker Tries (using curl/Postman):**

```bash
# Try to update someone else's profile
curl -X PUT https://your-api.com/api/users/VICTIM_WALLET/profile \
  -H "Content-Type: application/json" \
  -H "X-Wallet-Address: ATTACKER_WALLET" \
  -d '{"bio": "Hacked!", ...}'

# Expected: ❌ 403 Forbidden - "You can only access your own resources"
```

```bash
# Try without authentication header
curl -X PUT https://your-api.com/api/users/VICTIM_WALLET/profile \
  -H "Content-Type: application/json" \
  -d '{"bio": "Hacked!", ...}'

# Expected: ❌ 401 Unauthorized - "Authentication required"
```

---

## 🎯 Quick Status Check (30 seconds)

### Run This Checklist:

| Check | Status | How to Verify |
|-------|--------|---------------|
| Frontend deployed | ☐ | Visit your Vercel URL |
| Backend deployed | ☐ | Visit https://your-backend.onrender.com (should see API message) |
| Headers being sent | ☐ | DevTools → Network → See `X-Wallet-Address` |
| Input validation working | ☐ | Try empty bio → Should fail |
| PostgreSQL working | ☐ | Backend logs show `🐘 Using PostgreSQL` |
| Auth mode known | ☐ | Check `REQUIRE_AUTH` env var |

---

## 🔧 Common Issues & Solutions

### Issue: "I don't see X-Wallet-Address in headers"

**Solutions:**
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check if frontend deployed successfully
4. Check browser console for errors

---

### Issue: "Input validation not working"

**Symptoms:** Can save empty bio, can save XSS content

**Solutions:**
1. Check backend logs for errors
2. Verify backend is running latest code
3. Try redeploying backend
4. Check Pydantic validators in `main.py`

---

### Issue: "All requests return 401 Unauthorized"

**Cause:** `REQUIRE_AUTH=true` but frontend not sending headers

**Solutions:**
1. Check DevTools → Network → Headers
2. If no `X-Wallet-Address`, redeploy frontend
3. If header exists, check wallet address matches
4. Temporarily set `REQUIRE_AUTH=false` to test

---

### Issue: "Backend logs show warnings but everything works"

**This is NORMAL in development mode!**

Example logs:
```
⚠️  WARNING: Wallet mismatch in dev mode - ABC accessing XYZ
```

This means:
- ✅ Auth checks are running
- ✅ They're being logged
- ⚠️ Not enforced yet (by design)
- ✅ Set `REQUIRE_AUTH=true` when ready to enforce

---

## 🚀 When You're Ready for Production

### Enable Full Authentication:

1. **Set Environment Variable on Render:**
   - Go to your backend service
   - Click "Environment" tab
   - Add or update: `REQUIRE_AUTH` = `true`
   - Click "Save" (will auto-redeploy)

2. **Wait for Deployment** (~2 minutes)

3. **Check Logs:**
   ```
   🔒 Authentication ENABLED - All endpoints require wallet signatures
   ```

4. **Test Your App:**
   - Everything should still work normally
   - But now attackers are blocked!

5. **Monitor Logs for 401/403 Errors:**
   - 401 = Missing auth header (shouldn't happen with your frontend)
   - 403 = Wrong wallet trying to access resources (good! blocking attackers)

---

## 📊 Security Checklist (Before Launch)

### Pre-Launch Security Audit:

- [ ] ✅ Frontend sends `X-Wallet-Address` on all authenticated calls
- [ ] ✅ Input validation prevents empty fields
- [ ] ✅ Input validation prevents XSS
- [ ] ✅ PostgreSQL is being used (not SQLite)
- [ ] ✅ `DATABASE_URL` is set on Render
- [ ] ⚠️ `REQUIRE_AUTH=true` is set (when ready for production)
- [ ] ✅ Backend logs show no errors
- [ ] ✅ All features work in production
- [ ] ✅ Test chat membership (can't read others' chats)
- [ ] ✅ Test profile updates (can't update others' profiles)

---

## 🎉 You're Good If You See:

### Frontend DevTools:
```
✅ X-Wallet-Address: YOUR_WALLET in headers
✅ Status: 200 OK on API calls
✅ No console errors
```

### Backend Logs:
```
✅ 🐘 Using PostgreSQL: sizematters-db...
✅ ⚠️  Authentication DISABLED (or 🔒 ENABLED)
✅ ✅ Database already has X users
✅ 200 OK responses
```

### App Behavior:
```
✅ Can edit own profile
✅ Can't save empty bio
✅ Can't save XSS content
✅ Can send messages in matches
✅ Can swipe on profiles
✅ Data persists after page refresh
```

---

## 🆘 Need Help?

If something's not working:

1. **Check this doc** - Most issues covered above
2. **Check browser console** (F12 → Console tab)
3. **Check Render logs** (Render → Logs tab)
4. **Try development mode** (set `REQUIRE_AUTH=false` temporarily)
5. **Hard refresh browser** (Ctrl+Shift+R)
6. **Redeploy** (frontend and/or backend)

---

## 📝 Testing Script (Copy-Paste)

Run these curl commands to test your production API:

```bash
# Set your variables
BACKEND_URL="https://your-backend.onrender.com"
YOUR_WALLET="YOUR_WALLET_ADDRESS_HERE"

# Test 1: Check API is running
curl $BACKEND_URL
# Expected: {"message": "Smart Money Tinder API", "status": "running"}

# Test 2: Empty bio (should fail)
curl -X PUT $BACKEND_URL/api/users/$YOUR_WALLET/profile \
  -H "Content-Type: application/json" \
  -H "X-Wallet-Address: $YOUR_WALLET" \
  -d '{"bio": "", "country": "US", "favourite_ct_account": "@test", "favourite_trading_venue": "Jupiter", "asset_choice_6m": "SOL"}'
# Expected: 422 Unprocessable Entity

# Test 3: Valid update (should work)
curl -X PUT $BACKEND_URL/api/users/$YOUR_WALLET/profile \
  -H "Content-Type: application/json" \
  -H "X-Wallet-Address: $YOUR_WALLET" \
  -d '{"bio": "Testing!", "country": "US", "favourite_ct_account": "@test", "favourite_trading_venue": "Jupiter", "asset_choice_6m": "SOL"}'
# Expected: 200 OK

# Test 4: Missing auth header (with REQUIRE_AUTH=true, should fail)
curl -X PUT $BACKEND_URL/api/users/$YOUR_WALLET/profile \
  -H "Content-Type: application/json" \
  -d '{"bio": "Testing!", "country": "US", "favourite_ct_account": "@test", "favourite_trading_venue": "Jupiter", "asset_choice_6m": "SOL"}'
# Expected: 401 Unauthorized (only if REQUIRE_AUTH=true)
```

---

**Status:** Ready to test! 🚀

Follow the steps above to verify everything is working correctly.

