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
                # Get oldest 100 messages - need to search all then sort
                query = f'in:inbox'
                max_results = 100
                print(f"DEBUG: Listing first {max_results} messages (oldest)")
                
                # For "first day", we need to get ALL message IDs first, then take oldest
                # Gmail API doesn't have a "sort by oldest" parameter directly
                # So we'll get messages and reverse the list (newest first by default)
                all_msg_ids = []
                page_token = None
                
                # Get all message IDs (just IDs, very fast)
                while True:
                    results = self.service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=500,
                        pageToken=page_token,
                        includeSpamTrash=False
                    ).execute()
                    
                    messages = results.get('messages', [])
                    if not messages:
                        break
                    
                    all_msg_ids.extend(messages)
                    
                    page_token = results.get('nextPageToken')
                    if not page_token:
                        break
                
                # Reverse to get oldest first, then take first 100
                all_msg_ids.reverse()
                all_messages = all_msg_ids[:100] if len(all_msg_ids) > 100 else all_msg_ids
                
                print(f"DEBUG: Found {len(all_messages)} oldest messages out of {len(all_msg_ids)} total")
                
                return all_messages
                
            else:
                # Calculate date for query
                from datetime import datetime, timedelta
                days_int = int(days)
                since_date = datetime.now() - timedelta(days=days_int)
                # Gmail API uses format: after:YYYY/MM/DD
                date_str = since_date.strftime('%Y/%m/%d')
                query = f'in:inbox after:{date_str}'
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
    
    def create_gmail_filter(self, sender_email, label_id):
        """
        Create Gmail filter to auto-label future emails from sender
        
        Args:
            sender_email: Email address to filter
            label_id: Label ID to apply
            
        Returns:
            dict: Filter details if successful, None if failed
        """
        try:
            filter_content = {
                'criteria': {
                    'from': sender_email
                },
                'action': {
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            }
            
            created_filter = self.service.users().settings().filters().create(
                userId='me',
                body=filter_content
            ).execute()
            
            print(f"DEBUG: Created filter for {sender_email} (filter ID: {created_filter.get('id')})")
            
            return created_filter
            
        except Exception as e:
            print(f"DEBUG: Error creating filter for {sender_email}: {e}")
            return None
    
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
    
    def Clean_up_history(self, sender_emails, folder_name, keep_days, archive_days, delete_days, preview_only=False):
        """
        Clean_up email retention for selected senders with three-tier policy
        
        Args:
            sender_emails: List of sender email addresses
            folder_name: Base folder name (will create Archive-{folder_name})
            keep_days: Days to keep in inbox (e.g., 7)
            archive_days: Days to keep in archive before delete (e.g., 60)
            delete_days: Days after which to delete (e.g., 60+)
            preview_only: If True, only return counts without taking action
            
        Returns:
            dict: {
                'success': bool,
                'preview': {
                    'keep_count': int,
                    'archive_count': int,
                    'delete_count': int
                },
                'executed': {
                    'archived': int,
                    'deleted': int
                } if not preview_only
            }
        """
        from datetime import datetime, timedelta
        
        try:
            # Support single sender
            if isinstance(sender_emails, str):
                sender_emails = [sender_emails]
            
            # Calculate date boundaries
            now = datetime.now()
            keep_cutoff = now - timedelta(days=keep_days)
            archive_cutoff = now - timedelta(days=archive_days)
            delete_cutoff = now - timedelta(days=delete_days)
            
            print(f"DEBUG: Clean-up History - Keep: {keep_days}d, Archive: {archive_days}d, Delete: {delete_days}d")
            print(f"DEBUG: Date boundaries - Keep after: {keep_cutoff.strftime('%Y/%m/%d')}, Delete before: {delete_cutoff.strftime('%Y/%m/%d')}")
            
            # Collect message IDs by category
            keep_messages = []
            archive_messages = []
            delete_messages = []
            
            for sender_email in sender_emails:
                print(f"DEBUG: Processing sender: {sender_email}")
                
                # Get ALL messages from sender
                all_messages = self.search_messages(sender_email)
                
                # Categorize by date
                for msg_id in all_messages:
                    try:
                        # Get message date
                        msg = self.service.users().messages().get(
                            userId='me',
                            id=msg_id,
                            format='minimal',
                            fields='internalDate'
                        ).execute()
                        
                        msg_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                        
                        # Categorize
                        if msg_date >= keep_cutoff:
                            # Recent - keep in inbox
                            keep_messages.append(msg_id)
                        elif msg_date >= delete_cutoff:
                            # Middle age - archive
                            archive_messages.append(msg_id)
                        else:
                            # Old - delete
                            delete_messages.append(msg_id)
                    
                    except Exception as e:
                        print(f"DEBUG: Error checking message {msg_id}: {e}")
                        continue
            
            preview = {
                'keep_count': len(keep_messages),
                'archive_count': len(archive_messages),
                'delete_count': len(delete_messages)
            }
            
            print(f"DEBUG: Preview - Keep: {preview['keep_count']}, Archive: {preview['archive_count']}, Delete: {preview['delete_count']}")
            
            # If preview only, return counts
            if preview_only:
                return {
                    'success': True,
                    'preview': preview,
                    'message': f"Found {preview['keep_count']} to keep, {preview['archive_count']} to archive, {preview['delete_count']} to delete"
                }
            
            # Execute moves/deletes
            archived_count = 0
            deleted_count = 0
            
            # 1. Archive emails (if any)
            if archive_messages:
                archive_label_name = f"Archive-{folder_name}"
                
                # Create archive label
                label_result = self.create_label(archive_label_name)
                if not label_result['success']:
                    return {
                        'success': False,
                        'message': f"Failed to create archive label: {label_result['message']}"
                    }
                
                archive_label_id = label_result['label_id']
                
                # Move to archive
                move_result = self.move_messages_to_label(
                    archive_messages,
                    archive_label_id,
                    remove_from_inbox=True
                )
                archived_count = move_result.get('moved_count', 0)
                print(f"DEBUG: Archived {archived_count} messages")
            
            # 2. Delete emails (move to trash)
            if delete_messages:
                for msg_id in delete_messages:
                    try:
                        self.service.users().messages().trash(
                            userId='me',
                            id=msg_id
                        ).execute()
                        deleted_count += 1
                        
                        if deleted_count % 50 == 0:
                            print(f"DEBUG: Deleted {deleted_count}/{len(delete_messages)} messages")
                    
                    except Exception as e:
                        print(f"DEBUG: Error deleting message {msg_id}: {e}")
                        continue
                
                print(f"DEBUG: Deleted {deleted_count} messages to trash")
            
            return {
                'success': True,
                'preview': preview,
                'executed': {
                    'archived': archived_count,
                    'deleted': deleted_count
                },
                'message': f"Archived {archived_count} emails, deleted {deleted_count} emails to trash"
            }
        
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in Clean-up_history: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }

