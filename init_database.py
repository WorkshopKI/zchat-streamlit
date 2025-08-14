#!/usr/bin/env python3
"""
Database initialization script for ChatBot v1.0
Run this script to set up the SQLite database with sample data
"""

import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from storage_service import StorageService
from config_manager import ConfigManager
import json

def init_database():
    """Initialize database with default configuration"""
    print("Initialisiere ChatBot v1.0 Datenbank...")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager()
    storage = StorageService()
    config_manager = ConfigManager()
    
    print("✅ Datenbanktabellen erfolgreich erstellt")
    
    # Load and save default configuration
    default_config = config_manager.config
    success = storage.save_settings(default_config)
    
    if success:
        print("✅ Standardkonfiguration in Datenbank gespeichert")
    else:
        print("❌ Fehler beim Speichern der Standardkonfiguration")
    
    # Get database statistics
    stats = storage.get_application_stats()
    
    print("\n📊 Datenbankstatistiken:")
    print(f"   • Aktive Projekte: {stats['active_projects']}")
    print(f"   • Gesamte Nachrichten: {stats['total_messages']}")
    print(f"   • Gesamte Dokumente: {stats['total_documents']}")
    print(f"   • Datenbankgröße: {stats['database_size_mb']} MB")
    
    print("\n🚀 Datenbankinitialisierung abgeschlossen!")
    print("Sie können nun die Anwendung starten mit: streamlit run app.py")

def create_sample_project():
    """Create a sample project with demo data"""
    print("\nErstelle Beispielprojekt...")
    
    storage = StorageService()
    
    # Create sample project
    project_id = storage.create_project(
        "Demo-Projekt", 
        "Ein Beispielprojekt zur Demonstration der ChatBot-Funktionalität"
    )
    
    # Create a default chat session
    session_id = storage.create_chat_session(project_id, "Haupt-Chat")
    
    # Add sample messages to the session
    sample_messages = [
        ("user", "Hallo! Ich brauche Hilfe bei einem Support-Ticket."),
        ("assistant", "Hallo! Ich bin hier, um Ihnen bei der Support-Ticket-Bearbeitung zu helfen. Mit welcher Phase der Bearbeitung möchten Sie arbeiten?\n\n1) **ErstCheck**\n2) **IntensivCheck**\n3) **3rd Level SupportCheck**"),
        ("user", "Lassen Sie uns mit dem ErstCheck beginnen."),
        ("assistant", "Großartig! Für die ErstCheck-Phase helfe ich Ihnen bei der ersten Bewertung. Bitte geben Sie mir die Support-Ticket-Details oder laden Sie relevante Dokumente hoch.")
    ]
    
    for role, content in sample_messages:
        storage.add_message(project_id, role, content, session_id=session_id)
    
    # Add sample document
    sample_doc_content = """# Beispiel Support-Ticket

**Ticket ID:** ST-2024-001
**Priorität:** Hoch
**Kategorie:** Technisches Problem

## Problembeschreibung
Kunde erlebt Verbindungszeitüberschreitungen beim Zugriff auf die Anwendung während der Spitzenzeiten.

## Umgebung
- Anwendungsversion: 2.1.3
- Browser: Chrome 120.0
- Betriebssystem: Windows 11

## Schritte zur Reproduktion
1. In die Anwendung einloggen
2. Zum Dashboard navigieren
3. Versuchen, Daten während der 9-11 Uhr Zeitspanne zu laden
4. Verbindungszeitüberschreitung tritt auf

## Erwartetes Verhalten
Anwendung sollte innerhalb von 3 Sekunden laden

## Tatsächliches Verhalten
Verbindung überschreitet die Zeit nach 30 Sekunden

## Kundenauswirkung
Zugriff auf kritische Geschäftsdaten während der Morgenstunden nicht möglich
"""
    
    storage.add_document(
        project_id, 
        "beispiel_ticket.md", 
        sample_doc_content, 
        "text/markdown", 
        len(sample_doc_content.encode('utf-8'))
    )
    
    print(f"✅ Beispielprojekt erstellt: {project_id}")
    print("   • 4 Beispielnachrichten hinzugefügt")
    print("   • 1 Beispieldokument hinzugefügt")
    
    return project_id

def main():
    """Main initialization function"""
    print("ChatBot v1.0 Datenbank-Setup")
    print("=" * 30)
    
    # Check if database already exists
    if os.path.exists("chatbot.db"):
        print("Datenbank existiert bereits. Initialisiere neu...")
        os.remove("chatbot.db")
        print("Bestehende Datenbank entfernt.")
    
    # Initialize database
    init_database()
    
    # Create sample data automatically
    print("\nErstelle Beispielprojekt mit Demodaten...")
    create_sample_project()
    
    print("\n" + "=" * 50)
    print("🎉 Setup abgeschlossen! Ihre ChatBot-Datenbank ist bereit.")
    print("\nNächste Schritte:")
    print("1. Ausführen: streamlit run app.py")
    print("2. Gehen Sie zur Einstellungsseite, um AI-Provider zu konfigurieren")
    print("3. Beginnen Sie zu chatten mit Ihrem AI-Assistenten!")

if __name__ == "__main__":
    main()