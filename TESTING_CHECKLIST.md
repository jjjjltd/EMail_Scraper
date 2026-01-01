# 🧪 EMAIL SCRAPER - TESTING CHECKLIST

## PRE-TEST SETUP

### Environment
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Flask installed (`pip install -r requirements.txt`)
- [ ] Internet connection active
- [ ] Test email accounts ready (Gmail + Outlook)

### Gmail Setup
- [ ] 2-Step Verification enabled
- [ ] App Password generated
- [ ] App Password saved securely
- [ ] Know inbox has emails in last 7 days

### Outlook Setup
- [ ] IMAP enabled in settings
- [ ] Know regular password
- [ ] Know inbox has emails in last 7 days

---

## FUNCTIONAL TESTING

### 1. Application Startup
- [ ] App starts without errors (`python app.py`)
- [ ] Browser opens automatically
- [ ] URL is http://127.0.0.1:5000
- [ ] Page loads completely
- [ ] No console errors (F12 Developer Tools)

### 2. UI Elements Present
- [ ] Header with title "Email Scraper"
- [ ] Privacy notice section visible
- [ ] Email input field present
- [ ] Password input field present
- [ ] Days dropdown present (1/5/7 options)
- [ ] "Analyze My Inbox" button visible
- [ ] Button enabled (not grayed out)

### 3. Privacy Notice Content
- [ ] "Your Privacy Matters" heading
- [ ] Lists what data we need
- [ ] States credentials never stored
- [ ] States emails never transmitted
- [ ] States "no data mining"
- [ ] Clear and reassuring tone

### 4. Form Validation
- [ ] Empty email → Shows error message
- [ ] Empty password → Shows error message
- [ ] Invalid email format → Appropriate error
- [ ] Error message red/prominent
- [ ] Error clears on retry

### 5. Gmail Authentication (App Password)
- [ ] Enter Gmail address
- [ ] Enter App Password (16 chars)
- [ ] Select 1 day period
- [ ] Click Analyze
- [ ] Login form hides
- [ ] Spinner appears
- [ ] "Analyzing..." message shows
- [ ] No error message appears
- [ ] Connection successful

### 6. Outlook Authentication
- [ ] Enter Outlook address
- [ ] Enter regular password
- [ ] Select 1 day period
- [ ] Click Analyze
- [ ] Login form hides
- [ ] Spinner appears
- [ ] Connection successful

### 7. Analysis Process (1 Day)
- [ ] Spinner animates smoothly
- [ ] "Analyzing..." text visible
- [ ] Takes reasonable time (< 60 seconds)
- [ ] No browser freezing
- [ ] Completes without error

### 8. Analysis Process (7 Days)
- [ ] Same as 1 day test
- [ ] Takes longer (expected)
- [ ] Still completes within 5 minutes
- [ ] No timeout errors

### 9. Results Display
- [ ] Results section appears
- [ ] Login/analyzing sections hidden
- [ ] Results header shows:
  - [ ] Total emails count
  - [ ] Total senders count
  - [ ] Days analyzed (matches selection)
- [ ] Action toolbar visible
- [ ] Results table visible
- [ ] Payment section visible

### 10. Results Table - Headers
- [ ] Checkbox column (with "select all")
- [ ] Sender Name column
- [ ] Organization column
- [ ] Count column
- [ ] Size column
- [ ] Last Received column
- [ ] Read/Unread column
- [ ] % Unread column
- [ ] Nuisance column (with ℹ️ tooltip)
- [ ] Unsubscribe? column (with ℹ️ tooltip)

### 11. Results Table - Data
- [ ] Rows populated with senders
- [ ] Sender names display correctly
- [ ] Organizations extracted from domains
- [ ] Counts are accurate (spot check)
- [ ] Sizes formatted (KB or MB)
- [ ] Dates formatted (YYYY-MM-DD HH:MM)
- [ ] Read/Unread shows "X / Y"
- [ ] % Unread calculated correctly
- [ ] Nuisance scores present
- [ ] Unsubscribe badges show Yes/No

### 12. Tooltips
- [ ] Hover over Nuisance ℹ️ shows tooltip
- [ ] Tooltip text: "Score based on unread%, count, and size"
- [ ] Hover over Unsubscribe? ℹ️ shows tooltip
- [ ] Tooltip text: "Unsubscribe link detected in email"
- [ ] Tooltips dismiss on mouse leave

