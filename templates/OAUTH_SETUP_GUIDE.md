# 🔐 OAUTH SETUP GUIDE - Email Scraper

## Overview

This guide walks you through setting up OAuth 2.0 authentication for Gmail and Outlook. This replaces password-based authentication with modern, frictionless user consent flows.

**Why OAuth?**
- ✅ No passwords needed (users authenticate via Google/Microsoft)
- ✅ Works with passkeys, biometrics, 2FA
- ✅ Secure token-based access
- ✅ User grants explicit permission
- ✅ Tokens can be revoked anytime

**Time Required:**
- Gmail setup: ~20 minutes
- Outlook setup: ~20 minutes
- Total: ~40 minutes (one-time setup)

---

## PART 1: GOOGLE OAUTH (Gmail)

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click project dropdown (top left, next to "Google Cloud")
   - Click "New Project"
   - Project name: `Email Scraper`
   - Organization: Leave as default (or select yours)
   - Location: No organization (or your organization)
   - Click **Create**
   - Wait ~30 seconds for project creation

3. **Select Your Project**
   - Click project dropdown again
   - Select "Email Scraper" project
   - Verify project name shows in top bar

### Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - Hamburger menu (☰) → "APIs & Services" → "Library"
   - Or direct: https://console.cloud.google.com/apis/library

2. **Search for Gmail API**
   - Search box: Type "Gmail API"
   - Click "Gmail API" in results
   - Click blue **Enable** button
   - Wait ~10 seconds for API to enable

3. **Verify Enabled**
   - You'll see "API enabled" message
   - Hamburger menu (☰) → "APIs & Services" → "Enabled APIs & services"
   - "Gmail API" should be listed

### Step 3: Configure OAuth Consent Screen

1. **Navigate to OAuth Consent**
   - Hamburger menu (☰) → "APIs & Services" → "OAuth consent screen"
   - Or direct: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select **External** (allows any Google user)
   - Click **Create**

3. **Fill OAuth Consent Screen (Page 1 of 4)**
   - **App name:** `Email Scraper`
   - **User support email:** Your email address (dropdown)
   - **App logo:** Skip for now (optional)
   - **App domain:** Leave blank for localhost testing
   - **Authorized domains:** Leave blank for now
   - **Developer contact information:** Your email address
   - Click **Save and Continue**

4. **Scopes (Page 2 of 4)**
   - Click **Add or Remove Scopes**
   - Scroll and find: `https://mail.google.com/` (Full Gmail access)
     - Or search: "Gmail API" in filter box
     - Select: `.../auth/gmail.readonly` (Read-only access - SAFER)
   - **Actually, let's use readonly:** Check `https://www.googleapis.com/auth/gmail.readonly`
   - Click **Update**
   - Click **Save and Continue**

5. **Test Users (Page 3 of 4)**
   - Click **Add Users**
   - Add your Gmail address (for testing)
   - Add any other test user emails
   - Click **Add**
   - Click **Save and Continue**

6. **Summary (Page 4 of 4)**
   - Review settings
   - Click **Back to Dashboard**

### Step 4: Create OAuth Credentials

1. **Navigate to Credentials**
   - Hamburger menu (☰) → "APIs & Services" → "Credentials"
   - Or direct: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**
   - Click **+ Create Credentials** (top)
   - Select "OAuth client ID"

3. **Configure Client ID**
   - **Application type:** Web application
   - **Name:** `Email Scraper Desktop`
   - **Authorized JavaScript origins:**
     - Click "+ Add URI"
     - Enter: `http://localhost:5000`
     - Click "+ Add URI" again
     - Enter: `http://127.0.0.1:5000`
   - **Authorized redirect URIs:**
     - Click "+ Add URI"
     - Enter: `http://localhost:5000/oauth/google/callback`
     - Click "+ Add URI" again
     - Enter: `http://127.0.0.1:5000/oauth/google/callback`
   - Click **Create**

4. **Save Your Credentials**
   - Modal appears: "OAuth client created"
   - **IMPORTANT:** Copy and save these securely:
     - **Client ID:** (long string ending in `.apps.googleusercontent.com`)
     - **Client Secret:** (shorter random string)
   - Click **Download JSON** (optional, for backup)
   - Click **OK**

5. **Record Credentials**
   ```
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

### Step 5: Verify Setup

1. **Check Credentials Page**
   - You should see "Email Scraper Desktop" in OAuth 2.0 Client IDs
   - Type: Web application
   - Creation date: Today

2. **Check OAuth Consent**
   - OAuth consent screen shows "Email Scraper"
   - Publishing status: Testing (this is fine for MVP)
   - User type: External

**Gmail OAuth Setup Complete! ✅**

---

## PART 2: MICROSOFT OAUTH (Outlook)

### Step 1: Register Azure Application

1. **Go to Azure Portal**
   - URL: https://portal.azure.com/
   - Sign in with your Microsoft account
   - (If no account: You may need to create a free Azure account)

2. **Navigate to App Registrations**
   - Search bar (top): Type "App registrations"
   - Click "App registrations" in results
   - Or direct: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps

3. **Register New Application**
   - Click **+ New registration**
   - **Name:** `Email Scraper`
   - **Supported account types:** 
     - Select: "Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)"
     - This allows Outlook.com, Hotmail, Live users
   - **Redirect URI:**
     - Platform: Web
     - URI: `http://localhost:5000/oauth/microsoft/callback`
   - Click **Register**

