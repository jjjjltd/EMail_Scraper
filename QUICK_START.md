# 🚀 EMAIL SCRAPER - QUICK START GUIDE

## GET RUNNING IN 3 STEPS

### Step 1: Install Flask
```bash
cd email_scraper
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python app.py
```

Browser opens automatically at `http://127.0.0.1:5000`

### Step 3: Test
- **Email:** Your Gmail or Outlook address
- **Password:** 
  - Gmail: Generate App Password at https://myaccount.google.com/apppasswords
  - Outlook: Use your regular password (ensure IMAP enabled)
- **Period:** Start with 1 day

---

## GMAIL APP PASSWORD SETUP (5 minutes)

Gmail requires App Passwords for third-party apps:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already on)
3. Search for "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Name it "Email Scraper"
6. Copy the 16-character password
7. Use this password in Email Scraper (not your regular password)

---

## WHAT TO TEST

### Basic Flow
1. ✅ Login works with your credentials
2. ✅ Analysis completes without errors
3. ✅ Results table shows senders
4. ✅ Sorting works (click column headers)
5. ✅ Selection enables action buttons
6. ✅ Unsubscribe detection shows "Yes" badges

### Edge Cases
1. ⚠️ Empty inbox (try 1 day on Sunday)
2. ⚠️ Wrong password (error message clear?)
3. ⚠️ Large inbox (7 days = slow?)
4. ⚠️ Special characters in sender names

### Performance
1. ⏱️ Time 1-day analysis
2. ⏱️ Time 7-day analysis
3. 📊 Check memory usage
4. 🔄 Progress indicator needed?

---

## EXPECTED BEHAVIOR

**1 day analysis:**
- Should complete in 5-30 seconds (depending on inbox size)
- Shows spinner during analysis
- Results appear immediately when done

**Results table:**
- Default sort: Sender Name (alphabetical)
- All columns sortable (click to toggle ▲/▼)
- Nuisance and Unsubscribe columns have tooltips (ℹ️)

**Action buttons:**
- Disabled (gray) until you select senders
- Show "Phase 2" placeholder when clicked
- Display count of selected senders

**Payment buttons:**
- Show alert: "PayPal coming soon"
- No actual payment processing yet

---

## TROUBLESHOOTING

### "IMAP error: authentication failed"
- **Gmail:** Did you use App Password (not regular password)?
- **Outlook:** Is IMAP enabled in settings?
- **Both:** Check email address is correct

### "Connection error"
- Check internet connection
- Firewall blocking port 993?
- Try different email provider

### App doesn't start
- Python 3.8+ installed?
- Flask installed? (`pip list | grep Flask`)
- Run from email_scraper directory?

### Results are empty
- Check date range (1 day might have no emails)
- Try longer period (5 or 7 days)
- Verify inbox has emails in that period

---

## FIRST TEST CHECKLIST

- [ ] Flask installed successfully
- [ ] App starts and opens browser
- [ ] Privacy notice visible and clear
- [ ] Gmail App Password flow works
- [ ] Analysis completes without error
- [ ] Results table populated
- [ ] Sorting works on all columns
- [ ] Selection enables action buttons
- [ ] Unsubscribe badges show correctly
- [ ] Payment buttons show placeholder alert

**Once this checklist passes → Ready for Phase 2 work!**

---

## NEXT STEPS

After successful MVP testing:

1. **PayPal Integration** - Add real payment processing
2. **Closing Splash** - Value summary on exit
3. **Action Confirmations** - Each action → confirmation screen
4. **Build .exe** - Test PyInstaller bundling
5. **User Testing** - 5-10 real users for feedback

---

## SUPPORT

Questions? Issues? Check:
- `EMAIL_SCRAPER_HANDOVER.md` - Complete documentation
- `README.md` - User-facing guide

---

*Happy testing! 🎉*
