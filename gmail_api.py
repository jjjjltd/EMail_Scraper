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
        Search for all messages from a specific sender
        
        Args:
            sender_email: Email address to search for
            
        Returns:
            list: Message IDs
        """
        try:
            query = f'from:{sender_email}'
            print(f"DEBUG: Searching for messages from: {sender_email}")
            
            all_messages = []
            page_token = None
            
            while True:
                # Search with pagination
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token
                ).execute()
                
                messages = results.get('messages', [])
                all_messages.extend(messages)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            message_ids = [msg['id'] for msg in all_messages]
            print(f"DEBUG: Found {len(message_ids)} messages from {sender_email}")
            
            return message_ids
            
        except Exception as e:
            print(f"DEBUG: Error searching messages: {e}")
            return []
    
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
            
                filter_result = self.create_gmail_filter(sender_email, label_id)
                filters_created += 1

            return {
                'success': True,
                'message': f"Successfully moved {total_moved} emails to {folder_name}",
                'emails_moved': total_moved,
                'failed_count': total_failed,
                'folder_created': folder_name,
                'label_id': label_id
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