4. **Record Application (client) ID**
   - You'll see "Overview" page
   - Copy and save:
     - **Application (client) ID:** (GUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
     - **Directory (tenant) ID:** (also save this)
   ```
   MICROSOFT_CLIENT_ID=your_application_id_here
   MICROSOFT_TENANT_ID=your_tenant_id_here
   ```

### Step 2: Create Client Secret

1. **Navigate to Certificates & Secrets**
   - Left sidebar: Click "Certificates & secrets"

2. **Create New Secret**
   - Under "Client secrets" tab
   - Click **+ New client secret**
   - **Description:** `Email Scraper Desktop Secret`
   - **Expires:** 24 months (or choose expiration)
   - Click **Add**

3. **IMPORTANT: Save Secret Immediately**
   - Secret appears in list
   - **Value** column shows the secret (only visible NOW)
   - **Copy the Value immediately** (you can't see it again)
   - Save securely:
   ```
   MICROSOFT_CLIENT_SECRET=your_secret_value_here
   ```

### Step 3: Configure API Permissions

1. **Navigate to API Permissions**
   - Left sidebar: Click "API permissions"

2. **Add Permissions**
   - Click **+ Add a permission**
   - Select **Microsoft Graph**
   - Select **Delegated permissions**
   - Search and add these permissions:
     - ✅ `Mail.Read` (Read user mail)
     - ✅ `IMAP.AccessAsUser.All` (Access mailboxes via IMAP)
     - ✅ `offline_access` (Maintain access to data)
     - ✅ `openid` (Sign in and read profile)
     - ✅ `email` (View email address)
     - ✅ `profile` (View basic profile)
   - Click **Add permissions**

3. **Review Permissions**
   - You should see all 6 permissions listed
   - Status: "Not granted for Default Directory"
   - Click **Grant admin consent for Default Directory** (if you're admin)
   - Or: Users will consent individually (fine for MVP)

### Step 4: Configure Authentication

1. **Navigate to Authentication**
   - Left sidebar: Click "Authentication"

2. **Verify Redirect URI**
   - Under "Web" platform:
   - Should see: `http://localhost:5000/oauth/microsoft/callback`
   - If not, click **+ Add URI** and add it

3. **Add Additional Redirect URI**
   - Click **+ Add URI**
   - Enter: `http://127.0.0.1:5000/oauth/microsoft/callback`
   - Click **Save** (bottom of page)

4. **Configure Implicit Grant** (Optional, for some flows)
   - Under "Implicit grant and hybrid flows"
   - Check: ✅ **ID tokens** (used for sign-in)
   - Leave "Access tokens" unchecked (we use authorization code flow)
   - Click **Save**

### Step 5: Verify Setup

1. **Check Overview**
   - Application (client) ID: ✅ Recorded
   - Directory (tenant) ID: ✅ Recorded
   - Client secret: ✅ Created and recorded

2. **Check API Permissions**
   - 6 permissions listed
   - All show "Delegated" type

3. **Check Authentication**
   - 2 redirect URIs listed (localhost + 127.0.0.1)
   - ID tokens enabled

**Microsoft OAuth Setup Complete! ✅**

---

## PART 3: RECORD ALL CREDENTIALS

Create a secure file (DO NOT commit to git) with all credentials:

### Create `.env` file (local only)

```bash
# Gmail OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth Credentials
MICROSOFT_CLIENT_ID=your_microsoft_application_id
MICROSOFT_TENANT_ID=your_microsoft_tenant_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Flask Settings
FLASK_SECRET_KEY=generate_a_random_string_here_at_least_32_chars
```

### Generate Flask Secret Key

Run this in Python:
```python
import secrets
print(secrets.token_hex(32))
```

Copy output to `FLASK_SECRET_KEY` in `.env` file.

### Add `.env` to `.gitignore`

Create/update `.gitignore`:
```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
venv313/
dist/
build/
*.egg-info/
.DS_Store
```

---

## PART 4: TESTING OAUTH SETUP

### Test Google OAuth

1. **Test Credentials URL**
   - Go to: https://developers.google.com/oauthplayground/
   - Click settings gear (⚙️) top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret
   - Select "Gmail API v1" → `https://www.googleapis.com/auth/gmail.readonly`
   - Click "Authorize APIs"
   - Sign in and grant permission
   - If successful: You'll get an authorization code ✅

### Test Microsoft OAuth

1. **Test Credentials**
   - Go to: https://developer.microsoft.com/en-us/graph/graph-explorer
   - Click "Sign in to Graph Explorer"
   - Sign in with your Microsoft account
   - Try sample query: "Get my messages"
   - If successful: You'll see your emails ✅

---

## PART 5: SECURITY BEST PRACTICES

### Protect Your Credentials

1. **Never commit `.env` to git**
   - Add to `.gitignore` immediately
   - Verify: `git status` should NOT show `.env`

2. **Store securely**
   - Use password manager for production credentials
   - Create separate credentials for dev/staging/production
   - Rotate secrets every 6-12 months

3. **Localhost only for now**
   - Current setup only works on localhost
   - For production deployment, you'll need:
     - HTTPS domain
     - Update redirect URIs
     - Update authorized origins

### Scope Minimization

- ✅ Gmail: `gmail.readonly` (not full access)
- ✅ Outlook: `Mail.Read` (not Mail.ReadWrite)
- We read only, never modify emails
- Users see this in consent screen

### Token Storage

- Tokens stored in memory only (like passwords)
- Never written to disk
- Discarded when app closes
- User must re-authorize each session (acceptable for MVP)

---

## PART 6: TROUBLESHOOTING

### Google OAuth Issues

**Error: "redirect_uri_mismatch"**
- Check redirect URI exactly matches: `http://localhost:5000/oauth/google/callback`
- No trailing slash
- No https (localhost uses http)
- Check both localhost AND 127.0.0.1 variants added

**Error: "access_denied"**
- User denied permission (expected behavior)
- Check user is in "Test users" list (if app not published)
- Check scopes requested match scopes configured

**Error: "invalid_client"**
- Client ID or Secret incorrect
- Check .env file has correct values
- Check no extra spaces/quotes

### Microsoft OAuth Issues

**Error: "AADSTS50011: redirect_uri_mismatch"**
- Check redirect URI exactly matches: `http://localhost:5000/oauth/microsoft/callback`
- Verify in Azure Portal → Authentication section

**Error: "AADSTS65001: consent_required"**
- User hasn't consented to permissions
- Normal for first auth
- Click "Accept" on consent screen

**Error: "invalid_client"**
- Client ID or Secret incorrect
- Secret may have expired (check expiration date)
- Generate new secret if needed

### General Issues

**Browser doesn't open**
- Check Flask running on port 5000
- Try manual: http://localhost:5000

**Localhost vs 127.0.0.1**
- Some systems treat these differently
- Add BOTH to authorized URIs (we did this)

**Firewall blocking**
- Check port 5000 not blocked
- Try disabling firewall temporarily for testing

---

## PART 7: NEXT STEPS

### After Credentials Created

1. ✅ Verify all 5 credentials saved in `.env`
2. ✅ Verify `.env` in `.gitignore`
3. ✅ Test OAuth playground (optional but recommended)
4. 🔄 Return to Claude for code implementation
5. 🔄 Test OAuth flow in Email Scraper
6. 🔄 Iterate based on user testing

### For Production Deployment

When ready to launch publicly:

**Google:**
1. Publish OAuth consent screen
2. Submit for verification (if >100 users)
3. Add production domain to authorized origins
4. Update redirect URIs to HTTPS

**Microsoft:**
1. Change app to "single tenant" if desired
2. Add production redirect URIs
3. Consider admin consent for org users
4. Rotate secrets before launch

---

## SUMMARY CHECKLIST

### Google OAuth Setup
- [ ] Created Google Cloud Project
- [ ] Enabled Gmail API
- [ ] Configured OAuth consent screen
- [ ] Created OAuth client ID
- [ ] Saved Client ID and Secret
- [ ] Added to `.env` file

### Microsoft OAuth Setup
- [ ] Registered Azure application
- [ ] Saved Application (client) ID and Tenant ID
- [ ] Created client secret
- [ ] Saved secret value
- [ ] Configured API permissions (6 permissions)
- [ ] Configured redirect URIs (2 URIs)
- [ ] Added to `.env` file

### Security
- [ ] Created `.env` file
- [ ] Generated Flask secret key
- [ ] Added `.env` to `.gitignore`
- [ ] Verified `.env` not tracked by git

### Ready for Development
- [ ] All credentials in `.env`
- [ ] OAuth playgrounds tested (optional)
- [ ] Ready to implement OAuth in Email Scraper

---

## APPENDIX: CREDENTIAL TEMPLATE

Copy this template to your `.env` file and fill in your values:

```bash
# ===========================================
# EMAIL SCRAPER - OAUTH CREDENTIALS
# ===========================================
# ⚠️  NEVER COMMIT THIS FILE TO GIT
# ===========================================

# Google OAuth (Gmail)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Microsoft OAuth (Outlook/Hotmail/Live)
MICROSOFT_CLIENT_ID=
MICROSOFT_TENANT_ID=
MICROSOFT_CLIENT_SECRET=

# Flask Application
FLASK_SECRET_KEY=

# ===========================================
# NOTES:
# - Get Google credentials: https://console.cloud.google.com/apis/credentials
# - Get Microsoft credentials: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps
# - Generate Flask key: python -c "import secrets; print(secrets.token_hex(32))"
# ===========================================
```

---

**Document Version: 1.0**  
**Last Updated: November 2025**  
**Status: OAuth Setup Guide Complete**

**Next Step:** Implement OAuth flow in `app.py` 🔄
