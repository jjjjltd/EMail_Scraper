"""
Email Actions Module
Modular, self-contained email manipulation functions
Each action is independent and can be enabled/disabled via config
"""

import imaplib
import email
from datetime import datetime
import re

# Import Gmail API for reliable Gmail operations
from gmail_api import GmailAPI


class EmailActions:
    """Handles all email manipulation actions (create folder, delete, archive, etc.)"""
    
    @staticmethod
    def create_folder_gmail(access_token, sender_emails, folder_name):
        """
        Create a folder and move emails using Gmail API (reliable for Gmail)
        
        Args:
            access_token: OAuth2 access token
            sender_emails: Email address(es) of sender(s) - can be string or list
            folder_name: Name of folder/label to create
        
        Returns:
            dict: {'success': bool, 'message': str, 'emails_moved': int, 'folder_created': str}
        """
        try:
            # Initialize Gmail API
            gmail = GmailAPI(access_token)
            
            # Use Gmail API to create folder and move emails
            result = gmail.create_folder_and_move(sender_emails, folder_name)
            
            return result
            
        except Exception as e:
            import traceback
            print(f"DEBUG: create_folder_gmail error: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'emails_moved': 0,
                'folder_created': None
            }
    
    @staticmethod
    def create_folder_microsoft(access_token, sender_emails, folder_name):
        """
        Create a folder and move emails using Microsoft Graph API
        
        Args:
            access_token: OAuth2 access token
            sender_emails: Email address(es) of sender(s) - can be string or list
            folder_name: Name of folder to create
        
        Returns:
            dict: {'success': bool, 'message': str, 'emails_moved': int, 'folder_created': str, 'filters_created': int}
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import time
        
        print(f"DEBUG: access_token type: {type(access_token)}")
        print(f"DEBUG: access_token length: {len(access_token) if access_token else 'None'}")
        print(f"DEBUG: access_token first 50 chars: {access_token[:50] if access_token else 'None'}")
        print(f"DEBUG: Contains dots? {('.' in access_token) if access_token else 'N/A'}")
    
        # Configure session with retry logic
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # 3 retries
            backoff_factor=2,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP codes
            allowed_methods=["GET", "POST"]  # Retry GET and POST
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
    


        try:
            # Support both single sender and multiple senders
            if isinstance(sender_emails, str):
                sender_emails = [sender_emails]
            
            # Graph API base URL
            graph_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Step 1: Create folder (mailFolder)
            print(f"DEBUG: Creating folder '{folder_name}' via Graph API")
            
            folder_response = session.post(
                f"{graph_url}/mailFolders",
                headers=headers,
                json={'displayName': folder_name},
                timeout=30
            )
            
            if folder_response.status_code == 201:
                folder_id = folder_response.json()['id']
                print(f"DEBUG: Folder created with ID: {folder_id}")
            elif folder_response.status_code == 409:
                # Folder already exists, get its ID
                print(f"DEBUG: Folder '{folder_name}' already exists, finding ID...")
                
                # First try top-level folders
                folders_response = session.get(f"{graph_url}/mailFolders", headers=headers, timeout=30)
                
                if folders_response.status_code != 200:
                    print(f"DEBUG: Failed to list folders: {folders_response.status_code}")
                    return {
                        'success': False,
                        'message': f'Folder exists but could not list folders to find ID',
                        'emails_moved': 0,
                        'folder_created': None,
                        'filters_created': 0
                    }
                
                folders = folders_response.json().get('value', [])
                print(f"DEBUG: Found {len(folders)} top-level folders")
                
                folder_id = None
                for folder in folders:
                    print(f"DEBUG: Checking folder: {folder.get('displayName')}")
                    if folder['displayName'] == folder_name:
                        folder_id = folder['id']
                        print(f"DEBUG: Found matching folder with ID: {folder_id}")
                        break
                
                if not folder_id:
                    # Also check child folders (in case user created it as subfolder)
                    for parent_folder in folders:
                        child_url = f"{graph_url}/mailFolders/{parent_folder['id']}/childFolders"
                        child_response = session.get(child_url, headers=headers, timeout=30)
                        if child_response.status_code == 200:
                            child_folders = child_response.json().get('value', [])
                            for child in child_folders:
                                print(f"DEBUG: Checking child folder: {child.get('displayName')}")
                                if child['displayName'] == folder_name:
                                    folder_id = child['id']
                                    print(f"DEBUG: Found matching child folder with ID: {folder_id}")
                                    break
                            if folder_id:
                                break
                
                if not folder_id:
                    return {
                        'success': False,
                        'message': f'Folder "{folder_name}" exists but could not find ID. Try using a different name.',
                        'emails_moved': 0,
                        'folder_created': None,
                        'filters_created': 0
                    }
            else:
                return {
                    'success': False,
                    'message': f'Failed to create folder: {folder_response.status_code} - {folder_response.text}',
                    'emails_moved': 0,
                    'folder_created': None,
                    'filters_created': 0
                }
            
            # Step 2: Find and move emails from each sender
            total_moved = 0
            
            for sender_email in sender_emails:
                print(f"DEBUG: Searching for emails from {sender_email}")
                
                # Search for emails from this sender with pagination
                search_url = f"{graph_url}/messages?$filter=from/emailAddress/address eq '{sender_email}'&$top=999"
                
                all_messages = []
                while search_url:
                    messages_response = session.get(search_url, headers=headers, timeout=30)
                    
                    if messages_response.status_code != 200:
                        print(f"DEBUG: Failed to search for {sender_email}: {messages_response.status_code}")
                        break
                    
                    data = messages_response.json()
                    messages = data.get('value', [])
                    all_messages.extend(messages)
                    
                    # Check for next page
                    search_url = data.get('@odata.nextLink')
                
                print(f"DEBUG: Found {len(all_messages)} emails from {sender_email}")
                
                # Move each email to the folder
                for message in all_messages:
                    message_id = message['id']
                    
                    # Retry individual moves up to 3 times on network errors
                    for attempt in range(3):
                        try:
                            move_response = session.post(
                                f"{graph_url}/messages/{message_id}/move",
                                headers=headers,
                                json={'destinationId': folder_id},
                                timeout=30
                            )
                            
                            if move_response.status_code in [200, 201]:
                                total_moved += 1
                                break  # Success, move to next email
                            else:
                                print(f"DEBUG: Failed to move message {message_id}: {move_response.status_code}")
                                if attempt < 2:  # Only retry if not last attempt
                                    time.sleep(1)
                                    continue
                                break  # Failed all retries
                        
                        except (requests.exceptions.ConnectionError, 
                                requests.exceptions.Timeout,
                                requests.exceptions.RequestException) as e:
                            if attempt < 2:  # Retry on network errors
                                print(f"DEBUG: Network error moving message (attempt {attempt + 1}/3): {e}")
                                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                                continue
                            else:
                                print(f"DEBUG: Failed to move message after 3 attempts: {e}")
                                break
            
            print(f"DEBUG: Total moved: {total_moved} emails")
            
            # Step 3: Create inbox rules (filters) for future emails
            filters_created = 0
            
            for sender_email in sender_emails:
                try:
                    rule_body = {
                        'displayName': f'Auto-move from {sender_email}',
                        'sequence': 1,  # Required: rule priority (1 = highest)
                        'isEnabled': True,
                        'conditions': {
                            'fromAddresses': [
                                {'emailAddress': {'address': sender_email}}
                            ]
                        },
                        'actions': {
                            'moveToFolder': folder_id
                        }
                    }
                    
                    rule_response = session.post(
                        f"{graph_url}/mailFolders/inbox/messageRules",
                        headers=headers,
                        json=rule_body,
                        timeout=30
                    )
                    
                    if rule_response.status_code in [200, 201]:
                        filters_created += 1
                        print(f"DEBUG: Created rule for {sender_email}")
                    else:
                        print(f"DEBUG: Failed to create rule for {sender_email}: {rule_response.status_code}")
                
                except Exception as e:
                    print(f"DEBUG: Error creating rule for {sender_email}: {e}")
            
            return {
                'success': True,
                'message': f'Successfully moved {total_moved} emails to {folder_name}',
                'emails_moved': total_moved,
                'folder_created': folder_name,
                'filters_created': filters_created,
                'failed_count': 0
            }
        
        except Exception as e:
            import traceback
            print(f"DEBUG: create_folder_microsoft error: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'emails_moved': 0,
                'folder_created': None,
                'filters_created': 0
            }
    
    
    @staticmethod
    def create_email_rule(mail, sender_email, folder_name, provider='google'):
        """
        Create email filter/rule for future emails from sender
        
        Args:
            mail: Active IMAP connection
            sender_email: Email address of sender
            folder_name: Destination folder for future emails
            provider: 'google' or 'microsoft'
        
        Returns:
            dict: {'success': bool, 'message': str, 'rule_type': str}
        """
        try:
            if provider == 'google':
                # Gmail filters cannot be created via IMAP
                # Must use Gmail API or manual creation
                return {
                    'success': False,
                    'message': 'Gmail filters require Gmail API (not available via IMAP). Please create filter manually in Gmail settings.',
                    'rule_type': 'gmail_filter',
                    'manual_instructions': f'Create filter: FROM {sender_email} → Move to {folder_name}'
                }
            
            elif provider == 'microsoft':
                # Outlook rules cannot be created via IMAP
                # Must use Outlook API or manual creation
                return {
                    'success': False,
                    'message': 'Outlook rules require Outlook API (not available via IMAP). Please create rule manually in Outlook settings.',
                    'rule_type': 'outlook_rule',
                    'manual_instructions': f'Create rule: FROM {sender_email} → Move to {folder_name}'
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown provider: {provider}',
                    'rule_type': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating rule: {str(e)}',
                'rule_type': None
            }
    
    @staticmethod
    def delete_all(mail, sender_email, provider='google'):
        """
        Delete all emails from sender
        
        Args:
            mail: Active IMAP connection
            sender_email: Email address of sender
            provider: 'google' or 'microsoft'
        
        Returns:
            dict: {'success': bool, 'message': str, 'emails_deleted': int}
        """
        # Placeholder for Phase 2
        return {
            'success': False,
            'message': 'Delete All feature not yet implemented (Phase 2)',
            'emails_deleted': 0
        }
    
    @staticmethod
    def Clean_up_history(mail, sender_email, days_config, provider='google'):
        """
        Clean-up email retention policies
        
        Args:
            mail: Active IMAP connection
            sender_email: Email address of sender
            days_config: dict with 'keep_days', 'folder_days', 'delete_days'
            provider: 'google' or 'microsoft'
        
        Returns:
            dict: {'success': bool, 'message': str, 'emails_processed': int}
        """
        # Placeholder for Phase 2
        return {
            'success': False,
            'message': 'Clean-up History feature not yet implemented (Phase 2)',
            'emails_processed': 0
        }
    @staticmethod
    def cleanup_history_microsoft(graph_token, sender_emails, keep_days, archive_days, delete_days, preview_only=False):
        """
        Clean up email history using age-based policies (one-time action)
        
        Args:
            graph_token: Graph API access token
            sender_emails: List of sender email addresses
            keep_days: Keep emails newer than this (e.g., 7)
            archive_days: Not used - kept for API compatibility
            delete_days: Delete emails older than this (e.g., 60)
            preview_only: If True, only count emails, don't move/delete
        
        Logic:
            - Emails < keep_days: Stay in inbox
            - Emails keep_days to delete_days: Move to Archive
            - Emails > delete_days: Move to Trash
        
        Returns:
            dict: For preview: {'success': bool, 'preview': {'keep_count', 'archive_count', 'delete_count'}}
                For execution: {'success': bool, 'message': str, 'executed': {'archived', 'deleted'}}
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        from datetime import datetime, timedelta
        import time
        
        # Configure session with retry logic
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        
        try:
            # Support single sender
            if isinstance(sender_emails, str):
                sender_emails = [sender_emails]
            
            graph_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {graph_token}',
                'Content-Type': 'application/json'
            }
            
            # Calculate date thresholds (UTC)
            now = datetime.utcnow()
            keep_date = now - timedelta(days=int(keep_days))
            delete_date = now - timedelta(days=int(delete_days))
            
            # Format for Graph API (ISO 8601)
            keep_date_str = keep_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            delete_date_str = delete_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            print(f"DEBUG: Cleanup thresholds - Keep: {keep_date_str}, Delete: {delete_date_str}")
            
            # Get or create Archive folder
            archive_folder_id = None
            if not preview_only:
                # Check if Archive folder exists
                folders_response = session.get(f"{graph_url}/mailFolders", headers=headers, timeout=30)
                if folders_response.status_code == 200:
                    folders = folders_response.json().get('value', [])
                    for folder in folders:
                        if folder['displayName'].lower() == 'archive':
                            archive_folder_id = folder['id']
                            print(f"DEBUG: Found existing Archive folder: {archive_folder_id}")
                            break
                    
                    # Create Archive folder if doesn't exist
                    if not archive_folder_id:
                        create_response = session.post(
                            f"{graph_url}/mailFolders",
                            headers=headers,
                            json={'displayName': 'Archive'},
                            timeout=30
                        )
                        if create_response.status_code == 201:
                            archive_folder_id = create_response.json()['id']
                            print(f"DEBUG: Created Archive folder: {archive_folder_id}")
            
            # Get DeletedItems folder ID (use well-known name)
            deleted_folder_id = 'deleteditems'
            
            # Counters
            keep_count = 0
            archive_count = 0
            delete_count = 0
            
            actually_archived = 0
            actually_deleted = 0
            
            # Process each sender
            for sender_email in sender_emails:
                print(f"DEBUG: Processing emails from {sender_email}")
                
                # Fetch emails from INBOX ONLY with pagination
                search_url = f"{graph_url}/mailFolders/inbox/messages?$filter=from/emailAddress/address eq '{sender_email}'&$select=id,receivedDateTime&$top=999"
                
                all_messages = []
                while search_url:
                    messages_response = session.get(search_url, headers=headers, timeout=30)
                    
                    if messages_response.status_code != 200:
                        print(f"DEBUG: Failed to fetch emails from {sender_email}: {messages_response.status_code}")
                        break
                    
                    data = messages_response.json()
                    messages = data.get('value', [])
                    all_messages.extend(messages)
                    
                    # Check for next page
                    search_url = data.get('@odata.nextLink')
                
                print(f"DEBUG: Found {len(all_messages)} inbox emails from {sender_email}")
                
                # Categorize and process emails by age
                for message in all_messages:
                    message_id = message['id']
                    received_str = message['receivedDateTime']
                    
                    # Parse datetime (format: 2024-01-15T10:30:00Z)
                    received_dt = datetime.strptime(received_str, '%Y-%m-%dT%H:%M:%SZ')
                    
                    # Determine action based on age
                    # Logic: <keep_days (keep), keep_days to delete_days (archive), >delete_days (delete)
                    
                    if received_dt >= keep_date:
                        # Newer than keep_days - keep in inbox
                        keep_count += 1
                    
                    elif received_dt >= delete_date:
                        # Between keep_days and delete_days - move to Archive
                        archive_count += 1
                        
                        if not preview_only and archive_folder_id:
                            # Actually move to Archive
                            for attempt in range(3):
                                try:
                                    move_response = session.post(
                                        f"{graph_url}/messages/{message_id}/move",
                                        headers=headers,
                                        json={'destinationId': archive_folder_id},
                                        timeout=30
                                    )
                                    
                                    if move_response.status_code in [200, 201]:
                                        actually_archived += 1
                                        break
                                    elif attempt < 2:
                                        time.sleep(1)
                                except Exception as e:
                                    if attempt < 2:
                                        print(f"DEBUG: Network error on archive attempt {attempt + 1}: {e}")
                                        time.sleep(2)
                                    else:
                                        print(f"DEBUG: Failed to archive {message_id} after 3 attempts: {e}")
                                    break
                    
                    else:
                        # Older than delete_days - move to Trash
                        delete_count += 1
                        
                        if not preview_only:
                            # Actually move to Deleted Items
                            for attempt in range(3):
                                try:
                                    move_response = session.post(
                                        f"{graph_url}/messages/{message_id}/move",
                                        headers=headers,
                                        json={'destinationId': deleted_folder_id},
                                        timeout=30
                                    )
                                    
                                    if move_response.status_code in [200, 201]:
                                        actually_deleted += 1
                                        break
                                    elif attempt < 2:
                                        time.sleep(1)
                                except Exception as e:
                                    if attempt < 2:
                                        print(f"DEBUG: Network error on delete attempt {attempt + 1}: {e}")
                                        time.sleep(2)
                                    else:
                                        print(f"DEBUG: Failed to delete {message_id} after 3 attempts: {e}")
                                    break
            
            # Return results
            if preview_only:
                return {
                    'success': True,
                    'preview': {
                        'keep_count': keep_count,
                        'archive_count': archive_count,
                        'delete_count': delete_count
                    }
                }
            else:
                return {
                    'success': True,
                    'message': f'Cleanup complete: Archived {actually_archived}, Deleted {actually_deleted} emails',
                    'executed': {
                        'archived': actually_archived,
                        'deleted': actually_deleted
                    }
                }
        
        except Exception as e:
            import traceback
            print(f"DEBUG: cleanup_history_microsoft error: {e}")
            print(traceback.format_exc())
            
            if preview_only:
                return {
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'preview': {'keep_count': 0, 'archive_count': 0, 'delete_count': 0}
                }
            else:
                return {
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'executed': {'archived': 0, 'deleted': 0}
                }

        @staticmethod
        def archive_emails(mail, sender_email, archive_path, provider='google'):
            """
            Archive emails to zip file
            
            Args:
                mail: Active IMAP connection
                sender_email: Email address of sender
                archive_path: Path to save archive
                provider: 'google' or 'microsoft'
            
            Returns:
                dict: {'success': bool, 'message': str, 'emails_archived': int, 'archive_file': str}
            """
            # Placeholder for Phase 2
            return {
                'success': False,
                'message': 'Archive feature not yet implemented (Phase 2)',
                'emails_archived': 0,
                'archive_file': None
            }
        
    def create_gmail_filter(self, sender_email, label_id):
        """
        Create Gmail filter to auto-label future emails
        
        Args:
            sender_email: Email address to filter
            label_id: Label to apply
        """
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
        
        return created_filter