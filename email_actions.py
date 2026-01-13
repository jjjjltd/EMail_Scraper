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
            
            folder_response = requests.post(
                f"{graph_url}/mailFolders",
                headers=headers,
                json={'displayName': folder_name}
            )
            
            if folder_response.status_code == 201:
                folder_id = folder_response.json()['id']
                print(f"DEBUG: Folder created with ID: {folder_id}")
            elif folder_response.status_code == 409:
                # Folder already exists, get its ID
                print(f"DEBUG: Folder '{folder_name}' already exists, finding ID...")
                folders_response = requests.get(f"{graph_url}/mailFolders", headers=headers)
                folders = folders_response.json().get('value', [])
                folder_id = None
                for folder in folders:
                    if folder['displayName'] == folder_name:
                        folder_id = folder['id']
                        break
                if not folder_id:
                    return {
                        'success': False,
                        'message': f'Folder exists but could not find ID',
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
                
                # Search for emails from this sender
                search_url = f"{graph_url}/messages?$filter=from/emailAddress/address eq '{sender_email}'"
                messages_response = requests.get(search_url, headers=headers)
                
                if messages_response.status_code != 200:
                    print(f"DEBUG: Failed to search for {sender_email}: {messages_response.status_code}")
                    continue
                
                messages = messages_response.json().get('value', [])
                print(f"DEBUG: Found {len(messages)} emails from {sender_email}")
                
                # Move each email to the folder
                for message in messages:
                    message_id = message['id']
                    try:
                        move_response = requests.post(
                            f"{graph_url}/messages/{message_id}/move",
                            headers=headers,
                            json={'destinationId': folder_id}
                        )
                        
                        if move_response.status_code in [200, 201]:
                            total_moved += 1
                        else:
                            print(f"DEBUG: Failed to move message {message_id}: {move_response.status_code}")
                    
                    except Exception as e:
                        print(f"DEBUG: Error moving message {message_id}: {e}")
                        continue
            
            print(f"DEBUG: Total moved: {total_moved} emails")
            
            # Step 3: Create inbox rules (filters) for future emails
            filters_created = 0
            
            for sender_email in sender_emails:
                try:
                    rule_body = {
                        'displayName': f'Auto-move from {sender_email}',
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
                    
                    rule_response = requests.post(
                        f"{graph_url}/mailFolders/inbox/messageRules",
                        headers=headers,
                        json=rule_body
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