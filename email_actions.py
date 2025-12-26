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
    def create_folder(mail, sender_emails, folder_name, provider='google'):
        """
        Create a folder and move all emails from sender(s) into it
        
        Args:
            mail: Active IMAP connection
            sender_emails: Email address(es) of sender(s) - can be string or list
            folder_name: Name of folder to create
            provider: 'google' or 'microsoft'
        
        Returns:
            dict: {'success': bool, 'message': str, 'emails_moved': int, 'folder_created': str}
        """
        try:
            # Support both single sender and multiple senders
            if isinstance(sender_emails, str):
                sender_emails = [sender_emails]
            
            # Normalize folder name for IMAP
            if provider == 'google':
                # Gmail uses format: [Gmail]/FolderName or just FolderName
                # For user-created folders, just use the name
                imap_folder = folder_name
            elif provider == 'microsoft':
                # Outlook uses format: FolderName or Inbox/FolderName
                imap_folder = folder_name
            else:
                return {'success': False, 'message': f'Unknown provider: {provider}'}
            
            print(f"DEBUG: Creating folder '{imap_folder}'")
            
            # Create the folder
            status, response = mail.create(imap_folder)
            
            # Check if already exists (not an error)
            if status != 'OK':
                # Folder might already exist
                if b'already exists' in str(response).lower() or b'alreadyexists' in str(response).lower():
                    print(f"DEBUG: Folder already exists: {imap_folder}")
                else:
                    return {
                        'success': False, 
                        'message': f'Failed to create folder: {response}',
                        'emails_moved': 0,
                        'folder_created': None
                    }
            
            print(f"DEBUG: Folder created/exists: {imap_folder}")
            
            # Select inbox
            mail.select('INBOX')
            
            # Process all senders
            total_moved = 0
            for sender_email in sender_emails:
                # Search for all emails from this sender
                search_criteria = f'(FROM "{sender_email}")'
                status, messages = mail.search(None, search_criteria)
                
                if status != 'OK':
                    print(f"DEBUG: Failed to search for {sender_email}: {status}")
                    continue
                
                email_ids = messages[0].split()
                sender_count = len(email_ids)
                
                if sender_count == 0:
                    print(f"DEBUG: No emails found from {sender_email}")
                    continue
                
                print(f"DEBUG: Found {sender_count} emails from {sender_email}")
                
                # Move emails to folder
                moved_count = 0
                for email_id in email_ids:
                    try:
                        # Copy email to new folder
                        status, response = mail.copy(email_id, imap_folder)
                        if status == 'OK':
                            # Mark original for deletion
                            mail.store(email_id, '+FLAGS', '\\Deleted')
                            moved_count += 1
                    except Exception as e:
                        print(f"DEBUG: Error moving email {email_id}: {e}")
                        continue
                
                print(f"DEBUG: Moved {moved_count}/{sender_count} emails from {sender_email}")
                total_moved += moved_count
            
            # Expunge to actually delete marked emails
            mail.expunge()
            
            print(f"DEBUG: Total moved: {total_moved} emails")
            
            return {
                'success': True,
                'message': f'Successfully moved {total_moved} emails to {folder_name}',
                'emails_moved': total_moved,
                'folder_created': imap_folder
            }
            
        except Exception as e:
            import traceback
            print(f"DEBUG: create_folder error: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'emails_moved': 0,
                'folder_created': None
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
    def manage_history(mail, sender_email, days_config, provider='google'):
        """
        Manage email retention policies
        
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
            'message': 'Manage History feature not yet implemented (Phase 2)',
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
