# ChatBot v1.0 - Streamlit KI-Chat-Anwendung

Eine funktionsreiche Chat-Anwendung, erstellt mit Streamlit, die mehrere KI-Modelle, Projektmanagement, Dokument-Upload und vieles mehr unterstützt.

## 🚀 Funktionen

### Kernfunktionen
- **Echtzeit-Chat-Interface** mit Streaming-Antworten
- **Projektmanagement** mit lokalem Browser-Speicher  
- **Dokument-Upload und -Verarbeitung** (PDF, DOCX, TXT, MD, etc.)
- **Unterstützung mehrerer KI-Modelle** (LM Studio und OpenRouter)
- **Chat-Verlaufsverwaltung** lokal gespeichert
- **Hell/Dunkel-Theme** mit benutzerdefiniertem Farbsystem
- **Responsives Design** für mobile Geräte
- **Kontextbewusste Antworten** mit hochgeladenen Dokumenten

### Projektmanagement
- Projekte erstellen und löschen
- Projektspezifischer Chat-Verlauf und Dokumente
- Lokaler Browser-Speicher für Persistenz
- Chat-Gespräche exportieren

### KI-Modell-Unterstützung
- **LM Studio**: Verbindung zu lokalen Modellen
- **OpenRouter**: Zugang zu mehreren Cloud-Modellen einschließlich:
  - Claude 3.5 Sonnet
  - GPT-4
  - GPT-3.5 Turbo
  - Llama 3.1
  - Gemini Pro
  - And more...

## 📦 Installation

1. **Klonen oder herunterladen** der Anwendungsdateien:
   ```bash
   # Ensure you have these files:
   # - app.py
   # - llm_integration.py
   # - requirements.txt
   # - chat-logo-system.png
   # - chat-logo-user.png
   ```

2. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Anwendung ausführen**:
   ```bash
   streamlit run app.py
   ```

4. **Browser öffnen** und zu `http://localhost:8501` navigieren

## ⚙️ Konfiguration

Die Anwendung verwendet ein umfassendes Konfigurationssystem mit JSON-Dateien für einfache Anpassung.

### Konfigurationsdateien

- **`config.json`**: Hauptkonfigurationsdatei mit allen Einstellungen
- **`user_config.json`**: Benutzerspezifische Überschreibungen (automatisch erstellt)
- Konfiguration kann über UI oder Kommandozeilen-Tools verwaltet werden

### Schnelleinrichtung

#### Method 1: Using the UI (Recommended)
1. Start the application: `streamlit run app.py`
2. Open the **Settings** section in the sidebar
3. Configure your preferred AI provider
4. Click **Save Settings**

#### Method 2: Using Configuration Files

**LM Studio Setup:**
```json
{
  "llm_providers": {
    "default_provider": "lm_studio",
    "providers": {
      "lm_studio": {
        "enabled": true,
        "settings": {
          "base_url": "http://localhost:1234",
          "model_name": "llama-3.1-8b-instruct",
          "parameters": {
            "temperature": 0.7,
            "max_tokens": 2000
          }
        }
      }
    }
  }
}
```

**OpenRouter Setup:**
```json
{
  "llm_providers": {
    "default_provider": "openrouter", 
    "providers": {
      "openrouter": {
        "enabled": true,
        "settings": {
          "api_key": "your-api-key-here",
          "model_name": "anthropic/claude-3.5-sonnet",
          "parameters": {
            "temperature": 0.7,
            "max_tokens": 2000
          }
        }
      }
    }
  }
}
```

### Configuration Management CLI

Use the built-in configuration utilities:

```bash
# Validate configuration
python config_utils.py validate

# List all providers
python config_utils.py list

# Enable/disable providers
python config_utils.py disable azure_openai

# Set default provider
python config_utils.py default openrouter

# Reset to defaults
python config_utils.py reset

# Show current config
python config_utils.py show
```

### Supported AI Providers

The application supports multiple AI providers out of the box:

| Provider | Type | Status | Models Supported |
|----------|------|--------|------------------|
| **LM Studio** | Local | ✅ Enabled | Any GGUF model supported by LM Studio |
| **OpenRouter** | Cloud | ✅ Enabled | Claude, GPT-4, Llama, Gemini, Mixtral, and more |
| **Azure OpenAI** | Cloud | ⚙️ Available | GPT-3.5, GPT-4, and Azure-hosted models |

#### Provider-Specific Notes:

