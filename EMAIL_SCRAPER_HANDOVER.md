# 📧 EMAIL SCRAPER - MVP HANDOVER DOCUMENT

## EXECUTIVE SUMMARY

**Project:** Email Scraper - HERD-principled inbox analysis tool  
**Status:** MVP Complete - Ready for Testing  
**Date:** November 2025  
**Purpose:** Trust-building foundation for Subscription Scraper using honor-based payment model

**Core Achievement:** Built a privacy-first desktop application that connects to email via IMAP, analyzes inbox locally, detects clutter and unsubscribe opportunities, and prepares for PayPal integration.

---

## PROJECT PHILOSOPHY: HERD PRINCIPLES

This project follows the same HERD philosophy as Subscription Scraper:

**H - Honor:** We trust customers to pay fairly. They trust us with their email data.

**E - Etiquette:** We deliver value BEFORE asking for payment. We NEVER mine email data.

**R - Respect:** We help customers achieve inbox peace and reduce digital overwhelm.

**D - Discipline:** KaaS (Kindness as a Service) - focused determination to make the world better.

### Email Scraper's Strategic Role

**Trust Builder:** Email analysis is LESS sensitive than financial data. This proves:
- We keep our privacy promises
- We're not a data mining operation
- We deliver real value first
- We're honorable with sensitive information

**Loss Leader:** Free (with optional honor payment) service that:
- Establishes trust before Subscription Scraper
- Demonstrates HERD principles in action
- Captures email for future product downloads
- Proves value-first business model works

---

## TECHNICAL ARCHITECTURE

### Technology Stack
- **Backend:** Python 3.8+ + Flask
- **Frontend:** HTML/CSS/JavaScript (vanilla, matching Subscription Scraper)
- **Email Access:** IMAP (imaplib) - Gmail and Outlook
- **Data Processing:** In-memory only (no storage)
- **Distribution:** Standalone .exe via PyInstaller (planned)

