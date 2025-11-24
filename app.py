#!/usr/bin/env python3
"""
Email Scraper - HERD-principled inbox analysis tool
Privacy-first, value-first, honor-based payment
"""

from flask import Flask, render_template, request, jsonify
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from collections import defaultdict
import re
import webbrowser
from threading import Timer

app = Flask(__name__)

# IMAP server configurations
IMAP_SERVERS = {
    'gmail.com': 'imap.gmail.com',
    'outlook.com': 'imap-mail.outlook.com',
    'hotmail.com': 'imap-mail.outlook.com',
    'hotmail.co.uk': 'imap-mail.outlook.com',
    'live.com': 'imap-mail.outlook.com'
}

def get_imap_server(email_address):
    """Determine IMAP server from email address"""
    domain = email_address.split('@')[1].lower()
    return IMAP_SERVERS.get(domain, f'imap.{domain}')

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
                if re.search(r'unsubscribe', body, re.IGNORECASE):
                    return True
    except:
        pass
    
    return False

def analyze_emails(email_address, password, days=1):
    """Connect to IMAP and analyze emails"""
    
    try:
        # Connect to IMAP server
        imap_server = get_imap_server(email_address)
        mail = imaplib.IMAP4_SSL(imap_server)
        
        # Login
        mail.login(email_address, password)
        
        # Select inbox
        mail.select('INBOX')
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        
        # Search for emails in date range
        status, messages = mail.search(None, f'SINCE {since_date}')
        
        if status != 'OK':
            return {'error': 'Failed to search emails'}
        
        email_ids = messages[0].split()
        
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
        
        total_emails = len(email_ids)
        
        # Process emails
        for idx, email_id in enumerate(email_ids):
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822 FLAGS)')
                
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
        
        # Sort by sender name (default)
        results.sort(key=lambda x: x['sender_name'].lower())
        
        return {
            'success': True,
            'total_emails': total_emails,
            'senders': results,
            'days_analyzed': days
        }
        
    except imaplib.IMAP4.error as e:
        return {'error': f'IMAP error: {str(e)}. Check your email and password.'}
    except Exception as e:
        return {'error': f'Connection error: {str(e)}'}

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze emails endpoint"""
    data = request.get_json()
    
    email_address = data.get('email')
    password = data.get('password')
    days = int(data.get('days', 1))
    
    if not email_address or not password:
        return jsonify({'error': 'Email and password required'})
    
    # Validate days (1-7 max)
    if days < 1 or days > 7:
        days = 1
    
    result = analyze_emails(email_address, password, days)
    return jsonify(result)

def open_browser():
    """Open browser after short delay"""
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Open browser after 1 second
    Timer(1, open_browser).start()
    
    # Run Flask app
    print("🔍 Email Scraper starting...")
    print("📧 Privacy-first inbox analysis")
    print("🌐 Opening browser at http://127.0.0.1:5000")
    
    app.run(debug=False, host='127.0.0.1', port=5000)
