"""
Feature Configuration
Controls which email actions are enabled/disabled
Allows for gradual rollout and A/B testing
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Feature flags - control which actions are available
FEATURES = {
    'create_folder': os.getenv('FEATURE_CREATE_FOLDER', 'true').lower() == 'true',
    'delete_all': os.getenv('FEATURE_DELETE_ALL', 'false').lower() == 'true',
    'Cleanup_history': os.getenv('FEATURE_CLEANUP_HISTORY', 'false').lower() == 'true',
    'archive': os.getenv('FEATURE_ARCHIVE', 'false').lower() == 'true',
    'unsubscribe': os.getenv('FEATURE_UNSUBSCRIBE', 'false').lower() == 'true',
}

# Action button configurations
ACTION_BUTTONS = {
    'create_folder': {
        'label': '📁 Create Folder',
        'description': 'Move emails to a folder and create a rule',
        'phase': 1,
        'requires_selection': True
    },
    'delete_all': {
        'label': '🗑️ Delete All',
        'description': 'Delete all emails from sender',
        'phase': 2,
        'requires_selection': True
    },
    'Cleanup_history': {
        'label': '📜 Cleanup History',
        'description': 'Set retention policies for emails',
        'phase': 2,
        'requires_selection': True
    },
    'archive': {
        'label': '📦 Archive',
        'description': 'Save emails to zip file',
        'phase': 2,
        'requires_selection': True
    },
    'unsubscribe': {
        'label': '🚫 Unsubscribe',
        'description': 'View unsubscribe options',
        'phase': 1,
        'requires_selection': True
    }
}

def get_enabled_actions():
    """Return list of enabled action names"""
    return [action for action, enabled in FEATURES.items() if enabled]

def is_action_enabled(action_name):
    """Check if specific action is enabled"""
    return FEATURES.get(action_name, False)

def get_action_config(action_name):
    """Get configuration for specific action"""
    if action_name in ACTION_BUTTONS:
        config = ACTION_BUTTONS[action_name].copy()
        config['enabled'] = FEATURES.get(action_name, False)
        return config
    return None