### Privacy-First Design
- **Runs on:** localhost (127.0.0.1) only
- **Data storage:** None. Everything in memory, credentials used once then discarded
- **No backend:** No servers, no databases, no cloud
- **No file system writes:** Emails processed in memory only
- **Internet required:** Only for IMAP connection (to user's own email server)

### Supported Email Providers
- Gmail (imap.gmail.com) - requires App Password
- Outlook/Hotmail/Live (imap-mail.outlook.com)

---

## CORE FUNCTIONALITY

### 1. Email Authentication

**Credentials Required:**
- Email address (full address, e.g., user@gmail.com)
- Email password (or App Password for Gmail)

**Security:**
- Credentials used once to establish IMAP connection
- Stored in memory only during analysis
- Never written to disk
- Never transmitted to our servers

**Gmail Special Case:**
Gmail requires "App Passwords" for third-party apps:
1. Enable 2-Step Verification
2. Generate App Password in account settings
3. Use 16-character App Password instead of regular password

### 2. Inbox Analysis

**Date Range Options:**
- 1 day (default, fastest)
- 5 days
- 7 days (maximum for MVP)

**What It Analyzes:**
- INBOX folder only (not Sent, Drafts, Spam, etc.)
- Emails within selected date range
- Groups by sender email address
- Calculates metrics per sender

**Metrics Calculated:**
- **Count:** Number of emails from sender
- **Total Size:** Storage used (in KB or MB)
- **Last Received:** Most recent email date/time
- **Read Count:** Emails user has opened
- **Unread Count:** Emails user hasn't opened
- **% Unread:** Percentage of unopened emails
- **Nuisance Score:** Sum of (unread% + count + size_in_MB)
- **Has Unsubscribe:** Boolean flag if unsubscribe link detected

### 3. Results Display

**Table Columns:**
1. ☑️ Checkbox - Select sender for bulk actions
2. Sender Name - Extracted from email From header
3. Organization - Domain-based (e.g., "gmail" from email@gmail.com)
4. Count - Number of emails
5. Size - Display in KB or MB
6. Last Received - Date and time
7. Read/Unread - "X / Y" format
8. % Unread - Percentage
9. Nuisance - Calculated score with tooltip
10. Unsubscribe? - Yes/No badge with tooltip

**Sorting:**
- Click any column header to sort
- Default: Sender Name (ascending)
- Toggle between ascending/descending
- Visual indicators (▲/▼) show current sort

**Selection:**
- Individual checkboxes per sender
- "Select All" checkbox in header
- Action buttons enable when selections made

### 4. Actions (Phase 1 - Placeholders)

**Action Toolbar:**
- 🚫 Unsubscribe - Flag for Phase 2 implementation
- 📁 Create Folder - Flag for Phase 2 implementation
- 🗃️ Manage History - Flag for Phase 2 implementation
- 🗑️ Delete All - Flag for Phase 2 implementation
- 📦 Archive - Flag for Phase 2 implementation

**Current Behavior:**
- Buttons disabled until sender(s) selected
- Clicking shows modal: "Feature coming in Phase 2"
- Shows number of selected senders

**Phase 2 Plans:**
- Each action opens confirmation screen
- Lists selected senders with counts
- Provides action-specific options
- Requires explicit confirmation
- Never instant-delete or instant-action

### 5. Payment Flow (Phase 1 - Placeholder)

**Payment Section:**
- Appears after results displayed
- Shows value statement
- Two buttons:
  - "Pay for Service" (2/3 width, green)
  - "Do Not Pay" (1/3 width, gray)

**Current Behavior:**
- Buttons show alert: "PayPal integration coming soon"
- No actual payment processing
- Prepares user expectation for honor payment

**Phase 2 Plans:**
- PayPal SDK integration
- Payment based on usage (days analyzed)
- Metadata tracking: days_analyzed, payment_tier
- Closing splash with value summary
- "Close and Pay" second chance option

---

## FILE STRUCTURE

```
email_scraper/
├── app.py                    # Flask app + IMAP logic
├── templates/
│   └── index.html           # Complete UI (single file)
├── requirements.txt         # Python dependencies
├── build.bat               # Windows build script for .exe
└── README.md               # User documentation
```

### Key Files

**app.py** - Main application:
- `/` - Serves index.html
- `/analyze` - POST endpoint for email analysis
- `get_imap_server()` - Determines IMAP server from email domain
- `decode_mime_words()` - Handles email header encoding
- `extract_sender_info()` - Parses From header
- `get_organization()` - Extracts domain organization
- `check_unsubscribe()` - Scans for unsubscribe links
- `analyze_emails()` - Main IMAP connection and analysis

**index.html** - Complete UI:
- Login form with email/password/days
- Privacy notice section
- Analyzing spinner screen
- Results table with sorting
- Action toolbar with disabled buttons
- Payment section with placeholders
- Action modal for future features

**requirements.txt:**
```
Flask==3.0.0
```

**build.bat** - PyInstaller build script:
- Kills running processes
- Cleans previous builds
- Creates standalone .exe
- Bundles templates folder

---

## DESIGN DECISIONS & WHY

### Why IMAP Instead of Downloaded Files?

**Target Audience:** Low IT sophistication
- Downloading all emails = friction + storage panic
- Most users don't know how to export emails
- IMAP = "just works" experience

**Privacy Trade-off:**
- Connects to email servers (not 100% offline)
- BUT: Still privacy-first (no storage, no transmission to us)
- Honest positioning: "We analyze locally, never store"

### Why Inbox Only?

**Simplicity:** 
- Inbox = primary pain point
- Other folders less relevant (Sent, Drafts, Spam)
- Keeps MVP focused

**Performance:**
- Analyzing multiple folders = slow
- Phase 2 can add folder selection

### Why 7-Day Maximum?

**Performance:**
- Large inboxes (10,000+ emails) = slow analysis
- 7 days = reasonable sample size
- Prevents abuse/overload

**User Experience:**
- Forces focused analysis
- "Leave overnight" warning if 7 days selected
- Phase 2: Calendar selector with visual 7-day cap

### Why Nuisance Score Unweighted?

**Simplicity:**
- Raw sum: `unread% + count + size_MB`
- Easy to understand
- "Good enough" for MVP

**Phase 2:**
- Add weighting: `(unread% × 0.5) + (count × 0.3) + (size × 0.2)`
- Make weights configurable
- A/B test optimal formula

### Why Sender Name Sort Default?

**Alphabetical = Familiar:**
- Users expect alphabetical by default
- Easy to find specific sender
- Low cognitive load

**Alternative Sorts Available:**
- Nuisance (high first) = shows worst offenders
- Count (high first) = shows volume senders
- Date (recent first) = shows active senders

### Why Tooltips on Headers?

**Clarity Without Clutter:**
- "Nuisance" needs explanation (ℹ️ tooltip)
- "Unsubscribe?" could be ambiguous (ℹ️ tooltip)
- Hover reveals details without UI noise

### Why Action Buttons Styled Like SharePoint?

**Professional Not Clunky:**
- Icon + text links (not heavy buttons)
- Clean toolbar aesthetic
- Context-aware (gray out when disabled)
- Familiar UX pattern

---

## CURRENT STATUS & TESTING NEEDS

### ✅ Complete (MVP Ready)

1. **Core functionality:**
   - IMAP connection works
   - Email parsing and aggregation
   - Metrics calculation
   - Unsubscribe detection
   - Sender organization extraction

2. **UI/UX:**
   - Login form with validation
   - Privacy notice prominent
   - Analyzing spinner
   - Results table with all columns
   - Sortable columns
   - Checkbox selection
   - Action toolbar (disabled buttons)
   - Payment section (placeholder)

3. **Technical:**
   - Flask app imports successfully
   - Template rendering works
   - Build script ready
   - README documentation complete

### ⚠️ Needs Testing (Critical Before Release)

1. **Gmail Integration:**
   - Test with real Gmail account
   - Verify App Password flow works
   - Handle authentication errors gracefully
   - Test with large Gmail inbox (10,000+ emails)

2. **Outlook Integration:**
   - Test with real Outlook account
   - Verify IMAP connection works
   - Test with large Outlook inbox

3. **Performance:**
   - 1 day analysis = fast enough?
   - 7 day analysis = too slow?
   - Progress indicator needed?
   - Handle 10,000+ email inboxes

4. **Edge Cases:**
   - Empty inbox (no emails in period)
   - Malformed email headers
   - Non-UTF-8 encoded senders
   - Extremely large single email
   - Timeout on slow IMAP servers

5. **Browser Compatibility:**
   - Test in Chrome, Firefox, Edge
   - Test on Windows, Mac (if possible)
   - Verify localhost access works

### 🔴 Known Limitations (Accept for MVP)

1. **No actual unsubscribe:** Detection only, not automation
2. **No PayPal integration:** Placeholder only
3. **No closing splash:** Coming in Phase 2
4. **No usage tracking:** No metadata in PayPal
5. **No folder selection:** Inbox only
6. **No date range > 7 days:** Hard limit
7. **No progress details:** Just spinner, no "X emails processed"
8. **No .exe build yet:** Needs testing with PyInstaller
9. **No organization grouping:** Flat sender list only

---

## PHASE 2 PRIORITIES

### Critical (Must Have)

1. **PayPal Integration:**
   - SDK setup (sandbox → production)
   - Payment modal with tier options
   - Metadata: days_analyzed, sender_count
   - Success/failure handling

2. **Closing Splash:**
   - Value summary (emails analyzed, senders found, potential cleanup)
   - "Leave" and "Stay Open" buttons
   - "Close and Pay" for non-payers
   - Match Subscription Scraper aesthetic

3. **Action Confirmations:**
   - Each action = confirmation screen
   - List selected senders with details
   - Action-specific options
   - Explicit "Confirm" button

### Important (Should Have)

4. **Auto-Unsubscribe:**
   - Parse unsubscribe links from emails
   - Handle List-Unsubscribe headers
   - Click unsubscribe links programmatically
   - Confirm unsubscribe success

5. **Create Folder:**
   - Default folder name from sender
   - Option to auto-file current emails
   - Option to create forwarding rule
   - Execute via IMAP commands

6. **Manage History:**
   - Retain only last N emails option
   - Retain only for X period option
   - Archive vs Delete toggle
   - Create automation rule

### Nice to Have (Could Have)

7. **Delete All:**
   - Move to Trash (not permanent delete)
   - Option to block sender
   - Confirm count before delete

8. **Archive:**
   - Zip selected emails
   - Calculate space savings
   - Phase 2.5: Cloud/cold storage integration

9. **Organization Grouping:**
   - Toggle view: by sender vs by organization
   - Collapse/expand organizations
   - Aggregate metrics per org

10. **Usage Count Gating:**
    - Track analysis count
    - After 3 free analyses, prompt payment
    - "Unlock unlimited" with honor payment

---

## BUILD & DEPLOYMENT GUIDE

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
python app.py

# Opens browser at http://127.0.0.1:5000
```

### Building .exe (Windows)

```bash
# Ensure PyInstaller installed
pip install pyinstaller

# Run build script
build.bat

# Output: dist/EmailScraper.exe
```

### Build Notes

- Virtual environment: Use Python 3.8-3.12 (avoid bytecode bugs)
- Kill running .exe before rebuilding (file lock issue)
- Include templates folder in build
- Test on machine WITHOUT Python installed
- File size: ~10-15 MB expected

### Distribution Plan

**Step 1: Static Landing Page**
- Platform: Netlify or Vercel (free)
- Content:
  - JJJJ Ltd intro + HERD principles
  - Email Scraper overview
  - Privacy promise prominent
  - Email gate for download
  - Download link to latest .exe

**Step 2: Email Capture**
- Tool: Simple form → Airtable or JSON file
- Data stored:
  - Email address
  - App name ("Email Scraper")
  - Payment amount (default: 0)
  - Download date

**Step 3: Host .exe**
- GitHub Releases or Netlify static hosting
- Update process:
  1. Build new .exe
  2. Upload to hosting
  3. Update download link
  4. Email existing users (optional)

**Step 4: Go Live**
- Test on non-Python machines FIRST
- PayPal sandbox → production
- Soft launch to small group (10-20 people)
- Gather feedback
- Iterate

---

## SUCCESS METRICS

### Phase 1 (Prove Concept)
- Downloads > 500
- Usage rate > 60% (actually analyze inbox)
- No major bugs reported
- Positive feedback on privacy positioning

### Phase 2 (Validate Model)
- Payment rate > 10%
- Average payment ≥ £2
- Repeat usage > 20%
- NPS score > 40

### Phase 3 (Scale)
- Monthly active users > 5,000
- Payment rate > 15%
- Cross-app adoption (Subscription Scraper) > 30%
- Revenue > £1,500/month

---

## LESSONS LEARNED (Anticipated)

### From Subscription Scraper Experience

**What Will Work:**
- Privacy-first positioning builds trust
- HERD principles guide all decisions
- Fast iterations = better product
- Real user testing reveals edge cases
- Simple tech stack = easier maintenance

**What to Watch:**
- IMAP authentication complexity
- Gmail App Password confusion
- Performance with large inboxes
- Balance between features and simplicity

### Anticipated Challenges

1. **Gmail App Passwords:**
   - Users won't know about them
   - Need clear instructions + screenshots
   - Support burden expected

2. **Performance:**
   - 10,000 email inbox = potential slowness
   - Progress indicator critical
   - May need optimization

3. **Unsubscribe Complexity:**
   - Each sender has different unsubscribe method
   - List-Unsubscribe headers inconsistent
   - Link clicking = potential security concern
   - Phase 2 may be harder than expected

4. **Payment Psychology:**
   - Email cleanup < Financial savings
   - May need stronger value messaging
   - Payment rate might be < Subscription Scraper

---

## MARKETING & MESSAGING

### Value Proposition

**Primary:** "Clean inbox, clear mind"  
**Secondary:** "Privacy-first email analysis"  
**Differentiator:** "We analyze locally - your emails never leave your device"

### Target Audience

**Primary:** People overwhelmed by email clutter
- Professionals with 10,000+ emails
- Non-technical users who don't know how to manage email
- Privacy-conscious individuals

**Secondary:** Future Subscription Scraper users
- Need trust before sharing financial data
- Email Scraper proves we're honorable
- Low barrier to entry (free, optional payment)

### Messaging Framework

**Trust Building:**
- "Your data never leaves your device"
- "No data mining. No selling. No storage."
- "We only need your email for download"

**Value First:**
- "Find unsubscribe opportunities"
- "Calculate inbox clutter score"
- "Take informed action"

**Honor Payment:**
- "Found this useful? Pay what you think it's worth"
- "Your payment helps us build more privacy-first tools"
- "No payment required - but deeply appreciated"

---

## TODO LIST

### Critical (Before First User Test)
- [ ] Test with real Gmail account (yours)
- [ ] Test with real Outlook account (yours)
- [ ] Verify App Password flow works
- [ ] Handle edge case: no emails in period
- [ ] Add progress text: "Analyzing... X emails processed"
- [ ] Test on Windows machine without Python

### Important (Before Public Launch)
- [ ] PayPal sandbox integration
- [ ] Closing splash screen
- [ ] Build .exe and test distribution
- [ ] Write Gmail App Password guide (with screenshots)
- [ ] Create landing page copy
- [ ] Email capture form

### Nice to Have (Post-Launch)
- [ ] Calendar date selector (7-day max)
- [ ] Weighted nuisance scoring
- [ ] Organization grouping toggle
- [ ] Export results to CSV
- [ ] Usage count tracking

---

## NEXT SESSION PLAN

### Immediate Tasks

1. **Test Gmail Integration:**
   - Use your own Gmail account
   - Generate App Password
   - Run analysis on 1 day
   - Verify results accurate

2. **Test Outlook Integration:**
   - Use your own Outlook account
   - Ensure IMAP enabled
   - Run analysis on 1 day
   - Verify results accurate

3. **Edge Case Testing:**
   - Empty inbox (no emails in period)
   - Very large inbox (if available)
   - Malformed sender names

4. **Performance Assessment:**
   - Time 1 day analysis
   - Time 7 day analysis
   - Determine if progress indicator needed

5. **Bug Fixes:**
   - Address any issues found in testing
   - Improve error messages
   - Handle timeouts gracefully

### Future Sessions

**Session 2: PayPal & Polish**
- PayPal SDK integration
- Closing splash implementation
- Payment tier options
- Metadata tracking

**Session 3: Actions Phase 1**
- Confirmation screens for each action
- List selected senders
- Action-specific options
- No actual execution yet

**Session 4: Actions Phase 2**
- Auto-unsubscribe implementation
- Create folder functionality
- Manage history options
- Archive to zip

**Session 5: Build & Deploy**
- PyInstaller .exe build
- Test on non-Python machine
- Create landing page
- Set up email capture
- Soft launch

---

## CONTACT & SUPPORT

**Developer:** JJJJ Ltd  
**Project Lead:** [User]  
**AI Partner:** Claude (Anthropic)  
**License:** Proprietary (HERD-principled, but commercial)

---

## FINAL NOTES

**Email Scraper is the trust foundation for HERD portfolio.**

By analyzing emails (less sensitive than finance), we prove:
- Our privacy promises are real
- We deliver value before asking for money
- We're not data miners in disguise
- Our business model works without exploitation

**If users trust us with their inbox, they'll trust us with their bank statements.**

This is intentional. This is strategic. This is HERD in action.

---

*Document Version: 1.0*  
*Last Updated: November 2025*  
*Status: MVP Complete - Ready for Testing*
