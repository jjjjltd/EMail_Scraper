# 📧 EMAIL SCRAPER - MVP v1.0

**HERD-principled inbox analysis tool**  
*Privacy-first. Value-first. Honor-based payment.*

---

## 🎯 WHAT IT DOES

Email Scraper analyzes your inbox to help you:
- **Identify email clutter** - See which senders flood your inbox
- **Spot unsubscribe opportunities** - Flags emails with unsubscribe links
- **Calculate nuisance scores** - Combines unread%, count, and size
- **Take informed action** - Sort, filter, and Clean-up your email

**All processing happens locally. Your emails never leave your device.**

---

## 🔒 PRIVACY PROMISE

We only collect:
- ✅ Your email address (for download)
- ✅ PayPal payment info (optional, if you choose to pay)

We NEVER:
- ❌ Store your email password
- ❌ Save your emails
- ❌ Mine your data
- ❌ Sell your information

Your credentials are used once, in memory only, then discarded.

---

## 🚀 QUICK START

### Prerequisites
- Python 3.8 or higher
- Gmail or Outlook email account

### Installation

1. **Extract the files** to a folder
2. **Open terminal/command prompt** in that folder
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python app.py
```

The app will:
1. Start a local server at `http://127.0.0.1:5000`
2. Open your browser automatically
3. Show the analysis interface

---

## 📖 HOW TO USE

### Step 1: Enter Your Credentials
- **Email:** Your Gmail or Outlook address
- **Password:** Your email password
  - **Gmail users:** You may need an "App Password" (see below)
- **Period:** Choose 1, 5, or 7 days to analyze

### Step 2: Analyze
Click "🔍 Analyze My Inbox" and wait while we process your emails locally.

### Step 3: Review Results
You'll see a table with:
- **Sender Name** - Who sent the email
- **Organization** - Domain-based grouping
- **Count** - Number of emails
- **Size** - Total storage used
- **Last Received** - Most recent email date
- **Read/Unread** - Email status counts
- **% Unread** - Percentage you haven't opened
- **Nuisance Score** - Combined metric (unread% + count + size)
- **Unsubscribe?** - Whether unsubscribe link detected

### Step 4: Take Action (Phase 2)
Select senders using checkboxes and choose actions:
- 🚫 Unsubscribe
- 📁 Create Folder
- 🗃️ Clean-up History
- 🗑️ Delete All
- 📦 Archive

*Note: Actions are placeholders in MVP - full implementation coming in Phase 2*

### Step 5: Pay (Optional)
If you found value, consider an honor payment via PayPal.

---

## 🔑 GMAIL APP PASSWORDS

Gmail requires "App Passwords" for third-party applications:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already on)
3. Search for "App Passwords"
4. Generate a new app password for "Mail"
5. Use this 16-character password in Email Scraper

**Why?** This keeps your main password secure while allowing app access.

---

## 📊 FEATURES

### MVP (Current)
- ✅ IMAP connection (Gmail + Outlook)
- ✅ Inbox analysis (1/5/7 day periods)
- ✅ Sender aggregation and metrics
- ✅ Unsubscribe link detection
- ✅ Sortable results table
- ✅ Nuisance scoring
- ✅ Privacy-first architecture

### Phase 2 (Planned)
- ⏳ Auto-unsubscribe functionality
- ⏳ Folder creation and rules
- ⏳ Email history clean-up
- ⏳ Bulk delete operations
- ⏳ Archive to zip/cloud
- ⏳ PayPal integration
- ⏳ Organization grouping

---

## 🛠️ TECHNICAL DETAILS

### Architecture
- **Backend:** Python 3 + Flask
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Email Access:** IMAP (imaplib)
- **Processing:** In-memory only
- **Distribution:** Standalone .exe (planned)

### File Structure
```
email_scraper/
├── app.py                 # Flask application + IMAP logic
├── templates/
│   └── index.html        # Complete UI
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Supported Email Providers
- Gmail (imap.gmail.com)
- Outlook (imap-mail.outlook.com)
- Hotmail (imap-mail.outlook.com)
- Live (imap-mail.outlook.com)

---

## 🐛 TROUBLESHOOTING

### "IMAP error: authentication failed"
- **Gmail:** Use App Password, not your regular password
- **Outlook:** Ensure IMAP is enabled in settings
- Check username is full email address
- Verify password is correct

### "Connection error"
- Check internet connection
- Firewall may be blocking IMAP ports
- Try different email provider

### Analysis is slow
- Analyzing 7 days of email takes longer than 1 day
- Large inboxes (10,000+ emails) may take several minutes
- Consider analyzing shorter periods first

### Emails not showing up
- Only INBOX folder is analyzed (not Sent, Drafts, etc.)
- Only emails within selected date range appear
- Check "days analyzed" in results header

---

## 💡 DESIGN PHILOSOPHY: HERD

**H - Honor:** We trust customers to pay fairly. They trust us with their data.

**E - Etiquette:** We deliver value BEFORE asking for payment. No data mining. Ever.

**R - Respect:** We help customers achieve inbox peace and reduce digital stress.

**D - Discipline:** KaaS (Kindness as a Service) - focused determination to make the world better.

---

## 🗺️ ROADMAP

### Phase 1: MVP (Current)
✅ Core analysis functionality  
✅ Privacy-first architecture  
✅ Basic UI with sorting  
✅ Unsubscribe detection  

### Phase 2: Actions
- Implement full action workflows
- Auto-unsubscribe automation
- Folder creation + rules
- Delete and archive operations

### Phase 3: Polish
- PayPal integration
- Closing splash screen
- Usage metrics in PayPal metadata
- Build standalone .exe

### Phase 4: Scale
- Multi-folder analysis
- Advanced filtering
- Export reports
- Organization grouping

---

## 📝 TODO LIST

### Critical (Next Session)
- [ ] Test with real Gmail account
- [ ] Test with real Outlook account
- [ ] Verify App Password flow
- [ ] Handle large inbox performance
- [ ] Add progress indicator details

### Important (Soon)
- [ ] Implement action confirmation screens
- [ ] Add PayPal integration
- [ ] Create closing splash
- [ ] Build .exe with PyInstaller
- [ ] Add usage count tracking

### Nice to Have (Later)
- [ ] Calendar date selector (7-day max)
- [ ] Organization grouping toggle
- [ ] Weighted nuisance scoring
- [ ] Export to CSV
- [ ] Multi-folder selection

---

## 🤝 CONTRIBUTING

This is a private HERD project by JJJJ Ltd.  
If you want to contribute, please contact the project lead.

---

## 📄 LICENSE

Proprietary - HERD-principled, but commercial

---

## 🙏 ACKNOWLEDGMENTS

Built with HERD principles:
- Privacy-first
- Value-first
- No data mining
- Honor-based payment

**If this works, it changes the game.**

---

*Document Version: 1.0*  
*Last Updated: November 2025*  
*Status: MVP Complete*
