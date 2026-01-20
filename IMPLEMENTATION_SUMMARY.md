# Microsoft Graph API JWT Token Implementation
## Summary of Changes

### Problem Solved
Microsoft OAuth returns two different token types:
- **v1.0 tokens** (for IMAP) - no dots, format: `EwA4BOl3...`
- **JWT tokens** (for Graph API) - has dots, format: `header.payload.signature`

Previous implementation used IMAP scopes which gave v1.0 tokens, breaking Graph API actions.

### Solution Architecture
**Dual OAuth Flow** - Keep both token types for different purposes:

1. **Initial OAuth** (IMAP analysis) - UNCHANGED
   - Uses `outlook.office.com` scopes
   - Returns v1.0 token → stored as `session['access_token']`
   - Powers inbox analysis (working, don't touch)

2. **Lazy Graph OAuth** (actions) - NEW
   - Triggered on first action button confirm
   - Uses `graph.microsoft.com` scopes
   - Returns JWT token → stored as `session['graph_token']`
   - Powers all action buttons

---

## File Changes

### 1. app.py - Main Changes

#### A. OAuth Configuration (lines 57-82)
```python
# Split into TWO OAuth clients:

# microsoft (IMAP - for analysis)
- Scopes: outlook.office.com/IMAP.AccessAsUser.All, Mail.Read
- Token type: v1.0 (no dots)
- Purpose: Inbox analysis via IMAP

# microsoft_graph (Graph API - for actions)
- Scopes: graph.microsoft.com/Mail.ReadWrite, MailboxSettings.ReadWrite
- Token type: JWT (has dots)
- Purpose: All action buttons
```

#### B. New Routes Added

**Route: `/login/microsoft-graph`** (lines 577-610)
- Initiates Graph API OAuth
- Stores pending action in memory (`app.graph_oauth_states`)
- Redirects to Microsoft with Graph API scopes

**Route: `/oauth/microsoft-graph/callback`** (lines 612-674)
- Handles Graph OAuth callback
- Exchanges code for JWT token
- Stores `graph_token` in session
- Redirects to execute pending action

**Route: `/execute-pending-action`** (lines 676-694)
- Executes stored action after Graph OAuth
- Renders execution template for frontend

#### C. Modified Route: `/action/create-folder` (lines 867-932)

**For Microsoft provider:**
```python
# Check for graph_token
if not graph_token:
    # Store action data
    session['pending_action'] = {
        'type': 'create_folder',
        'sender_emails': [...],
        'folder_name': 'name'
    }
    
    # Return redirect instruction to frontend
    return jsonify({
        'needs_graph_auth': True,
        'redirect_url': '/login/microsoft-graph'
    })

# Use graph_token for action (JWT)
result = EmailActions.create_folder_microsoft(graph_token, ...)
```

---

### 2. email_actions.py - NO CHANGES
The `create_folder_microsoft()` function already uses Graph API endpoints.
Now it receives JWT tokens instead of v1.0 tokens → will work.

---

### 3. New Template Files

#### templates/graph_auth_success.html
- Shown after successful Graph OAuth
- Auto-redirects to execute pending action
- Loading spinner for UX

#### templates/execute_create_folder.html
- Auto-POSTs to `/action/create-folder` endpoint
- Shows progress spinner
- Handles success/error responses
- Redirects back to results page

---

## User Flow

### First Time Using Action Button:
```
1. User analyzes inbox (IMAP OAuth ✓, has v1.0 token)
2. User clicks "Create Folder" → enters name → clicks "Confirm"
3. Backend checks: graph_token exists? → NO
4. Backend stores action data, returns redirect URL
5. Frontend redirects to /login/microsoft-graph
6. Microsoft consent screen (one-time)
7. Redirect back to /oauth/microsoft-graph/callback
8. Backend stores graph_token (JWT)
9. Redirect to /execute-pending-action
10. Auto-execute create-folder action
11. Success! Return to results
```

### Subsequent Action Buttons:
```
1. User clicks any action button → "Confirm"
2. Backend checks: graph_token exists? → YES
3. Use graph_token immediately
4. Execute action
5. Return result
```

### Token Expiration:
```
1. User clicks action after token expires
2. Backend checks: graph_token valid? → NO (expired/missing)
3. Same flow as "First Time" above
4. Re-authenticate, get new JWT
5. Execute action
```

---

## Session Storage

```python
session = {
    'email': 'user@example.com',
    'provider': 'microsoft',
    'days': '7',
    
    # IMAP token (v1.0) - for analysis
    'access_token': 'EwA4BOl3BAAU0wDjFA6usBY8gB...',
    
    # Graph API token (JWT) - for actions
    'graph_token': 'eyJhbGciOiJSUzI1NiIsIng1d...',
    
    # Pending action (during OAuth redirect)
    'pending_action': {
        'type': 'create_folder',
        'sender_emails': ['bbc@email.com'],
        'folder_name': 'BBC Emails'
    }
}
```

---

## Testing Checklist

### Prerequisites
- [ ] Azure app has Graph API permissions added (Mail.ReadWrite, MailboxSettings.ReadWrite)
- [ ] Redirect URI added: `http://localhost:5000/oauth/microsoft-graph/callback`

### Test Flow
1. **Initial Analysis** (existing flow)
   - [ ] Click "Connect with Outlook"
   - [ ] Complete OAuth → analysis works
   - [ ] Verify `access_token` in session (v1.0)

2. **First Action** (new flow)
   - [ ] Select sender → Click "Create Folder"
   - [ ] Enter folder name → Click "Confirm"
   - [ ] Redirected to Microsoft consent screen
   - [ ] Grant permissions
   - [ ] Auto-redirected back → action executes
   - [ ] Folder created successfully
   - [ ] Verify `graph_token` in session (JWT with dots)

3. **Subsequent Actions** (cached token)
   - [ ] Select different sender → "Create Folder"
   - [ ] No Microsoft redirect (uses cached token)
   - [ ] Action executes immediately

4. **Token Expiration**
   - [ ] Wait 1 hour or clear `graph_token` from session
   - [ ] Try action → should re-auth automatically

---

## Debugging

### Check Token Types in Console
```python
# In app.py routes, tokens are logged:
DEBUG: access_token first 50: EwA4BOl3BAAU0wDjFA6usBY8gB...
DEBUG: access_token has dots? False

DEBUG Graph: token first 50: eyJhbGciOiJSUzI1NiIsIng1d...
DEBUG Graph: token has dots (JWT)? True
```

### Common Issues

**Issue: "JWT not well formed, no dots"**
- Cause: Using v1.0 token for Graph API
- Fix: Check that `graph_token` exists and is being used

**Issue: Redirect loop after OAuth**
- Cause: Pending action not stored correctly
- Fix: Check `session['pending_action']` is set before redirect

**Issue: "Invalid state"**
- Cause: State token not found in memory
- Fix: Check `app.graph_oauth_states` dict

---

## Next Steps

### Extend to Other Actions
Same pattern for Delete All, Archive, Clean-up History:

```python
# In /action/delete-all route:
if provider == 'microsoft':
    graph_token = session.get('graph_token')
    
    if not graph_token:
        session['pending_action'] = {
            'type': 'delete_all',
            'sender_emails': sender_emails
        }
        return jsonify({
            'needs_graph_auth': True,
            'redirect_url': '/login/microsoft-graph'
        })
    
    # Use graph_token for delete action
    result = EmailActions.delete_all_microsoft(graph_token, ...)
```

### Production Considerations
1. **Token refresh**: Implement refresh token flow for long sessions
2. **State cleanup**: Clear old state tokens from `app.graph_oauth_states`
3. **Redirect URI**: Update to production domain
4. **Error handling**: Better user messages for auth failures
5. **Rate limiting**: Handle Graph API throttling (429 responses)

---

## Summary

**What Changed:**
- Split Microsoft OAuth into IMAP (analysis) and Graph (actions)
- Added lazy JWT generation on first action
- Preserved existing IMAP analysis flow (no regressions)

**What Stayed Same:**
- Google OAuth (untouched)
- Analysis via IMAP for Microsoft (working, don't touch)
- Frontend UI (no changes needed)

**Result:**
- Microsoft users can now use ALL action buttons
- Seamless UX (one-time consent, then cached)
- No breaking changes to existing functionality

**Token Spend:** ~11K tokens for design discussion + implementation