**LM Studio:**
- Requires LM Studio running locally
- Default port: 1234
- Supports any GGUF format model
- Best for privacy and offline usage

**OpenRouter:**
- Requires API key from [OpenRouter](https://openrouter.ai/)
- Access to multiple model providers
- Pay-per-use pricing
- Best for variety and latest models

**Azure OpenAI:**
- Requires Azure subscription and OpenAI service
- Enterprise features and compliance
- Custom deployment names supported

## 🎨 User Interface

### Navigation
- **Left Sidebar**: Project management, settings
- **Main Area**: Tabbed interface with Chat and Documents
- **Chat Tab**: Real-time conversation with AI
- **Documents Tab**: File upload and management

### Theme Support
- **Light Theme**: Clean, professional appearance
- **Dark Theme**: Easy on the eyes for extended use
- Switch themes in the Settings section

## 📝 Usage Guide

### Getting Started
1. **Create a Project**: Use the sidebar to create your first project
2. **Upload Documents** (optional): Switch to Documents tab and upload relevant files
3. **Start Chatting**: Return to Chat tab and begin your conversation
4. **Configure AI Model**: Adjust settings in the sidebar for your preferred AI provider

### Document Management
- **Supported Formats**: PDF, DOCX, XLSX, PPTX, TXT, MD
- **File Size Limit**: 200MB per file
- **Context Integration**: Uploaded documents provide context for AI responses
- **Character Count**: Display shows document size for reference

### Chat Features
- **Streaming Responses**: See AI responses as they're generated
- **Message History**: All conversations saved per project
- **Token Tracking**: Monitor usage with built-in counter
- **Export Functionality**: Download chat history as JSON

## 🔧 Advanced Settings

### Model Parameters
- **Temperature**: Control response creativity (0.0-2.0)
- **Max Tokens**: Set response length limit (100-4000)
- **Model Selection**: Choose from available models per provider

### Storage
- All data stored in browser's local storage
- No server-side data persistence
- Projects and chats persist between sessions
- Clear browser data to reset application

## 🧪 Testing

Run the included test script:
```bash
python test_app.py
```

This will verify:
- File existence
- LLM integration setup
- Create sample documents for testing

### Manual Testing Checklist
1. ✅ Create a new project
2. ✅ Upload a document (try the generated `sample_ticket.md`)
3. ✅ Send a chat message
4. ✅ Test streaming responses
5. ✅ Switch between light/dark themes
6. ✅ Try different AI models
7. ✅ Export chat history
8. ✅ Delete and recreate projects

## 🎯 Use Cases

### Support Ticket Processing
- Upload support tickets and documentation
- Get AI assistance for ticket analysis
- Generate response templates
- Track ticket resolution progress

### Document Analysis
- Upload research papers, reports, or manuals
- Ask questions about document content
- Generate summaries and insights
- Compare multiple documents

### Knowledge Management
- Create project-specific knowledge bases
- Organize documents by topic/project
- Search and reference information quickly
- Maintain conversation context

## 🔒 Security & Privacy

- **Local Storage**: All data stays in your browser
- **No Cloud Storage**: No data sent to external services (except AI API calls)
- **API Key Security**: Keys stored locally, not transmitted except to respective AI services
- **File Processing**: Documents processed locally before being sent as context

## 🚧 Troubleshooting

### Common Issues

**LM Studio Connection Failed**
- Ensure LM Studio is running
- Check the URL (usually http://localhost:1234)
- Verify a model is loaded and served

**OpenRouter API Errors**
- Verify API key is correct
- Check your OpenRouter account balance
- Ensure selected model is available

**File Upload Issues**
- Check file size (max 200MB)
- Verify file format is supported
- Try uploading one file at a time

**Theme Not Applying**
- Refresh the page after changing theme
- Clear browser cache if issues persist

## 📊 Technical Details

### Architecture
- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with requests for API calls
- **Storage**: Browser localStorage simulation via Streamlit session state
- **AI Integration**: RESTful APIs for both LM Studio and OpenRouter

### Dependencies
- streamlit >= 1.28.0
- requests >= 2.28.0
- Standard Python libraries (json, uuid, datetime, etc.)

## 🤝 Contributing

This is a complete implementation based on the provided requirements. For enhancements:

1. Fork the project
2. Create feature branches
3. Test thoroughly
4. Submit pull requests

## 📄 License

This project is provided as-is for educational and practical use.

---

**ChatBot v1.0** - Built with ❤️ using Streamlit