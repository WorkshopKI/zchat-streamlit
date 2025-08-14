# ChatBot v1.0 - Projektübersicht

## 📋 Übersicht

ChatBot v1.0 ist eine umfassende KI-Chat-Anwendung für Support-Ticket-Bearbeitung, entwickelt mit Streamlit. Die Anwendung bietet projektbasierte Organisation, Dokument-Integration und Unterstützung für mehrere KI-Provider.

## 🏗️ Projektstruktur

```
chat-streamlit-docs/
├── app.py                      # Hauptanwendung
├── pages/
│   └── Settings.py            # Einstellungsseite
├── config.json                # Hauptkonfiguration
├── config_manager.py          # Konfigurations-Management
├── config_utils.py            # CLI-Tools für Konfiguration
├── database.py                # SQLite-Datenbankschicht
├── storage_service.py         # Hochlevel Storage-Service
├── llm_integration.py         # KI-Provider-Integration
├── init_database.py           # Datenbank-Initialisierung
├── requirements.txt           # Python-Abhängigkeiten
├── chat-logo-system.png       # System-Avatar
├── chat-logo-user.png         # Benutzer-Avatar
├── sample_ticket.md           # Beispiel-Ticket
├── demo_*.md                  # Demo-Dokumente
└── docs/                      # Dokumentation
    ├── README.md
    ├── CONFIGURATION.md
    ├── DATABASE.md
    └── SETTINGS_PAGE.md
```

## 🎯 Kernfunktionen

### 1. Projektmanagement
- **Projektbasierte Organisation**: Jedes Projekt hat eigene Chats und Dokumente
- **Session-Verwaltung**: Mehrere Chat-Sessions pro Projekt
- **Persistente Speicherung**: SQLite-Datenbank für alle Daten

### 2. KI-Integration
- **LM Studio**: Lokale Modelle über OpenAI-kompatible API
- **OpenRouter**: Cloud-basierte Modelle (Claude, GPT-4, etc.)
- **Azure OpenAI**: Enterprise-KI-Lösung
- **Kontextuelle Antworten**: Integration von hochgeladenen Dokumenten

### 3. Dokument-Management
- **Multi-Format-Support**: PDF, DOCX, TXT, MD, etc.
- **Kontext-Integration**: Dokumente werden für KI-Antworten verwendet
- **Projektspezifisch**: Dokumente gehören zu spezifischen Projekten

### 4. Benutzeroberfläche
- **Deutsche Lokalisierung**: Vollständig deutsche Benutzeroberfläche
- **Responsive Design**: Funktioniert auf Desktop und Mobile
- **Intuitive Navigation**: Projektbaum in der Seitenleiste

## 🔧 Technische Architektur

### Anwendungsschichten

1. **Präsentationsschicht** (Streamlit)
   - `app.py`: Haupt-UI und Navigation
   - `pages/Settings.py`: Konfigurationsoberfläche

2. **Geschäftslogik**
   - `storage_service.py`: Hochlevel-Datenoperationen
   - `llm_integration.py`: KI-Provider-Abstraktion
   - `config_manager.py`: Konfigurationsverwaltung

3. **Datenschicht**
   - `database.py`: SQLite-Datenbankoperationen
   - `config.json`: Konfigurationsdaten

### Datenmodell

```sql
-- Haupttabellen
projects          # Projektmetadaten
chat_sessions     # Chat-Sessions pro Projekt
chat_messages     # Einzelne Nachrichten
documents         # Hochgeladene Dokumente
settings          # Anwendungseinstellungen
user_preferences  # Benutzereinstellungen
```

## 🚀 Installation und Setup

### Schnellstart

1. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

2. **Datenbank initialisieren**
   ```bash
   python init_database.py
   ```

3. **Anwendung starten**
   ```bash
   streamlit run app.py
   ```

### Konfiguration

1. **Über UI**: Einstellungsseite → AI-Provider konfigurieren
2. **Über CLI**: `python config_utils.py` für erweiterte Optionen
3. **Direkt**: `config.json` manuell bearbeiten

## 📊 Code-Qualität

### Dokumentation
- **Vollständige Docstrings**: Alle Funktionen dokumentiert
- **Typisierung**: Type hints für bessere Wartbarkeit
- **Kommentare**: Erklärung komplexer Logik

### Struktur
- **Modulare Architektur**: Klare Trennung der Verantwortlichkeiten
- **Einheitliche Schnittstellen**: Abstrakte Basisklassen
- **Fehlerbehandlung**: Robuste Error-Handling

### Standards
- **Deutsche Lokalisierung**: UI und Dokumentation
- **Konsistente Namensgebung**: Einheitliche Code-Konventionen
- **Clean Code**: Lesbarer und wartbarer Code

## 🔒 Sicherheit

- **Lokale Speicherung**: Alle Daten bleiben lokal
- **API-Schlüssel**: Sichere Konfigurationsverwaltung
- **Input-Validierung**: Schutz vor schädlichen Eingaben
- **Dateivalidierung**: Sichere Dokument-Uploads

## 🎛️ Konfigurationsoptionen

### KI-Provider
```json
{
  "llm_providers": {
    "default_provider": "lm_studio",
    "providers": {
      "lm_studio": { /* Lokale Modelle */ },
      "openrouter": { /* Cloud-Modelle */ },
      "azure_openai": { /* Enterprise */ }
    }
  }
}
```

### Anwendungseinstellungen
- **Datei-Upload**: Größenlimits, erlaubte Formate
- **Chat-Verhalten**: Streaming, Verlaufslimits
- **UI-Anpassungen**: Theme, Sprache
- **Performance**: Caching, Timeouts

## 📈 Erweiterbarkeit

### Neue KI-Provider hinzufügen
1. Neue Klasse in `llm_integration.py` erstellen
2. `LLMProvider` Basisklasse erweitern
3. Provider in `config.json` registrieren
4. UI-Integration in `Settings.py`

### Neue Funktionen
- **Plugin-System**: Modulare Erweiterungen möglich
- **API-Integration**: RESTful-Services anbindbar
- **Datenexport**: Verschiedene Exportformate
- **Automatisierung**: Workflow-Integration

## 🐛 Debugging und Wartung

### Logging
- **Strukturiertes Logging**: Python logging-Modul
- **Debug-Modi**: Ausführliche Fehlerinformationen
- **Performance-Monitoring**: Antwortzeiten verfolgen

### Datenbank-Tools
```bash
# Datenbank zurücksetzen
python init_database.py

# Konfiguration validieren
python config_utils.py validate

# Backup erstellen
sqlite3 chatbot.db ".backup backup.db"
```

## 📞 Support

Bei Fragen oder Problemen:
1. **Dokumentation**: Siehe README.md und docs/
2. **Konfiguration**: `python config_utils.py --help`
3. **Debug-Modus**: Detaillierte Fehlermeldungen aktivieren
4. **Logs prüfen**: Streamlit-Konsole für Fehlerdetails

---

**Version**: 1.0  
**Letzte Aktualisierung**: 2024  
**Sprache**: Deutsch  
**Framework**: Streamlit 1.28+