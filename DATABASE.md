# ChatBot v1.0 - Persistent Database Storage

## Overview

ChatBot v1.0 now uses **SQLite database** for persistent storage of projects, chats, settings, and documents. This ensures all your data is saved permanently and survives browser refreshes, app restarts, and system reboots.

## Features

### 🗄️ Persistent Storage
- **Projects**: All project information stored permanently
- **Chat History**: Full conversation history preserved across sessions
- **Documents**: Uploaded files and content stored in database
- **Settings**: AI provider configurations and user preferences
- **User Preferences**: Current project, UI settings, etc.

### 📊 Database Schema

#### Tables Created:
1. **projects** - Project metadata and information
2. **chat_messages** - All chat messages with timestamps
3. **documents** - Uploaded files and content
4. **settings** - Application configuration
5. **user_preferences** - User-specific preferences

### 🔧 Auto-Migration
- Existing session data automatically migrated to database on first run
- Seamless transition from memory-based to persistent storage
- No data loss during migration

## Setup Instructions

### 1. Initialize Database
```bash
python init_database.py
```

This script will:
- Create SQLite database (`chatbot.db`)
- Set up all required tables
- Save default configuration
- Create sample project with demo data

### 2. Run Application
```bash
streamlit run app.py
```

The app will automatically:
- Connect to the database
- Load saved projects and settings
- Migrate any existing session data

## Database Benefits

### ✅ Data Persistence
- **No data loss**: Projects and chats survive browser crashes
- **Cross-session**: Resume work exactly where you left off
- **Backup ready**: Single SQLite file contains all data

### ⚡ Performance
- **Fast queries**: Indexed database for quick access
- **Efficient storage**: Optimized schema design
- **Scalable**: Handles thousands of projects and messages

### 🔒 Data Integrity
- **ACID compliance**: SQLite ensures data consistency
- **Foreign keys**: Relational integrity maintained
- **Transactions**: Atomic operations prevent data corruption

## Database Operations

### Project Management
```python
# Create project
project_id = storage.create_project("My Project", "Description")

# Get all projects
projects = storage.get_all_projects()

# Get specific project
project = storage.get_project(project_id)

# Update project
storage.update_project(project_id, name="New Name")

# Delete project (soft delete)
storage.delete_project(project_id)
```

### Chat Messages
```python
# Add message
storage.add_message(project_id, "user", "Hello!")

# Get chat history
messages = storage.get_chat_history(project_id)

# Clear chat
storage.clear_chat_history(project_id)
```

### Documents
```python
# Add document
doc_id = storage.add_document(project_id, "file.txt", content, "text/plain", file_size)

# Get project documents
documents = storage.get_project_documents(project_id)

# Delete document
storage.delete_document(doc_id)
```

### Settings
```python
# Save settings
storage.save_settings(config_dict)

# Load settings
settings = storage.load_settings(default_config)

# User preferences
storage.save_user_preference("current_project", project_id)
current_project = storage.get_user_preference("current_project")
```

## Database File Location

- **File**: `chatbot.db`
- **Location**: Same directory as `app.py`
- **Size**: Starts at ~86KB, grows with data
- **Format**: SQLite 3.x database

## Backup & Export

### Manual Backup
```bash
# Copy database file
cp chatbot.db chatbot_backup_$(date +%Y%m%d).db
```

### Export Project Data
```python
# From application
storage = get_storage_service()
export_data = storage.export_project(project_id)

# Save to JSON
with open('project_export.json', 'w') as f:
    json.dump(export_data, f, indent=2)
```

### Database Statistics
```python
# Get usage stats
stats = storage.get_application_stats()
print(f"Projects: {stats['active_projects']}")
print(f"Messages: {stats['total_messages']}")
print(f"Documents: {stats['total_documents']}")
print(f"DB Size: {stats['database_size_mb']} MB")
```

## Migration Notes

### From Session Storage
- First run automatically detects session data
- Migrates projects, messages, and documents
- Sets migration flag to prevent re-migration
- Original session data preserved until confirmed working

### Settings Migration
- Configuration automatically saved to database
- User preferences preserved
- Provider settings maintained
- All customizations carried forward

## Troubleshooting

### Database Issues
```bash
# Check database integrity
sqlite3 chatbot.db "PRAGMA integrity_check;"

# View table structure
sqlite3 chatbot.db ".schema"

# Check table contents
sqlite3 chatbot.db "SELECT * FROM projects;"
```

### Performance Optimization
- Database includes indexes for common queries
- Regular VACUUM operation can reclaim space
- Consider backup rotation for large databases

### Reset Database
```bash
# Delete and reinitialize
rm chatbot.db
python init_database.py
```

## Security Considerations

### Data Protection
- Database file contains all application data
- No automatic encryption (consider OS-level encryption)
- API keys stored in database (consider environment variables for production)

### Access Control
- Single-user application design
- No built-in authentication
- Protect database file access at OS level

## Advanced Usage

### Custom Queries
```python
# Direct database access
db_manager = get_database_manager()
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE role = 'user'")
    user_messages = cursor.fetchone()[0]
```

### Database Maintenance
```python
# Backup database
storage.backup_database("backup_path.db")

# Get detailed stats
stats = storage.get_application_stats()

# Export all project data
for project in storage.get_all_projects():
    export_data = storage.export_project(project['id'])
    # Process export data...
```

---

## Technical Details

### Dependencies
- **SQLite**: Included with Python (no additional packages needed)
- **Streamlit**: Caching used for database connections
- **JSON**: Settings and metadata serialization

### Performance Characteristics
- **Concurrent Access**: Single-writer, multiple-reader design
- **Memory Usage**: Minimal - data streamed from disk
- **Scalability**: Handles 10,000+ projects efficiently

### Schema Versioning
- Initial version includes all required tables
- Future versions may include migration scripts
- Schema changes handled gracefully

---

*This persistent storage system ensures your ChatBot v1.0 data is safe, accessible, and ready for production use.*