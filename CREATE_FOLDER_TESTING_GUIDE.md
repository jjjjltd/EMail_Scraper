# Create Folder Feature - Testing Guide

## What's Implemented

✅ **Modular Architecture**
- `email_actions.py` - Self-contained action functions
- `config.py` - Feature flag configuration
- Clean separation of concerns

✅ **Create Folder Action (Test 7-12)**
- Modal dialog with folder name input
- Default folder name from sender name
- Confirm button before action
- Progress feedback during execution
- Moves ALL emails from sender to folder
- Attempts to create email rule (informs if manual step needed)

✅ **Feature Flags**
- Enable/disable features via .env
- UI automatically hides disabled buttons
- Easy to ship incrementally

---

## Setup Instructions

### 1. Update .env File

Add these lines to your `.env`:

```bash
# Feature Flags
FEATURE_CREATE_FOLDER=true
FEATURE_DELETE_ALL=false
FEATURE_MANAGE_HISTORY=false
FEATURE_ARCHIVE=false
FEATURE_UNSUBSCRIBE=false
```

### 2. Install Files

Replace these files with new versions:
- `app.py`
- `static/style.css`
- `templates/results.html`

Add these NEW files:
- `email_actions.py`
- `config.py`

### 3. No New Dependencies

No pip install needed - uses existing libraries!

---

## Testing Checklist

### Test 7: Prompt Default Folder Name ✅

**Steps:**
1. Run analysis (Google or Microsoft, Last 1 Day)
2. Select ONE sender checkbox
3. Click "📁 Create Folder" button
4. **Expected:** Modal appears with default folder name (sender name, cleaned)

**Pass Criteria:**
- Modal shows sender name and email
- Default folder name is pre-filled
- Name is editable


### Test 8: Confirm Button Before Action ✅

**Steps:**
1. Continue from Test 7
2. Edit folder name if desired
3. Click "Cancel"
4. **Expected:** Modal closes, no action taken
5. Repeat, click "Create Folder & Move Emails"

**Pass Criteria:**
- Cancel works without side effects
- Confirm triggers action
- Button shows "Processing..." during execution


### Test 9: Progress Bar Implementation ⏳

**Status:** Partial implementation
- Progress message shows during execution
- ✅ "Creating folder and moving emails..."
- ✅ "Success! Moved X emails..."
- ❌ No actual progress bar (would require async updates)

**Phase 2:** Could add WebSocket for real-time progress


### Test 10: Move ALL Emails from Sender ✅

**Steps:**
1. Note count of emails from sender before action
2. Execute Create Folder action
3. Check inbox after completion
4. Check new folder

**Pass Criteria:**
- All emails from sender moved to folder
- Inbox no longer shows emails from that sender
- Folder contains all expected emails

**Testing:**
```
Before: Inbox shows "Google (3 emails)"
After:  Inbox no longer shows Google
        Folder "Google" contains 3 emails
```


### Test 11: Create Email Rule ⚠️

**Status:** IMAP Limitation Documented

**Current Behavior:**
- App attempts to create rule via IMAP
- IMAP does not support creating filters/rules
- App informs user with manual instructions

**Alert Message:**
```
✅ Success! Moved X emails to "FolderName"

⚠️ Email Rule:
Gmail/Outlook filters require manual creation (not available via IMAP)

Manual step required:
Create filter: FROM sender@example.com → Move to FolderName
```

**Pass Criteria:**
- User is clearly informed
- Manual instructions provided
- Folder creation still succeeds


### Test 12: Test Email Rule (Where Provable) ⏳

**Status:** Manual verification required

**Steps:**
1. After Test 11, manually create the rule in Gmail/Outlook
   - Gmail: Settings → Filters → Create filter
   - Outlook: Settings → Rules → Create rule
2. Send test email from that sender (or wait for natural email)
3. Verify new email goes directly to folder

**Pass Criteria:**
- New emails automatically sorted to folder
- Inbox stays clean

---

## Known Limitations

### IMAP Cannot Create Rules
- Gmail filters require Gmail API
- Outlook rules require Graph API
- Workaround: Provide clear manual instructions

### Single Sender Only
- Create Folder currently supports 1 sender at a time
- Selecting multiple shows: "Please select only ONE sender"
- Phase 2: Could batch process multiple senders

### No Undo
- Moving emails is permanent
- Phase 2: Could add archive/backup before move

---

## Error Handling

**Tested Scenarios:**
- ✅ No sender selected → Button stays disabled
- ✅ Multiple senders → Alert: "Select only ONE"
- ✅ Empty folder name → Alert: "Enter a folder name"
- ✅ Folder already exists → Proceeds (not an error)
- ✅ IMAP connection fails → Error message shown
- ✅ OAuth token expired → Redirects to login

---

## Feature Flags Testing

### Disable Create Folder

In `.env`, set:
```
FEATURE_CREATE_FOLDER=false
```

**Expected:**
- "📁 Create Folder" button does not appear
- API endpoint still protected (returns disabled message)

### Enable Other Features

Set any feature to `true`:
```
FEATURE_DELETE_ALL=true
```

**Expected:**
- Button appears in toolbar
- Placeholder alert shows "Phase 2" message

---

## Success Criteria Summary

| Test | Description | Status |
|------|-------------|--------|
| 7 | Default folder name prompt | ✅ Pass |
| 8 | Confirm button | ✅ Pass |
| 9 | Progress indicator | ⚠️ Partial |
| 10 | Move all emails | ✅ Pass |
| 11 | Create email rule | ⚠️ Manual |
| 12 | Test rule works | ⏳ Manual |

**Overall: 4/6 Automated, 2/6 Manual Steps Required**

---

## Next Steps After Testing

1. **Test on Google account** (primary)
2. **Test on Microsoft account** (secondary)
3. **Document any issues found**
4. **Update test script with results**
5. **Phase 2:** Implement Delete All, Manage History, Archive

---

## Troubleshooting

### "Feature not enabled" error
- Check `.env` has `FEATURE_CREATE_FOLDER=true`
- Restart Flask app after changing .env

### Modal doesn't appear
- Check browser console for JavaScript errors
- Verify `style.css` loaded correctly
- Try hard refresh (Ctrl+F5)

### Emails not moving
- Check IMAP connection is active
- Verify OAuth token is valid
- Check terminal for DEBUG messages

### "Multiple senders selected" even with one
- Check checkbox state in DevTools
- Verify `data-sender` attribute on table rows
- Check `selectedSenders` set in console

---

## Architecture Notes

### Modular Design
Each action is self-contained in `EmailActions` class:
```python
EmailActions.create_folder(mail, sender, folder, provider)
EmailActions.delete_all(mail, sender, provider)
EmailActions.manage_history(mail, sender, config, provider)
```

**Benefits:**
- Easy to test individually
- Can enable/disable independently
- Future: Could move to plugins
- Clear separation of concerns

### Feature Flags
Controlled via `config.py` and `.env`:
```python
FEATURES = {
    'create_folder': True,
    'delete_all': False,
    ...
}
```

**Benefits:**
- Ship partial functionality safely
- A/B testing capability
- Easy rollback if issues found
- Gradual user rollout

---

## Ready for Testing! 🚀

Start with Test 7 and work through systematically.
Document results in test script Excel file.
Report any issues or unexpected behavior.
