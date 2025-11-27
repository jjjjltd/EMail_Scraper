# 🧪 OAUTH TESTING GUIDE

## ✅ YOU'RE READY TO TEST!

OAuth implementation is complete. Here's how to test it.

---

## STEP 1: VERIFY YOUR SETUP

Check that you have:
- ✅ `.env` file with all 6 credentials filled in
- ✅ `.gitignore` includes `.env`
- ✅ OAuth credentials from Google and Microsoft

---

## STEP 2: INSTALL DEPENDENCIES

```bash
cd email_scraper
pip install -r requirements.txt
```

New dependencies:
- `authlib` - OAuth library
- `python-dotenv` - Environment variable loading
- `requests` - HTTP client (for OAuth)

---

## STEP 3: RUN THE APP

```bash
python app.py
```

You should see:
```
🔍 Email Scraper starting...
📧 Privacy-first inbox analysis with OAuth
🌐 Opening browser at http://127.0.0.1:5000
```

Browser opens automatically.

---

## STEP 4: TEST GMAIL OAUTH

1. **Home page loads** - You see:
   - "Connect with Gmail" button (blue)
   - "Connect with Outlook" button (light blue)
   - Date range selector (1 day / 7 days)

2. **Click "Connect with Gmail"**
   - Redirects to Google login page
   - URL shows `accounts.google.com`
   - **THIS IS GOOGLE'S PAGE** (not ours - that's the point!)

3. **Sign in with Google**
   - Use your password, passkey, or biometric
   - Google shows consent screen:
     - "Email Scraper wants to..."
     - "Read your Gmail messages"
   - Click "Allow"

4. **Redirected back to app**
   - Shows "Analyzing..." spinner
   - Shows your email address
   - Shows period (1 or 7 days)

5. **Analysis completes**
   - Results page loads
   - Shows table of senders
   - Shows metrics (count, size, nuisance, etc.)
   - Action buttons appear (disabled until selection)

---

## STEP 5: TEST OUTLOOK OAUTH

Same flow as Gmail:

1. **Click "Connect with Outlook"**
2. **Microsoft login page** (login.microsoftonline.com)
3. **Sign in** with Microsoft account
4. **Consent screen** - Click "Accept"
5. **Analyzing...** spinner
6. **Results** page

---

## EXPECTED BEHAVIOR

### ✅ Success Signs

- No password fields (just OAuth buttons)
- Redirects to Google/Microsoft (not our app)
- Consent screen shows "Email Scraper"
- Analysis completes without errors
- Results table populated
- Sorting works
- Selection enables action buttons

### ⚠️ Common Issues

**"redirect_uri_mismatch"**
- Check OAuth callback URLs match exactly:
  - `http://localhost:5000/oauth/google/callback`
  - `http://localhost:5000/oauth/microsoft/callback`
- No trailing slashes
- No `https` (localhost uses http)

**"invalid_client"**
- Check `.env` credentials are correct
- No extra spaces or quotes
- Client ID and Secret copied fully

**"IMAP error"**
- OAuth token received but IMAP auth failed
- Check scopes in OAuth setup:
  - Gmail: `gmail.readonly`
  - Outlook: `IMAP.AccessAsUser.All` + `Mail.Read`

**"Authentication failed"**
- User denied consent (clicked "Cancel")
- This is expected - ask user to try again

---

## STEP 6: VERIFY FUNCTIONALITY

Test these features:

### Results Table
- [ ] All columns display correctly
- [ ] Sender names, organizations, counts
- [ ] Sizes formatted (KB or MB)
- [ ] Dates formatted properly
- [ ] Read/Unread counts
- [ ] % Unread calculated
- [ ] Nuisance scores present
- [ ] Unsubscribe badges (Yes/No)

### Selection
- [ ] Individual checkboxes work
- [ ] "Select All" checkbox works
- [ ] Action buttons enable when selected
- [ ] Action buttons show "Phase 2" alerts

### Actions (Phase 2 Placeholders)
- [ ] Unsubscribe - Shows alert
- [ ] Create Folder - Shows alert
- [ ] Manage History - Shows alert
- [ ] Delete All - Shows alert
- [ ] Archive - Shows alert

### Payment (Phase 2 Placeholder)
- [ ] "Pay for Service" - Shows alert
- [ ] "Do Not Pay" - Shows alert

### Navigation
- [ ] "New Analysis" button returns to home
- [ ] Can run analysis again with different provider
- [ ] Can change date range

---

## STEP 7: TEST EDGE CASES

### Empty Inbox
- Select date range with no emails (e.g., 1 day on Sunday)
- Should complete without error
- Shows "0 emails from 0 senders"
- Table empty but page renders

### Large Inbox
- Try 7 days on a busy inbox
- Should respect MAX_EMAILS limit (5000)
- Shows warning if limited
- Completes within MAX_TIME_SECONDS (300 = 5 min)

### Test Mode
- Set `TEST_MODE=true` in `.env`
- Restart app
- Should show "TEST MODE: Read-only" badge
- Analysis runs normally
- No side effects (technically, but cosmetic for now)

---

## TROUBLESHOOTING

### OAuth Flow Breaks

**Check Flask logs:**
```bash
python app.py
# Watch console for errors
```

**Common errors:**
- `KeyError: 'access_token'` - OAuth didn't complete
- `IMAP4.error` - Check scopes/permissions
- `redirect_uri_mismatch` - Check callback URLs

### Analysis Hangs

- Check console - may be processing large inbox
- Wait up to 5 minutes (MAX_TIME_SECONDS)
- Check for timeout errors in logs

### Results Don't Load

- Check browser console (F12)
- Look for JavaScript errors
- Check network tab for failed requests

---

## SUCCESS CRITERIA

You've succeeded when:

✅ Gmail OAuth works (no password needed)
✅ Outlook OAuth works (no password needed)
✅ Analysis completes for both providers
✅ Results display correctly
✅ Selection and actions work (even if placeholder)
✅ No errors in console

---

## NEXT STEPS AFTER TESTING

Once OAuth works:

1. **Commit to git** (develop branch)
   ```bash
   git add .
   git commit -m "feat: OAuth implementation complete"
   git push origin develop
   ```

2. **Create PR** to merge to main

3. **Document any issues** found during testing

4. **Plan Phase 2:**
   - PayPal integration
   - Action implementations
   - Progress indicators
   - Resource monitoring

---

## GETTING HELP

If stuck:

1. Check OAUTH_SETUP_GUIDE.md
2. Check Google/Azure portal settings
3. Verify `.env` credentials
4. Check Flask console logs
5. Share error message for troubleshooting

---

**Happy testing! 🚀**

*Remember: No passwords needed anymore. That's the whole point!*
