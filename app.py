#!/usr/bin/env python3
"""
Email Scraper - HERD-principled inbox analysis tool
Privacy-first, value-first, honor-based payment
OAuth 2.0 implementation for frictionless authentication
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from collections import defaultdict
import re
import webbrowser
from threading import Timer
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
import base64

# Import email actions and config
from email_actions import EmailActions
from config import FEATURES, get_enabled_actions, is_action_enabled

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Test mode flag
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

# Resource limits
MAX_EMAILS = int(os.getenv('MAX_EMAILS', '5000'))
MAX_TIME_SECONDS = int(os.getenv('MAX_TIME_SECONDS', '300'))

# Initialize OAuth
oauth = OAuth(app)

# Google OAuth configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://mail.google.com/',
        'access_type': 'offline',
        'prompt': 'consent'
    }
)

# Microsoft OAuth configuration  
microsoft = oauth.register(
    name='microsoft',
    client_id=os.getenv('MICROSOFT_CLIENT_ID'),
    client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
    server_metadata_url=f'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/Mail.Read'
    }
)

def decode_mime_words(s):
    """Decode MIME encoded email headers"""
    if s is None:
        return ""
    decoded_fragments = decode_header(s)
    fragments = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            try:
                fragments.append(fragment.decode(encoding or 'utf-8', errors='ignore'))
            except:
                fragments.append(fragment.decode('utf-8', errors='ignore'))
        else:
            fragments.append(str(fragment))
    return ''.join(fragments)

def extract_sender_info(from_header):
    """Extract name and email from From header"""
    if not from_header:
        return "Unknown", "unknown@unknown.com"
    
    # Try to extract email address
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
    email_addr = email_match.group(0) if email_match else from_header
    
    # Extract name (if present)
    name_match = re.match(r'^([^<]+)<', from_header)
    if name_match:
        name = name_match.group(1).strip().strip('"')
    else:
        # Use email prefix as name
        name = email_addr.split('@')[0]
    
    return name, email_addr

def get_organization(email_addr):
    """Extract organization from email domain"""
    try:
        domain = email_addr.split('@')[1]
        # Remove common TLDs and get the main part
        org = domain.split('.')[0]
        return org.capitalize()
    except:
        return "Unknown"

def check_unsubscribe(email_msg):
    """Check if email contains unsubscribe link"""
    # Check headers first
    if email_msg.get('List-Unsubscribe'):
        return True
    
    # Check body for unsubscribe links
    try:
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                if content_type in ['text/plain', 'text/html']:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        if re.search(r'unsubscribe', body, re.IGNORECASE):
                            return True
                    except:
                        pass
        else:
            body = email_msg.get_payload(decode=True)
            if body:
                body_str = body.decode('utf-8', errors='ignore')
                if re.search(r'unsubscribe', body_str, re.IGNORECASE):
                    return True
    except:
        pass
    
    return False

def analyze_emails_oauth(email_address, access_token, provider, days):
    """Connect to IMAP using OAuth and analyze emails"""
    
    try:
        # Determine IMAP server
        if provider == 'google':
            imap_server = 'imap.gmail.com'
        elif provider == 'microsoft':
            imap_server = 'imap-mail.outlook.com'
        else:
            return {'error': 'Unknown provider'}
        
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        
        # Authenticate with OAuth - different methods for different providers
        if provider == 'google':
            # Gmail XOAUTH2 format
            auth_string = f'user={email_address}\x01auth=Bearer {access_token}\x01\x01'
            
            def get_auth(challenge):
                return auth_string.encode('utf-8')
            
            mail.authenticate('XOAUTH2', get_auth)
            
        elif provider == 'microsoft':
            # Microsoft IMAP XOAUTH2 format
            auth_string = f'user={email_address}\x01auth=Bearer {access_token}\x01\x01'
            
            def get_auth(challenge):
                return auth_string.encode('utf-8')
            
            mail.authenticate('XOAUTH2', get_auth)
        
        # Select inbox
        mail.select('INBOX')
        
        # Handle "first day" option
        if days == 'first':
            # Get ALL emails, take oldest 100
            status, messages = mail.search(None, 'ALL')
            if status != 'OK':
                return {'error': 'Failed to search emails'}
            email_ids = messages[0].split()
            if email_ids:
                email_ids = email_ids[:100]  # First 100 emails ever
            total_emails = len(email_ids)
            days_display = "first day"
        else:
            # Calculate date range
            days_int = int(days)
            since_date = (datetime.now() - timedelta(days=days_int)).strftime("%d-%b-%Y")
            
            # Search for emails in date range
            status, messages = mail.search(None, f'SINCE {since_date}')
            
            if status != 'OK':
                return {'error': 'Failed to search emails'}
            
            email_ids = messages[0].split()
            total_emails = len(email_ids)
            days_display = days_int
        
        # Apply limit
        if total_emails > MAX_EMAILS:
            email_ids = email_ids[-MAX_EMAILS:]  # Get most recent
            limited = True
        else:
            limited = False
        
        # Track senders
        sender_data = defaultdict(lambda: {
            'sender_name': '',
            'sender_email': '',
            'organization': '',
            'count': 0,
            'total_size': 0,
            'last_received': None,
            'read_count': 0,
            'unread_count': 0,
            'has_unsubscribe': False
        })
        
        # Process emails
        start_time = datetime.now()
        
        for idx, email_id in enumerate(email_ids):
            # Check timeout
            if (datetime.now() - start_time).seconds > MAX_TIME_SECONDS:
                break
                
            try:
                # FIX #1: Use BODY.PEEK[] to avoid marking as read
                status, msg_data = mail.fetch(email_id, '(BODY.PEEK[] FLAGS)')
                
                if status != 'OK':
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                email_msg = email.message_from_bytes(raw_email)
                
                # Get flags
                flags = msg_data[0][0].decode()
                is_read = '\\Seen' in flags
                
                # Extract sender info
                from_header = decode_mime_words(email_msg.get('From', ''))
                sender_name, sender_email = extract_sender_info(from_header)
                organization = get_organization(sender_email)
                
                # Get date
                date_header = email_msg.get('Date', '')
                try:
                    email_date = email.utils.parsedate_to_datetime(date_header)
                except:
                    email_date = datetime.now()
                
                # Get size (approximate)
                email_size = len(raw_email)
                
                # Check for unsubscribe
                has_unsubscribe = check_unsubscribe(email_msg)
                
                # Update sender data
                key = sender_email.lower()
                data = sender_data[key]
                data['sender_name'] = sender_name
                data['sender_email'] = sender_email
                data['organization'] = organization
                data['count'] += 1
                data['total_size'] += email_size
                
                if data['last_received'] is None or email_date > data['last_received']:
                    data['last_received'] = email_date
                
                if is_read:
                    data['read_count'] += 1
                else:
                    data['unread_count'] += 1
                
                if has_unsubscribe:
                    data['has_unsubscribe'] = True
                
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
        
        # Close connection
        mail.close()
        mail.logout()
        
        # Convert to list and calculate metrics
        results = []
        for sender_email, data in sender_data.items():
            total_count = data['count']
            unread_pct = (data['unread_count'] / total_count * 100) if total_count > 0 else 0
            
            # Nuisance score: sum of unread%, count, and size (MB)
            size_mb = data['total_size'] / (1024 * 1024)
            nuisance = unread_pct + total_count + size_mb
            
            results.append({
                'sender_name': data['sender_name'],
                'sender_email': sender_email,
                'organization': data['organization'],
                'count': total_count,
                'total_size': data['total_size'],
                'size_display': f"{size_mb:.2f} MB" if size_mb >= 1 else f"{data['total_size'] / 1024:.2f} KB",
                'last_received': data['last_received'].strftime('%Y-%m-%d %H:%M') if data['last_received'] else 'Unknown',
                'read_count': data['read_count'],
                'unread_count': data['unread_count'],
                'unread_pct': round(unread_pct, 1),
                'nuisance': round(nuisance, 2),
                'has_unsubscribe': data['has_unsubscribe']
            })
        
        # FIX #4: Filter out single emails in 1-day period
        if days == 1 or days == '1':
            results = [r for r in results if r['count'] > 1]
        
        # Sort by sender name (default)
        results.sort(key=lambda x: x['sender_name'].lower())
        
        response = {
            'success': True,
            'total_emails': total_emails,
            'senders': results,
            'days_analyzed': days_display,
            'test_mode': TEST_MODE
        }
        
        if limited:
            response['warning'] = f'Inbox has {total_emails} emails. Analyzed most recent {MAX_EMAILS}. Try shorter date range for complete analysis.'
        
        return response
        
    except imaplib.IMAP4.error as e:
        import traceback
        print(f"DEBUG: IMAP error details: {e}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return {'error': f'IMAP error: {str(e)}'}
    except Exception as e:
        import traceback
        print(f"DEBUG: Connection error details: {e}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return {'error': f'Connection error: {str(e)}'}

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/login/<provider>')
def login(provider):
    """Initiate OAuth flow for provider"""
    # Store days selection in session
    days = request.args.get('days', '1')
    session['days'] = days
    
    if provider == 'google':
        redirect_uri = url_for('google_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'microsoft':
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store state in memory (not session)
        if not hasattr(app, 'oauth_states'):
            app.oauth_states = {}
        app.oauth_states[state] = {'created': datetime.now()}
        
        # Build OAuth URL manually
        auth_url = (
            f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"client_id={os.getenv('MICROSOFT_CLIENT_ID')}"
            f"&response_type=code"
            f"&redirect_uri=http://localhost:5000/oauth/microsoft/callback"
            f"&scope=openid+email+profile+offline_access+https://outlook.office.com/IMAP.AccessAsUser.All+https://outlook.office.com/Mail.Read"
            f"&state={state}"
        )
        
        return redirect(auth_url)
    else:
        return jsonify({'error': 'Unknown provider'}), 400

@app.route('/oauth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        
        email_address = user_info.get('email')
        access_token = token.get('access_token')
        days = session.get('days', '1')
        
        # Store in session for analysis
        session['email'] = email_address
        session['access_token'] = access_token
        session['provider'] = 'google'
        session['days'] = days
        
        return render_template('analyzing.html', email=email_address, days=days)
        
    except Exception as e:
        return render_template('error.html', error=f'Authentication failed: {str(e)}')

@app.route('/oauth/microsoft/callback')
def microsoft_callback():
    """Handle Microsoft OAuth callback"""
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state from memory
    if not hasattr(app, 'oauth_states') or state not in app.oauth_states:
        return render_template('error.html', error='Invalid state - please try again')
    
    # Clean up state
    del app.oauth_states[state]
    
    try:
        # Exchange code for token manually
        import requests
        import jwt
        
        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        token_data = {
            'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
            'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
            'code': code,
            'redirect_uri': 'http://localhost:5000/oauth/microsoft/callback',
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token = token_response.json()
        
        # Get email from ID token instead of Graph API
        id_token = token.get('id_token')
        if id_token:
            # Decode without verification (just to read claims)
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            email_address = decoded.get('email') or decoded.get('preferred_username')
        else:
            email_address = None
        
        if not email_address:
            return render_template('error.html', error='Could not get email address from Microsoft')
        
        access_token = token['access_token']
        days = session.get('days', '1')
        
        # Store in session for analysis
        session['email'] = email_address
        session['access_token'] = access_token
        session['provider'] = 'microsoft'
        session['days'] = days
        session.modified = True
        
        return render_template('analyzing.html', email=email_address, days=days)
        
    except Exception as e:
        return render_template('error.html', error=f'Authentication failed: {str(e)}')

@app.route('/results')
def results():
    """Display analysis results"""
    email_address = session.get('email')
    access_token = session.get('access_token')
    provider = session.get('provider')
    days = session.get('days', '1')
    
    if not email_address or not access_token:
        return redirect(url_for('index'))
    
    # Perform analysis
    result = analyze_emails_oauth(email_address, access_token, provider, days)
    
    if result.get('error'):
        return render_template('error.html', error=result['error'])
    
    # Generate user-friendly period label
    if days == 'first':
        period_label = "First Day Ever"
    elif days == '1' or days == 1:
        period_label = "Last 1 Day"
    elif days == '7' or days == 7:
        period_label = "Last 7 Days"
    else:
        period_label = f"Last {days} Days"
    
    # Render results using the results template
    return render_template('results.html', 
                         total_emails=result['total_emails'],
                         total_senders=len(result['senders']),
                         days_analyzed=result['days_analyzed'],
                         period_label=period_label,
                         senders=result['senders'],
                         warning=result.get('warning'),
                         test_mode=result.get('test_mode', False),
                         features=FEATURES)

@app.route('/action/create-folder', methods=['POST'])
def action_create_folder():
    """Handle Create Folder action"""
    
    # Check if feature is enabled
    if not is_action_enabled('create_folder'):
        return jsonify({'success': False, 'message': 'Create Folder feature is not enabled'})
    
    # Get session data
    email_address = session.get('email')
    access_token = session.get('access_token')
    provider = session.get('provider')
    
    if not email_address or not access_token:
        return jsonify({'success': False, 'message': 'Not authenticated. Please log in again.'})
    
    # Get request data
    data = request.get_json()
    sender_email = data.get('sender_email')
    folder_name = data.get('folder_name')
    
    if not sender_email or not folder_name:
        return jsonify({'success': False, 'message': 'Missing sender_email or folder_name'})
    
    print(f"DEBUG: Create folder action for {sender_email} -> {folder_name}")
    
    try:
        # Determine IMAP server
        if provider == 'google':
            imap_server = 'imap.gmail.com'
        elif provider == 'microsoft':
            imap_server = 'imap-mail.outlook.com'
        else:
            return jsonify({'success': False, 'message': 'Unknown provider'})
        
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        
        # Authenticate
        auth_string = f'user={email_address}\x01auth=Bearer {access_token}\x01\x01'
        
        def get_auth(challenge):
            return auth_string.encode('utf-8')
        
        mail.authenticate('XOAUTH2', get_auth)
        
        # Execute create folder action
        result = EmailActions.create_folder(mail, sender_email, folder_name, provider)
        
        # Try to create email rule (will inform user if not possible via IMAP)
        rule_result = EmailActions.create_email_rule(mail, sender_email, folder_name, provider)
        
        # Close connection
        mail.close()
        mail.logout()
        
        # Combine results
        response = {
            'success': result['success'],
            'message': result['message'],
            'emails_moved': result.get('emails_moved', 0),
            'folder_created': result.get('folder_created'),
            'rule_created': rule_result['success'],
            'rule_message': rule_result['message'],
            'manual_instructions': rule_result.get('manual_instructions')
        }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        print(f"DEBUG: Error in create_folder action: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def open_browser():
    """Open browser after short delay"""
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Open browser after 1 second
    Timer(1, open_browser).start()
    
    # Run Flask app
    print("🔍 Email Scraper starting...")
    print("📧 Privacy-first inbox analysis with OAuth")
    print("🌐 Opening browser at http://127.0.0.1:5000")
    if TEST_MODE:
        print("⚠️  TEST MODE: Read-only analysis")
    
    app.run(debug=False, host='127.0.0.1', port=5000)