### 13. Sorting Functionality
- [ ] Click Sender Name → Table sorts alphabetically
- [ ] Click again → Reverses sort (Z to A)
- [ ] Sort indicator (▲/▼) updates
- [ ] Click Organization → Sorts by org
- [ ] Click Count → Sorts by count (numerical)
- [ ] Click Size → Sorts by size (numerical)
- [ ] Click Last Received → Sorts by date
- [ ] Click % Unread → Sorts by percentage
- [ ] Click Nuisance → Sorts by score
- [ ] Default sort is Sender Name (ascending)

### 14. Selection - Individual
- [ ] Click checkbox for one sender
- [ ] Checkbox becomes checked
- [ ] Action buttons enable (no longer gray)
- [ ] Click checkbox again
- [ ] Checkbox unchecks
- [ ] If no selections, buttons disable again

### 15. Selection - Select All
- [ ] Click "select all" checkbox in header
- [ ] All sender checkboxes become checked
- [ ] Action buttons enable
- [ ] Click "select all" again
- [ ] All sender checkboxes uncheck
- [ ] Action buttons disable

### 16. Action Toolbar - Unsubscribe
- [ ] Button shows 🚫 icon
- [ ] Button text: "Unsubscribe"
- [ ] Disabled when nothing selected (gray)
- [ ] Enabled when sender(s) selected
- [ ] Click when enabled
- [ ] Modal opens
- [ ] Modal title: "Unsubscribe"
- [ ] Modal body: "Feature coming in Phase 2!"
- [ ] Shows count of selected senders
- [ ] Close button (×) works
- [ ] Click outside modal closes it

### 17. Action Toolbar - Other Actions
Test same flow for each:
- [ ] 📁 Create Folder
- [ ] 🗃️ Clean-up History
- [ ] 🗑️ Delete All
- [ ] 📦 Archive

### 18. Payment Section
- [ ] Section visible below results
- [ ] Title: "Found This Useful?"
- [ ] Value message present
- [ ] Two buttons visible:
  - [ ] "Pay for Service" (larger, green)
  - [ ] "Do Not Pay" (smaller, gray)
- [ ] Click "Pay for Service"
- [ ] Alert: "PayPal integration coming soon!"
- [ ] Click "Do Not Pay"
- [ ] Alert: "Thank you for trying Email Scraper!"

### 19. Keyboard Navigation
- [ ] Tab through form fields works
- [ ] Enter in email field → Focus password
- [ ] Enter in password field → Starts analysis
- [ ] Tab through table works
- [ ] Spacebar toggles checkboxes

### 20. Browser Compatibility
Test in each browser:
- [ ] Chrome - All features work
- [ ] Firefox - All features work
- [ ] Edge - All features work
- [ ] Safari (if Mac available) - All features work

---

## EDGE CASE TESTING

### 21. Empty Results
- [ ] Select period with no emails
- [ ] Analysis completes
- [ ] Results section shows
- [ ] Table is empty (or "No senders found" message)
- [ ] Action buttons stay disabled
- [ ] Payment section still shows
- [ ] No JavaScript errors

### 22. Single Email
- [ ] Period with only 1 email
- [ ] Results show 1 sender
- [ ] Metrics calculated correctly
- [ ] All functionality works normally

### 23. Large Inbox (if available)
- [ ] Inbox with 5,000+ emails
- [ ] 7-day analysis
- [ ] Completes (may take 2-5 minutes)
- [ ] Results display properly
- [ ] Sorting performance acceptable
- [ ] No browser crashes

### 24. Special Characters
- [ ] Sender with emoji in name
- [ ] Sender with accented characters (é, ñ, etc.)
- [ ] Sender with quotes or apostrophes
- [ ] Display handles correctly
- [ ] No encoding errors

### 25. Wrong Credentials
- [ ] Wrong email format → Clear error
- [ ] Wrong password → "Authentication failed" error
- [ ] Error message helpful
- [ ] Can retry without refresh
- [ ] Form reappears correctly

### 26. Connection Issues
- [ ] Disconnect internet during analysis
- [ ] Error message appears: "Connection error"
- [ ] Can retry when reconnected
- [ ] No app crash

### 27. IMAP Timeout
- [ ] Very slow connection
- [ ] Takes > 60 seconds
- [ ] Check if timeout handled gracefully
- [ ] Error message if timeout occurs

