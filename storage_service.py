#!/usr/bin/env python3
"""
Storage service layer for ChatBot v1.0
Provides high-level interface for persistent storage operations
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import json
import logging
from database import DatabaseManager, init_streamlit_database

class StorageService:
    """High-level storage service for the ChatBot application"""
    
    def __init__(self):
        self.db = init_streamlit_database()
        self.logger = logging.getLogger(__name__)
    
    # Project Management
    def create_project(self, name: str, description: str = "") -> str:
        """Create a new project and return its ID"""
        project_id = str(uuid.uuid4())
        
        metadata = {
            'created_by': 'user',
            'version': '1.0',
            'document_count': 0,
            'message_count': 0
        }
        
        success = self.db.create_project(project_id, name, description, metadata)
        if success:
            self.logger.info(f"Created project: {name} ({project_id})")
            return project_id
        else:
            raise Exception("Failed to create project")
    
    def get_all_projects(self) -> List[Dict]:
        """Get all active projects with enhanced metadata"""
        projects = self.db.get_projects(active_only=True)
        
        # Enhance with live counts
        for project in projects:
            project_id = project['id']
            
            # Get message count
            messages = self.db.get_chat_messages(project_id)
            project['message_count'] = len(messages)
            
            # Get document count
            documents = self.db.get_documents(project_id)
            project['document_count'] = len(documents)
            
            # Get last activity
            if messages:
                project['last_activity'] = messages[-1]['timestamp']
            else:
                project['last_activity'] = project['created_at']
        
        return projects
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project with full details"""
        project = self.db.get_project(project_id)
        if project:
            # Add live counts
            messages = self.db.get_chat_messages(project_id)
            documents = self.db.get_documents(project_id)
            
            project['message_count'] = len(messages)
            project['document_count'] = len(documents)
            project['messages'] = messages
            project['documents'] = documents
        
        return project
    
    def update_project(self, project_id: str, name: str = None, description: str = None) -> bool:
        """Update project details"""
        return self.db.update_project(project_id, name, description)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project (soft delete)"""
        return self.db.delete_project(project_id, soft_delete=True)
    
    def duplicate_project(self, project_id: str, new_name: str) -> Optional[str]:
        """Duplicate a project with all its data"""
        original = self.get_project(project_id)
        if not original:
            return None
        
        # Create new project
        new_project_id = self.create_project(new_name, f"Copy of {original['description']}")
        
        # Copy messages
        for message in original['messages']:
            self.db.add_chat_message(
                new_project_id,
                message['role'],
                message['content'],
                message.get('metadata')
            )
        
        # Copy documents
        for doc in original['documents']:
            new_doc_id = str(uuid.uuid4())
            self.db.add_document(
                new_doc_id,
                new_project_id,
                doc['filename'],
                doc['content'],
                doc['file_type'],
                doc['file_size'],
                doc.get('metadata')
            )
        
        return new_project_id
    
    # Chat Session Management
    def create_chat_session(self, project_id: str, name: str) -> str:
        """Create a new chat session and return its ID"""
        session_id = str(uuid.uuid4())
        success = self.db.create_chat_session(session_id, project_id, name)
        if success:
            self.logger.info(f"Created chat session: {name} ({session_id}) for project {project_id}")
            return session_id
        else:
            raise Exception("Failed to create chat session")
    
    def get_project_sessions(self, project_id: str) -> List[Dict]:
        """Get all chat sessions for a project"""
        return self.db.get_project_sessions(project_id)
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a chat session"""
        return self.db.rename_session(session_id, new_name)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        return self.db.delete_session(session_id, soft_delete=True)
    
    def get_or_create_default_session(self, project_id: str) -> str:
        """Get the default session for a project or create one if none exists"""
        sessions = self.get_project_sessions(project_id)
        
        if not sessions:
            # Create default session
            return self.create_chat_session(project_id, "Haupt-Chat")
        
        # Return the first active session
        return sessions[0]['id']

    # Chat Management
    def add_message(self, project_id: str, role: str, content: str, metadata: Dict = None, session_id: str = None) -> bool:
        """Add a message to project chat (with session support)"""
        if not session_id:
            # Get or create default session for backward compatibility
            session_id = self.get_or_create_default_session(project_id)
        
        return self.db.add_chat_message(project_id, role, content, metadata, session_id)
    
    def get_chat_history(self, project_id: str, limit: int = None, session_id: str = None) -> List[Dict]:
        """Get chat history for a project or specific session"""
        return self.db.get_chat_messages(project_id, limit, session_id)
    
    def clear_chat_history(self, project_id: str) -> bool:
        """Clear all chat messages for a project"""
        return self.db.clear_chat_messages(project_id)
    
    def search_messages(self, project_id: str, query: str) -> List[Dict]:
        """Search messages in a project (simple text search)"""
        messages = self.get_chat_history(project_id)
        results = []
        query_lower = query.lower()
        
        for message in messages:
            if query_lower in message['content'].lower():
                results.append(message)
        
        return results
    
    # Document Management
    def add_document(self, project_id: str, filename: str, content: str, file_type: str, file_size: int) -> str:
        """Add a document to a project"""
        doc_id = str(uuid.uuid4())
        
        metadata = {
            'upload_timestamp': datetime.now().isoformat(),
            'processed': True,
            'char_count': len(content),
            'word_count': len(content.split())
        }
        
        success = self.db.add_document(doc_id, project_id, filename, content, file_type, file_size, metadata)
        if success:
            return doc_id
        else:
            raise Exception("Failed to add document")
    
    def get_project_documents(self, project_id: str) -> List[Dict]:
        """Get all documents for a project"""
        return self.db.get_documents(project_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        return self.db.delete_document(doc_id)
    
    def get_document_content(self, project_id: str) -> Dict[str, Dict]:
        """Get formatted document content for chat context"""
        documents = self.get_project_documents(project_id)
        doc_content = {}
        
        for doc in documents:
            doc_content[doc['id']] = {
                'filename': doc['filename'],
                'content': doc['content'],
                'file_type': doc['file_type'],
                'metadata': doc.get('metadata', {})
            }
        
        return doc_content
    
    # Settings Management
    def save_settings(self, settings: Dict) -> bool:
        """Save application settings"""
        try:
            # Flatten nested settings for storage
            flat_settings = self._flatten_dict(settings)
            
            for key, value in flat_settings.items():
                self.db.set_setting(key, value)
            
            # Also save as complete config
            self.db.set_setting('complete_config', settings, 'Complete application configuration')
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    def load_settings(self, default_settings: Dict = None) -> Dict:
        """Load application settings"""
        try:
            # Try to load complete config first
            complete_config = self.db.get_setting('complete_config')
            if complete_config:
                return complete_config
            
            # Fallback to reconstructing from flat settings
            flat_settings = self.db.get_all_settings()
            if flat_settings:
                return self._unflatten_dict(flat_settings)
            
            # Return default if nothing found
            return default_settings or {}
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return default_settings or {}
    
    def save_user_preference(self, key: str, value: Any) -> bool:
        """Save a user preference"""
        return self.db.set_user_preference(key, value)
    
    def get_user_preference(self, key: str, default=None) -> Any:
        """Get a user preference"""
        return self.db.get_user_preference(key, default)
    
    # Analytics and Statistics
    def get_application_stats(self) -> Dict:
        """Get comprehensive application statistics"""
        db_stats = self.db.get_database_stats()
        
        # Add computed stats
        projects = self.get_all_projects()
        
        stats = {
            **db_stats,
            'projects_with_messages': sum(1 for p in projects if p['message_count'] > 0),
            'projects_with_documents': sum(1 for p in projects if p['document_count'] > 0),
            'avg_messages_per_project': round(db_stats['total_messages'] / max(db_stats['active_projects'], 1), 1),
            'avg_documents_per_project': round(db_stats['total_documents'] / max(db_stats['active_projects'], 1), 1)
        }
        
        return stats
    
    def export_project(self, project_id: str) -> Dict:
        """Export project data for backup/sharing"""
        return self.db.export_project_data(project_id)
    
    def backup_all_data(self, backup_path: str) -> bool:
        """Backup entire database"""
        return self.db.backup_database(backup_path)
    
    # Migration helpers
    def migrate_from_session_state(self, session_projects: Dict) -> bool:
        """Migrate data from session state to database"""
        try:
            migrated_count = 0
            
            for project_id, project_data in session_projects.items():
                # Create project
                success = self.db.create_project(
                    project_id,
                    project_data.get('name', 'Untitled Project'),
                    project_data.get('description', ''),
                    {'migrated': True, 'original_id': project_id}
                )
                
                if success:
                    # Create default session for messages
                    session_id = None
                    messages = project_data.get('messages', [])
                    if messages:
                        session_id = self.create_chat_session(project_id, "Haupt-Chat")
                    
                    # Migrate messages
                    for msg in messages:
                        self.add_message(project_id, msg['role'], msg['content'], session_id=session_id)
                    
                    # Migrate documents
                    documents = project_data.get('documents', {})
                    for doc_id, doc_data in documents.items():
                        self.db.add_document(
                            doc_id,
                            project_id,
                            doc_data.get('filename', 'Unknown'),
                            doc_data.get('content', ''),
                            doc_data.get('file_type', 'text'),
                            len(doc_data.get('content', '')),
                            {'migrated': True}
                        )
                    
                    migrated_count += 1
            
            self.logger.info(f"Migrated {migrated_count} projects from session state")
            return True
            
        except Exception as e:
            self.logger.error(f"Error migrating from session state: {e}")
            return False
    
    def migrate_existing_projects_to_sessions(self) -> bool:
        """Migrate existing projects without sessions to have default sessions"""
        try:
            projects = self.get_all_projects()
            migrated_count = 0
            
            for project in projects:
                project_id = project['id']
                
                # Check if project has any sessions
                sessions = self.get_project_sessions(project_id)
                if not sessions:
                    # Get existing messages for this project
                    messages = self.get_chat_history(project_id)
                    
                    if messages:
                        # Create default session
                        session_id = self.create_chat_session(project_id, "Haupt-Chat")
                        
                        # Update all existing messages to belong to this session
                        for message in messages:
                            # Update message with session_id using raw database query
                            with self.db.get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    'UPDATE chat_messages SET session_id = ? WHERE id = ?',
                                    (session_id, message['id'])
                                )
                        
                        # Update session message count
                        self.db.update_session_message_count(session_id)
                        migrated_count += 1
            
            self.logger.info(f"Migrated {migrated_count} projects to use sessions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error migrating projects to sessions: {e}")
            return False
    
    # Utility methods
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _unflatten_dict(self, flat_dict: Dict, sep: str = '.') -> Dict:
        """Unflatten dictionary"""
        result = {}
        for key, value in flat_dict.items():
            keys = key.split(sep)
            d = result
            for k in keys[:-1]:
                if k not in d:
                    d[k] = {}
                d = d[k]
            d[keys[-1]] = value
        return result

# Streamlit session state integration
def get_storage_service():
    """Get storage service instance"""
    if 'storage_service' not in st.session_state:
        st.session_state.storage_service = StorageService()
    return st.session_state.storage_service

def migrate_session_data():
    """Migrate existing session data to database (one-time operation)"""
    if st.session_state.get('data_migrated', False):
        return
    
    storage = get_storage_service()
    
    # Check for existing projects in session state
    if 'projects' in st.session_state and st.session_state.projects:
        with st.spinner("Migrating existing data to persistent storage..."):
            success = storage.migrate_from_session_state(st.session_state.projects)
            if success:
                st.session_state.data_migrated = True
                st.success("Daten zu dauerhaftem Speicher migriert!")
            else:
                st.error("Migration der Daten fehlgeschlagen")