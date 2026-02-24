#!/usr/bin/env python3
"""
Email Scraper - HERD-principled inbox analysis tool
Privacy-first, value-first, honor-based payment
OAuth 2.0 implementation for frictionless authentication
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
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
from gmail_api import GmailAPI

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'null'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Test mode flag
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

# Resource limits
MAX_EMAILS = int(os.getenv('MAX_EMAILS', '5000'))
MAX_TIME_SECONDS = int(os.getenv('MAX_TIME_SECONDS', '300'))

# Initialize OAuth
oauth = OAuth(app)

# Microsoft Scopes (Graph API only - no IMAP)
MICROSOFT_SCOPES = 'openid email profile offline_access https://graph.microsoft.com/User.Read https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/MailboxSettings.ReadWrite'
def execute_email_action(action_name, provider, access_token, **kwargs):
    """
    Execute an email action with provider-specific logic
    
    Args:
        action_name: 'create_folder', 'delete_all', 'cleanup_history', etc.
        provider: 'google' or 'microsoft'
        access_token: OAuth token
        **kwargs: Action-specific parameters
    
    Returns:
        dict: Action result
    """
    if provider == 'google':
        gmail = GmailAPI(access_token)
        
        if action_name == 'create_folder':
            return gmail.create_folder(kwargs['sender_emails'], kwargs['folder_name'])
        elif action_name == 'cleanup_history':
            return gmail.Clean_up_history(
                kwargs['sender_emails'],
                kwargs['folder_name'],
                kwargs['keep_days'],
                kwargs['archive_days'],
                kwargs['delete_days'],
                kwargs['preview_only']
            )
        elif action_name == 'delete_all':
            return gmail.delete_all(kwargs['sender_emails'], kwargs.get('create_filter', False))
        elif action_name == 'archive':
            return gmail.archive_emails(kwargs['sender_emails'], kwargs.get('create_filter', False))
        else:
            return {'success': False, 'message': f'Unknown action: {action_name}'}
        
    elif provider == 'microsoft':
        if action_name == 'create_folder':
            return EmailActions.create_folder_microsoft(
                access_token,
                kwargs['sender_emails'],
                kwargs['folder_name']
            )
        elif action_name == 'cleanup_history':
            return EmailActions.cleanup_history_microsoft(
                access_token,
                kwargs['sender_emails'],
                kwargs['keep_days'],
                kwargs['archive_days'],
                kwargs['delete_days'],
                kwargs['preview_only']
            )

        elif action_name == 'delete_all':
            return EmailActions.delete_all_microsoft(
                access_token, 
                kwargs['sender_emails'],
                kwargs.get('create_filter', False)
            )
        elif action_name == 'archive':
            return EmailActions.archive_microsoft(
                access_token, 
                kwargs['sender_emails'],
                kwargs.get('create_filter', False)
            )

        else:
            return {'success': False, 'message': f'Unknown action: {action_name}'}
    
    else:
        return {'success': False, 'message': f'Unsupported provider: {provider}'}

# Google OAuth configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://mail.google.com/ https://www.googleapis.com/auth/gmail.settings.basic',
        'access_type': 'offline',
        'prompt': 'consent select_account'
    }
)

# Microsoft OAuth configuration (Graph API only)
microsoft = oauth.register(
    name='microsoft',
    client_id=os.getenv('MICROSOFT_CLIENT_ID'),
    client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    jwks_uri='https://login.microsoftonline.com/common/discovery/v2.0/keys',
    client_kwargs={
        'scope': MICROSOFT_SCOPES,
        'token_endpoint_auth_method': 'client_secret_post',
        'code_challenge_method': None,
        'prompt': 'select_account' 
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

def check_unsubscribe_header(headers):
    """Check if email has unsubscribe link in headers"""
    # Check for List-Unsubscribe header
    for header in headers:
        if header.get('name', '').lower() == 'list-unsubscribe':
            return True
    return False

def analyze_emails_oauth(email_address, access_token, provider, days):
    """Analyze emails using Gmail API (Google) or Graph API (Microsoft)"""
    
    try:
        # Use Gmail API for Google
        if provider == 'google':
            
            # Initialize Gmail API
            gmail = GmailAPI(access_token)
            
            # List messages
            messages = gmail.list_messages(days=days, max_results=MAX_EMAILS)
            total_emails = len(messages)
            
            if days == 'first':
                days_display = "first day"
            else:
                days_display = int(days)
            
            limited = total_emails >= MAX_EMAILS
            
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
            
            # Process messages
            start_time = datetime.now()
            
            for idx, msg in enumerate(messages):
                # Check timeout
                if (datetime.now() - start_time).seconds > MAX_TIME_SECONDS:
                    break
                
                try:
                    # Get message details
                    details = gmail.get_message_details(msg['id'])
                    if not details:
                        continue
                    
                    sender_email = details['sender_email']
                    sender_name = details['sender_name']
                    organization = get_organization(sender_email)
                    
                    # Update sender data
                    key = sender_email.lower()
                    data = sender_data[key]
                    data['sender_name'] = sender_name
                    data['sender_email'] = sender_email
                    data['organization'] = organization
                    data['count'] += 1
                    data['total_size'] += details['size']
                    
                    if data['last_received'] is None or details['date_received'] > data['last_received']:
                        data['last_received'] = details['date_received']
                    
                    if details['is_unread']:
                        data['unread_count'] += 1
                    else:
                        data['read_count'] += 1
                    
                    if details['has_unsubscribe']:
                        data['has_unsubscribe'] = True
                    
                except Exception as e:
                    print(f"DEBUG: Error processing message {msg.get('id')}: {e}")
                    continue
        
        # Use Graph API for Microsoft
        elif provider == 'microsoft':
            print(f"DEBUG: Using Graph API for Microsoft analysis, {days} days")
            
            import requests
            
            graph_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Calculate date range
            if days == 'first':
                # Get oldest 100 emails
                messages_url = f"{graph_url}/mailFolders/inbox/messages?$top=100&$orderby=receivedDateTime asc&$select=id,from,subject,receivedDateTime,isRead,hasAttachments,internetMessageHeaders"
                days_display = "first day"
            else:
                days_int = int(days)
                since_date = (datetime.utcnow() - timedelta(days=days_int)).strftime('%Y-%m-%dT%H:%M:%SZ')
                messages_url = f"{graph_url}/mailFolders/inbox/messages?$filter=receivedDateTime ge {since_date}&$top=999&$select=id,from,subject,receivedDateTime,isRead,hasAttachments,internetMessageHeaders"
                days_display = days_int
            
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
            
            # Fetch messages with pagination
            all_messages = []
            start_time = datetime.now()
            
            while messages_url:
                # Check timeout
                if (datetime.now() - start_time).seconds > MAX_TIME_SECONDS:
                    break
                    
                response = requests.get(messages_url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"DEBUG: Graph API error: {response.status_code}")
                    print(f"DEBUG: Response: {response.text}")
                    return {'error': f'Graph API error: {response.status_code}'}
                
                data = response.json()
                messages = data.get('value', [])
                all_messages.extend(messages)
                
                # Check for next page
                messages_url = data.get('@odata.nextLink')
                
                # Apply limit
                if len(all_messages) >= MAX_EMAILS:
                    all_messages = all_messages[:MAX_EMAILS]
                    break
            
            total_emails = len(all_messages)
            limited = len(all_messages) >= MAX_EMAILS
            
            # Process messages
            for msg in all_messages:
                try:
                    # Extract sender info
                    from_data = msg.get('from', {}).get('emailAddress', {})
                    sender_email = from_data.get('address', 'unknown@unknown.com')
                    sender_name = from_data.get('name', sender_email.split('@')[0])
                    organization = get_organization(sender_email)
                    
                    # Get date
                    received_str = msg.get('receivedDateTime', '')
                    try:
                        email_date = datetime.strptime(received_str, '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        email_date = datetime.utcnow()
                    
                    # Check read status
                    is_read = msg.get('isRead', False)
                    
                    # Check for unsubscribe
                    headers = msg.get('internetMessageHeaders', [])
                    has_unsubscribe = check_unsubscribe_header(headers)
                    
                    # Estimate size (Graph API doesn't provide size in list view)
                    # Rough estimate: 5KB per email
                    email_size = 5 * 1024
                    
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
                    print(f"DEBUG: Error processing message: {e}")
                    continue
        
        else:
            return {'error': 'Unknown provider'}
        
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
        
    except Exception as e:
        import traceback
        print(f"Error analyzing emails: {e}")
        print(traceback.format_exc())
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/<provider>')
def login(provider):
    """Initiate OAuth login for the selected provider"""
    days = request.args.get('days', '7')
    
    # Store days in session for later
    session['days'] = days
    
    if provider == 'google':
        redirect_uri = url_for('google_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'microsoft':
        redirect_uri = url_for('microsoft_callback', _external=True)
        return microsoft.authorize_redirect(redirect_uri)
    else:
        return "Unknown provider", 400

@app.route('/oauth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get token
        token = google.authorize_access_token()
        
        # Get user info
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()
        
        # Store in session
        session['email'] = user_info['email']
        session['provider'] = 'google'
        session['access_token'] = token['access_token']
        
        # Get days from session
        days = session.get('days', '7')
        
        return render_template('analyzing.html', email=user_info['email'], days=days)
        
    except Exception as e:
        print(f"Error in Google OAuth: {e}")
        return f"Authentication failed: {str(e)}", 400

@app.route('/oauth/microsoft/callback')
def microsoft_callback():
    """Handle Microsoft OAuth callback"""
    try:
        # Get token
        token = microsoft.authorize_access_token()
        
        # Get user info
        resp = microsoft.get('https://graph.microsoft.com/v1.0/me')
        print(f"DEBUG callback: Response status: {resp.status_code}")
        print(f"DEBUG callback: Response text: {resp.text}")
        user_info = resp.json()
        print(f"DEBUG callback: Full user_info dict: {user_info}")
        print(f"DEBUG callback: User info: {user_info.get('mail') or user_info.get('userPrincipalName')}")

        # Store in session
        email_address = user_info.get('mail') or user_info.get('userPrincipalName')
        session['email'] = email_address
        session['provider'] = 'microsoft'
        session['access_token'] = token['access_token']
        
        # Get days from session
        days = session.get('days', '7')
        print(f"DEBUG callback: Session stored - email={session.get('email')}, provider={session.get('provider')}")
        
        print(f"DEBUG callback: Days={days}")
        return render_template('analyzing.html', email=email_address, days=days)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in Microsoft OAuth: {e}")
        print(error_details)
        return f"Authentication failed: {str(e)}", 400

@app.route('/results')
def results():
    """Show analysis results"""
    email_address = session.get('email')
    access_token = session.get('access_token')
    provider = session.get('provider')

    days = session.get('days', '7')

    print(f"DEBUG /results: email={email_address}, provider={provider}, days={days}")
    print(f"DEBUG /results: has token={bool(access_token)}")
    
    if not email_address or not access_token:
        return redirect(url_for('index'))
    
    # Perform analysis
    analysis_result = analyze_emails_oauth(email_address, access_token, provider, days)
    
    if 'error' in analysis_result:
        return render_template('error.html', error=analysis_result['error'])
    
    # Get enabled actions for template
    enabled_actions = get_enabled_actions()
    
    return render_template('results.html', 
                         email=email_address,
                         provider=provider,
                         days=days,
                         total_emails=analysis_result.get('total_emails', 0),
                         senders=analysis_result.get('senders', []),
                         warning=analysis_result.get('warning'),
                         test_mode=TEST_MODE,
                         enabled_actions=enabled_actions,
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
    sender_emails = data.get('sender_emails', [])
    folder_name = data.get('folder_name')
    
    # Support both single sender (legacy) and multiple senders
    if not sender_emails:
        single_sender = data.get('sender_email')
        if single_sender:
            sender_emails = [single_sender]
    
    if not sender_emails or not folder_name:
        return jsonify({'success': False, 'message': 'Missing sender_emails or folder_name'})
    
    try:
        # Use helper function for both providers
        result = execute_email_action(
            'create_folder',
            provider,
            access_token,
            sender_emails=sender_emails,
            folder_name=folder_name
        )
        
        filters_created = result.get('filters_created', 0)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'emails_moved': result.get('emails_moved', 0),
            'failed_count': result.get('failed_count', 0),
            'folder_created': result.get('folder_created'),
            'rule_created': filters_created > 0,
            'rule_message': f'Created {filters_created} filter(s)/rule(s)' if filters_created > 0 else 'No filters/rules created',
            'filters_created': filters_created
        })
    
    except Exception as e:
        import traceback
        print(f"DEBUG: Error in create_folder action: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
@app.route('/action/clean_up_history', methods=['POST'])
def action_clean_up_history():
    """Handle Clean_up History action"""
    
    # Check if feature is enabled
    if not is_action_enabled('Cleanup_history'):
        return jsonify({'success': False, 'message': 'Cleanup History feature is not enabled'})
    
    # Get session data
    email_address = session.get('email')
    access_token = session.get('access_token')
    provider = session.get('provider')
    
    if not email_address or not access_token:
        return jsonify({'success': False, 'message': 'Not authenticated. Please log in again.'})
    
    # Get request data
    data = request.get_json()
    sender_emails = data.get('sender_emails', [])
    folder_name = data.get('folder_name')
    keep_days = data.get('keep_days')
    archive_days = data.get('archive_days')
    delete_days = data.get('delete_days')
    preview_only = data.get('preview_only', False)
    
    if not sender_emails or not folder_name:
        return jsonify({'success': False, 'message': 'Missing required parameters'})
    
    if keep_days is None or archive_days is None or delete_days is None:
        return jsonify({'success': False, 'message': 'Missing date period parameters'})
    
    try:
        keep_days = int(keep_days)
        archive_days = int(archive_days)
        delete_days = int(delete_days)
    except ValueError:
        return jsonify({'success': False, 'message': 'Date periods must be numbers'})
    
    # Validate logic: keep < archive < delete
    if not (keep_days < archive_days <= delete_days):
        return jsonify({'success': False, 'message': 'Invalid date periods: keep < archive <= delete'})
        
    try:
        # Use helper function for both providers
        result = execute_email_action(
            'cleanup_history',
            provider,
            access_token,
            sender_emails=sender_emails,
            folder_name=folder_name,
            keep_days=keep_days,
            archive_days=archive_days,
            delete_days=delete_days,
            preview_only=preview_only
        )
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def open_browser():
    """Open browser after short delay"""
    webbrowser.open('http://localhost:5000')


@app.route('/api/storage-info', methods=['GET'])
def get_storage_info():
    """Get storage information for current user"""
    
    email_address = session.get('email')
    access_token = session.get('access_token')
    provider = session.get('provider')
    
    if not email_address or not access_token:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        if provider == 'google':
            gmail = GmailAPI(access_token)
            result = gmail.get_storage_info()
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': 'Storage info only available for Google'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/action/delete_all', methods=['POST'])
def delete_all():
    """Delete all emails from selected senders"""
    if not is_action_enabled('delete_all'):
        return jsonify({'error': 'Delete All feature is not enabled'}), 403
    
    data = request.json
    sender_emails = data.get('sender_emails', [])
    create_filter = data.get('create_filter', False)
    
    if not sender_emails:
        return jsonify({'error': 'No senders selected'}), 400
    
    provider = session.get('provider')
    access_token = session.get('access_token')
    
    # Use helper function
    result = execute_email_action(
        'delete_all',
        provider,
        access_token,
        sender_emails=sender_emails,
        create_filter=create_filter
    )
    
    return jsonify(result)

@app.route('/action/archive', methods=['POST'])
def archive():
    """Archive all emails from selected senders"""
    if not is_action_enabled('archive'):
        return jsonify({'error': 'Archive feature is not enabled'}), 403
    
    data = request.json
    sender_emails = data.get('sender_emails', [])
    create_filter = data.get('create_filter', False)
    
    if not sender_emails:
        return jsonify({'error': 'No senders selected'}), 400
    
    provider = session.get('provider')
    access_token = session.get('access_token')
    
    # Use helper function
    result = execute_email_action(
        'archive',
        provider,
        access_token,
        sender_emails=sender_emails,
        create_filter=create_filter
    )
    
    return jsonify(result)

if __name__ == '__main__':
    # Open browser after 1 second
    Timer(1, open_browser).start()
    
    # Run Flask app
    print("🔍 Email Scraper starting...")
    print("🌐 Opening browser at http://localhost:5000")
    if TEST_MODE:
        print("⚠️  TEST MODE: Read-only analysis")
    
    app.run(debug=False, host='localhost', port=5000)