### 28. Unsubscribe Detection Accuracy
- [ ] Manually check 5 senders with "Yes" badge
- [ ] Verify they actually have unsubscribe links
- [ ] Check 5 senders with "No" badge
- [ ] Verify accuracy (spot check acceptable)

---

## PERFORMANCE TESTING

### 29. Analysis Speed
Measure and record:
- [ ] 1 day, small inbox (<100 emails): ___ seconds
- [ ] 1 day, medium inbox (100-1000 emails): ___ seconds
- [ ] 1 day, large inbox (1000+ emails): ___ seconds
- [ ] 7 days, small inbox: ___ seconds
- [ ] 7 days, medium inbox: ___ seconds
- [ ] 7 days, large inbox: ___ seconds

Acceptable benchmarks:
- Small: < 10 seconds
- Medium: < 30 seconds
- Large: < 120 seconds

### 30. Memory Usage
- [ ] Check browser memory (Task Manager)
- [ ] Before analysis: ___ MB
- [ ] During analysis: ___ MB
- [ ] After analysis: ___ MB
- [ ] No memory leaks (stays stable)

### 31. UI Responsiveness
- [ ] Table rendering fast (< 1 second)
- [ ] Sorting instant (< 0.5 seconds)
- [ ] Checkbox selection instant
- [ ] No lag when clicking actions
- [ ] Smooth scrolling on large tables

---

## SECURITY TESTING

### 32. Credential Handling
- [ ] Check browser dev tools → Network tab
- [ ] Credentials sent via POST (not GET)
- [ ] HTTPS not required (localhost)
- [ ] Password not visible in URL
- [ ] Password field type="password"

### 33. Data Storage
- [ ] Check browser localStorage → Should be empty
- [ ] Check browser sessionStorage → Should be empty
- [ ] Check browser cookies → Should be minimal/none
- [ ] Refresh page → Must re-login (no persistence)

### 34. Network Traffic
- [ ] Monitor network requests
- [ ] Only requests to:
  - [ ] 127.0.0.1:5000 (Flask app)
  - [ ] imap.gmail.com or imap-mail.outlook.com (email server)
  - [ ] No requests to external servers
  - [ ] No analytics tracking
  - [ ] No ad networks

---

## USABILITY TESTING

### 35. First Impression
- [ ] UI looks professional
- [ ] Privacy notice reassuring
- [ ] Purpose clear from header
- [ ] Not intimidating/technical
- [ ] HERD values evident

### 36. Flow Intuitiveness
- [ ] Login → Analyze flow obvious
- [ ] Results → Actions flow clear
- [ ] Payment positioning appropriate
- [ ] No confusion about next steps

### 37. Error Recovery
- [ ] Errors don't require refresh
- [ ] Can retry after error
- [ ] Error messages helpful (not technical jargon)
- [ ] "Try Again" obvious

### 38. Mobile (if applicable)
- [ ] Open on phone browser
- [ ] Layout responsive
- [ ] Text readable
- [ ] Buttons tappable
- [ ] Table scrollable horizontally

---

## FINAL CHECKLIST

### 39. Documentation
- [ ] README.md clear and complete
- [ ] QUICK_START.md helpful for new users
- [ ] EMAIL_SCRAPER_HANDOVER.md comprehensive
- [ ] Code comments present
- [ ] No obvious typos

### 40. Code Quality
- [ ] No Python errors in console
- [ ] No JavaScript errors in browser console
- [ ] Code follows consistent style
- [ ] Functions have clear names
- [ ] No dead code

### 41. Production Readiness
- [ ] Privacy notice matches actual behavior
- [ ] All placeholder features clearly marked
- [ ] No "TODO" comments in user-facing text
- [ ] Build script (build.bat) present
- [ ] requirements.txt accurate

---

## TEST RESULTS SUMMARY

### Bugs Found
List any issues discovered:
1. 
2. 
3. 

### Performance Notes
- Average 1-day analysis time: ___
- Average 7-day analysis time: ___
- Acceptable? Yes / No

### Usability Feedback
- Privacy notice clear? Yes / No
- Flow intuitive? Yes / No
- Errors helpful? Yes / No
- Would use again? Yes / No

### Overall Assessment
- [ ] Ready for Phase 2 work
- [ ] Needs bug fixes first
- [ ] Needs major refactoring
- [ ] Scrap and restart (hopefully not!)

---

## SIGN-OFF

Tester: _______________  
Date: _______________  
Version: MVP v1.0  

**Approved for Phase 2?** Yes / No  

**Notes:**

