"""
Gmail API Module
Handles Gmail-specific operations using Gmail API instead of IMAP
IMAP is unreliable for Gmail label/folder operations
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class GmailAPI:
    """Gmail API wrapper for reliable label/folder operations"""
    
    def __init__(self, access_token):
        """
        Initialize Gmail API service
        
        Args:
            access_token: OAuth2 access token with gmail.modify scope
        """
        # Create credentials from access token
        self.credentials = Credentials(token=access_token)
        
        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def create_label(self, label_name):
        """
        Create a new Gmail label
        
        Args:
            label_name: Name of label to create
            
        Returns:
            dict: {'success': bool, 'label_id': str, 'message': str}
        """
        try:
            # Check if label already exists
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    print(f"DEBUG: Label '{label_name}' already exists with ID: {label['id']}")
                    return {
                        'success': True,
                        'label_id': label['id'],
                        'message': f"Label '{label_name}' already exists"
                    }
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            print(f"DEBUG: Created label '{label_name}' with ID: {created_label['id']}")
            
            return {
                'success': True,
                'label_id': created_label['id'],
                'message': f"Created label '{label_name}'"
            }
            
        except Exception as e:
            print(f"DEBUG: Error creating label: {e}")
            return {
                'success': False,
                'label_id': None,
                'message': f"Error creating label: {str(e)}"
            }
    
    def search_messages(self, sender_email):
        """
        Search for all messages from a specific sender (in any location)
        
        Args:
            sender_email: Email address to search for
            
        Returns:
            list: Message IDs
        """
        try:
            # Search ALL locations (inbox, labels, archive) - not just inbox
            query = f'from:{sender_email}'
            print(f"DEBUG: Searching for messages from: {sender_email} (in all locations)")
            
            all_messages = []
            page_token = None
            
            while True:
                # Search with pagination
                # includeSpamTrash=False means we skip spam/trash but search everywhere else
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    includeSpamTrash=False,  # Don't search spam/trash
                    pageToken=page_token
                ).execute()
                
                messages = results.get('messages', [])
                all_messages.extend(messages)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            message_ids = [msg['id'] for msg in all_messages]
            print(f"DEBUG: Found {len(message_ids)} messages from {sender_email} (searched all locations)")
            
            return message_ids
            
        except Exception as e:
            print(f"DEBUG: Error searching messages: {e}")
            return []
    
    def list_messages(self, days=7, max_results=1000):
        """
        List messages from inbox within date range
        
        Args:
            days: Number of days to look back (or 'first' for oldest 100)
            max_results: Maximum number of messages to return
            
        Returns:
            list: Message IDs with metadata
        """
        try:
            # Build query based on days
            if days == 'first':
                # Get oldest 100 messages
                query = ''
                max_results = 100
                print(f"DEBUG: Listing first {max_results} messages (oldest)")
            else:
                # Calculate date for query
                from datetime import datetime, timedelta
                days_int = int(days)
                since_date = datetime.now() - timedelta(days=days_int)
                # Gmail API uses format: after:YYYY/MM/DD
                date_str = since_date.strftime('%Y/%m/%d')
                query = f'after:{date_str}'
                print(f"DEBUG: Listing messages after {date_str}")
            
            all_messages = []
            page_token = None
            
            while len(all_messages) < max_results:
                # List messages with pagination
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=min(500, max_results - len(all_messages)),  # API max is 500 per page
                    pageToken=page_token,
                    includeSpamTrash=False
                ).execute()
                
                messages = results.get('messages', [])
                if not messages:
                    break
                
                all_messages.extend(messages)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                
                # If we're getting "first" emails, stop after first page
                if days == 'first':
                    break
            
            # Limit to max_results
            if len(all_messages) > max_results:
                all_messages = all_messages[:max_results]
            
            print(f"DEBUG: Found {len(all_messages)} messages")
            
            return all_messages
            
        except Exception as e:
            print(f"DEBUG: Error listing messages: {e}")
            return []
    
    def get_message_details(self, message_id):
        """
        Get detailed information about a specific message
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            dict: Message details (sender, date, subject, flags, size, etc.)
        """
        try:
            # Get message with metadata and headers
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',  # Just headers, not full body
                metadataHeaders=['From', 'To', 'Subject', 'Date', 'List-Unsubscribe']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            # Parse sender info
            from_header = headers.get('From', '')
            sender_name, sender_email = self._parse_sender(from_header)
            
            # Get flags/labels
            labels = message.get('labelIds', [])
            is_unread = 'UNREAD' in labels
            
            # Get date
            internal_date = int(message.get('internalDate', 0))
            from datetime import datetime
            date_received = datetime.fromtimestamp(internal_date / 1000)
            
            # Get size
            size_estimate = message.get('sizeEstimate', 0)
            
            # Check for unsubscribe header
            has_unsubscribe = bool(headers.get('List-Unsubscribe'))
            
            return {
                'message_id': message_id,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'subject': headers.get('Subject', ''),
                'date_received': date_received,
                'is_unread': is_unread,
                'size': size_estimate,
                'has_unsubscribe': has_unsubscribe
            }
            
        except Exception as e:
            print(f"DEBUG: Error getting message {message_id}: {e}")
            return None
    
    def _parse_sender(self, from_header):
        """
        Parse sender name and email from From header
        
        Args:
            from_header: Email From header (e.g. "John Doe <john@example.com>")
            
        Returns:
            tuple: (sender_name, sender_email)
        """
        import re
        
        # Pattern: "Name" <email@domain.com> or Name <email@domain.com> or just email@domain.com
        match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>$', from_header.strip())
        if match:
            name = match.group(1).strip()
            email = match.group(2).strip().lower()
            return (name, email)
        
        # Just email address
        match = re.match(r'^([^\s@]+@[^\s@]+)$', from_header.strip())
        if match:
            email = match.group(1).strip().lower()
            return (email, email)
        
        # Fallback
        return (from_header, from_header.lower())
    
    def move_messages_to_label(self, message_ids, label_id, remove_from_inbox=True):
        """
        Move messages to a label (and optionally remove from inbox)
        
        Args:
            message_ids: List of message IDs to move
            label_id: Target label ID
            remove_from_inbox: Whether to remove from INBOX
            
        Returns:
            dict: {'success': bool, 'moved_count': int, 'message': str}
        """
        try:
            if not message_ids:
                return {
                    'success': True,
                    'moved_count': 0,
                    'message': 'No messages to move'
                }
            
            print(f"DEBUG: Moving {len(message_ids)} messages to label {label_id}")
            
            moved_count = 0
            failed_count = 0
            
            # Gmail API supports batch modifications
            # For now, we'll do them individually with error handling
            for message_id in message_ids:
                try:
                    modify_body = {
                        'addLabelIds': [label_id]
                    }
                    
                    if remove_from_inbox:
                        modify_body['removeLabelIds'] = ['INBOX']
                    
                    self.service.users().messages().modify(
                        userId='me',
                        id=message_id,
                        body=modify_body
                    ).execute()
                    
                    moved_count += 1
                    
                    # Log progress every 50 messages
                    if moved_count % 50 == 0:
                        print(f"DEBUG: Progress: {moved_count}/{len(message_ids)} messages moved")
                    
                except Exception as e:
                    print(f"DEBUG: Failed to move message {message_id}: {e}")
                    failed_count += 1
                    continue
            
            print(f"DEBUG: Moved {moved_count}/{len(message_ids)} messages (failed: {failed_count})")
            
            return {
                'success': True,
                'moved_count': moved_count,
                'failed_count': failed_count,
                'message': f"Moved {moved_count} messages to label"
            }
            
        except Exception as e:
            print(f"DEBUG: Error moving messages: {e}")
            return {
                'success': False,
                'moved_count': 0,
                'message': f"Error: {str(e)}"
            }
    
    def create_folder_and_move(self, sender_emails, folder_name):
        """
        Complete operation: create label and move all emails from senders
        
        Args:
            sender_emails: List of sender email addresses
            folder_name: Name of label/folder to create
            
        Returns:
            dict: {'success': bool, 'message': str, 'emails_moved': int, 'folder_created': str}
        """
        try:
            # Support both single sender and list
            if isinstance(sender_emails, str):
                sender_emails = [sender_emails]
            
            # Create label
            label_result = self.create_label(folder_name)
            if not label_result['success']:
                return {
                    'success': False,
                    'message': label_result['message'],
                    'emails_moved': 0,
                    'folder_created': None
                }
            
            label_id = label_result['label_id']
            
            # Search and move messages for each sender
            total_moved = 0
            total_failed = 0
            
            for sender_email in sender_emails:
                message_ids = self.search_messages(sender_email)
                
                if message_ids:
                    move_result = self.move_messages_to_label(
                        message_ids,
                        label_id,
                        remove_from_inbox=True
                    )
                    total_moved += move_result.get('moved_count', 0)
                    total_failed += move_result.get('failed_count', 0)
            
            # Create filters for future emails from each sender
            filters_created = 0
            for sender_email in sender_emails:
                try:
                    filter_result = self.create_gmail_filter(sender_email, label_id)
                    if filter_result:
                        filters_created += 1
                        print(f"DEBUG: Created filter for {sender_email}")
                except Exception as e:
                    print(f"DEBUG: Failed to create filter for {sender_email}: {e}")
                    # Don't fail the whole operation if filter creation fails
                    continue
            
            return {
                'success': True,
                'message': f"Successfully moved {total_moved} emails to {folder_name}",
                'emails_moved': total_moved,
                'failed_count': total_failed,
                'folder_created': folder_name,
                'label_id': label_id,
                'filters_created': filters_created
            }
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in create_folder_and_move: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'emails_moved': 0,
                'folder_created': None
            }
