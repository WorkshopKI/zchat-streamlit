#!/usr/bin/env python3
"""
Database models and operations for ChatBot v1.0
Provides persistent storage for projects, chats, and settings using SQLite
"""

import sqlite3
import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import os

class DatabaseManager:
    """Manages SQLite database operations for the ChatBot application"""
    
    def __init__(self, db_path: str = "chatbot.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def get_connection(self):
        """Get SQLite database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Chat sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            ''')
            
            # Chat messages table (enhanced with session support)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    session_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_project_id ON chat_messages(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_messages(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON chat_sessions(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_active ON chat_sessions(is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(is_active)')
            
            conn.commit()
            self.logger.info("Database initialized successfully")

    # Project operations
    def create_project(self, project_id: str, name: str, description: str = "", metadata: Dict = None) -> bool:
        """Create a new project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (id, name, description, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, name, description, json.dumps(metadata or {})))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error creating project: {e}")
            return False
    
    def get_projects(self, active_only: bool = True) -> List[Dict]:
        """Get all projects"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if active_only:
                    cursor.execute('SELECT * FROM projects WHERE is_active = 1 ORDER BY updated_at DESC')
                else:
                    cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
                
                columns = [desc[0] for desc in cursor.description]
                projects = []
                for row in cursor.fetchall():
                    project = dict(zip(columns, row))
                    if project['metadata']:
                        project['metadata'] = json.loads(project['metadata'])
                    projects.append(project)
                return projects
        except sqlite3.Error as e:
            self.logger.error(f"Error getting projects: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    project = dict(zip(columns, row))
                    if project['metadata']:
                        project['metadata'] = json.loads(project['metadata'])
                    return project
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting project: {e}")
            return None
    
    def update_project(self, project_id: str, name: str = None, description: str = None, metadata: Dict = None) -> bool:
        """Update project details"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)
                if metadata is not None:
                    updates.append("metadata = ?")
                    params.append(json.dumps(metadata))
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(project_id)
                
                query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating project: {e}")
            return False
    
    def delete_project(self, project_id: str, soft_delete: bool = True) -> bool:
        """Delete a project (soft delete by default)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if soft_delete:
                    cursor.execute('UPDATE projects SET is_active = 0 WHERE id = ?', (project_id,))
                else:
                    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting project: {e}")
            return False

    # Chat session operations
    def create_chat_session(self, session_id: str, project_id: str, name: str) -> bool:
        """Create a new chat session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chat_sessions (id, project_id, name)
                    VALUES (?, ?, ?)
                ''', (session_id, project_id, name))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error creating chat session: {e}")
            return False
    
    def get_project_sessions(self, project_id: str) -> List[Dict]:
        """Get all sessions for a project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM chat_sessions 
                    WHERE project_id = ? AND is_active = 1 
                    ORDER BY updated_at DESC
                ''', (project_id,))
                
                columns = [desc[0] for desc in cursor.description]
                sessions = []
                for row in cursor.fetchall():
                    session = dict(zip(columns, row))
                    sessions.append(session)
                return sessions
        except sqlite3.Error as e:
            self.logger.error(f"Error getting project sessions: {e}")
            return []
    
    def update_session_message_count(self, session_id: str) -> bool:
        """Update message count for a session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE chat_sessions 
                    SET message_count = (
                        SELECT COUNT(*) FROM chat_messages 
                        WHERE session_id = ?
                    ),
                    updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (session_id, session_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error updating session message count: {e}")
            return False
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a chat session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE chat_sessions 
                    SET name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_name, session_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error renaming session: {e}")
            return False
    
    def delete_session(self, session_id: str, soft_delete: bool = True) -> bool:
        """Delete a chat session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if soft_delete:
                    cursor.execute('UPDATE chat_sessions SET is_active = 0 WHERE id = ?', (session_id,))
                else:
                    cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting session: {e}")
            return False

    # Chat message operations (enhanced with session support)
    def add_chat_message(self, project_id: str, role: str, content: str, metadata: Dict = None, session_id: str = None) -> bool:
        """Add a chat message to a project and session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chat_messages (project_id, session_id, role, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, session_id, role, content, json.dumps(metadata or {})))
                
                # Update session message count if session provided
                if session_id:
                    self.update_session_message_count(session_id)
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding chat message: {e}")
            return False
    
    def get_chat_messages(self, project_id: str, limit: int = None, session_id: str = None) -> List[Dict]:
        """Get chat messages for a project or specific session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if session_id:
                    query = 'SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC'
                    params = (session_id,)
                else:
                    query = 'SELECT * FROM chat_messages WHERE project_id = ? ORDER BY timestamp ASC'
                    params = (project_id,)
                
                if limit:
                    query += f' LIMIT {limit}'
                
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                messages = []
                for row in cursor.fetchall():
                    message = dict(zip(columns, row))
                    if message['metadata']:
                        message['metadata'] = json.loads(message['metadata'])
                    messages.append(message)
                return messages
        except sqlite3.Error as e:
            self.logger.error(f"Error getting chat messages: {e}")
            return []
    
    def clear_chat_messages(self, project_id: str) -> bool:
        """Clear all chat messages for a project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM chat_messages WHERE project_id = ?', (project_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error clearing chat messages: {e}")
            return False

    # Document operations
    def add_document(self, doc_id: str, project_id: str, filename: str, content: str, 
                    file_type: str, file_size: int, metadata: Dict = None) -> bool:
        """Add a document to a project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO documents (id, project_id, filename, content, file_type, file_size, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (doc_id, project_id, filename, content, file_type, file_size, json.dumps(metadata or {})))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding document: {e}")
            return False
    
    def get_documents(self, project_id: str) -> List[Dict]:
        """Get all documents for a project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM documents WHERE project_id = ? ORDER BY upload_date DESC', 
                             (project_id,))
                columns = [desc[0] for desc in cursor.description]
                documents = []
                for row in cursor.fetchall():
                    doc = dict(zip(columns, row))
                    if doc['metadata']:
                        doc['metadata'] = json.loads(doc['metadata'])
                    documents.append(doc)
                return documents
        except sqlite3.Error as e:
            self.logger.error(f"Error getting documents: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting document: {e}")
            return False

    # Settings operations
    def set_setting(self, key: str, value: Any, description: str = "") -> bool:
        """Set a setting value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, description, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value), description))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error setting configuration: {e}")
            return False
    
    def get_setting(self, key: str, default=None) -> Any:
        """Get a setting value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
        except sqlite3.Error as e:
            self.logger.error(f"Error getting setting: {e}")
            return default
    
    def get_all_settings(self) -> Dict:
        """Get all settings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT key, value FROM settings')
                settings = {}
                for key, value in cursor.fetchall():
                    settings[key] = json.loads(value)
                return settings
        except sqlite3.Error as e:
            self.logger.error(f"Error getting all settings: {e}")
            return {}

    # User preferences operations
    def set_user_preference(self, key: str, value: Any) -> bool:
        """Set a user preference"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value)))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error setting user preference: {e}")
            return False
    
    def get_user_preference(self, key: str, default=None) -> Any:
        """Get a user preference"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
        except sqlite3.Error as e:
            self.logger.error(f"Error getting user preference: {e}")
            return default

    # Utility operations
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count projects
                cursor.execute('SELECT COUNT(*) FROM projects WHERE is_active = 1')
                stats['active_projects'] = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute('SELECT COUNT(*) FROM chat_messages')
                stats['total_messages'] = cursor.fetchone()[0]
                
                # Count documents
                cursor.execute('SELECT COUNT(*) FROM documents')
                stats['total_documents'] = cursor.fetchone()[0]
                
                # Count settings
                cursor.execute('SELECT COUNT(*) FROM settings')
                stats['total_settings'] = cursor.fetchone()[0]
                
                # Database size
                if os.path.exists(self.db_path):
                    stats['database_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
                else:
                    stats['database_size_mb'] = 0
                
                return stats
        except sqlite3.Error as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
    
    def export_project_data(self, project_id: str) -> Dict:
        """Export all data for a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {}
            
            messages = self.get_chat_messages(project_id)
            documents = self.get_documents(project_id)
            
            return {
                'project': project,
                'messages': messages,
                'documents': documents,
                'export_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error exporting project data: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return False

# Streamlit connection setup
@st.cache_resource
def get_database_manager():
    """Get database manager instance with caching"""
    return DatabaseManager()

def clear_database_cache():
    """Clear the cached database manager instance"""
    get_database_manager.clear()

def init_streamlit_database():
    """Initialize database for Streamlit app"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_database_manager()
    return st.session_state.db_manager