def get_storage_info(self):
    """
    Get Gmail storage information
    
    Returns:
        dict: {
            'success': bool,
            'used_bytes': int,
            'total_bytes': int,
            'used_mb': float,
            'total_mb': float,
            'used_gb': float,
            'total_gb': float,
            'percentage': float
        }
    """
    try:
        profile = self.service.users().getProfile(userId='me').execute()
        
        # Gmail storage is messagesTotal (number) and emailsTotal (size estimate)
        # But actual storage comes from historyId and other metadata
        # We need to use the quota from the profile
        
        # Note: Gmail API doesn't directly expose storage quota in profile
        # We'll use messagesTotal as a proxy and emailsTotal for size
        messages_total = profile.get('messagesTotal', 0)
        threads_total = profile.get('threadsTotal', 0)
        history_id = profile.get('historyId', 0)
        
        # For actual storage, we need to sum message sizes
        # This is an approximation - get a sample and extrapolate
        # Or we can just return message count for now
        
        # Gmail free tier = 15GB
        total_bytes = 15 * 1024 * 1024 * 1024  # 15GB in bytes
        
        # This is a limitation: Gmail API doesn't provide direct storage used
        # We can only estimate or return message count
        
        return {
            'success': True,
            'messages_total': messages_total,
            'threads_total': threads_total,
            'note': 'Gmail API does not provide direct storage quota. Message count shown instead.'
        }
        
    except Exception as e:
        print(f"DEBUG: Error getting storage info: {e}")
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }