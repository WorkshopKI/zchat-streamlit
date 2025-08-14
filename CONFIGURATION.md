# ChatBot v1.0 - Configuration System

## Overview

The ChatBot v1.0 application now includes a comprehensive configuration system that allows for easy customization and management of settings, AI providers, and application behavior.

## 🔧 Configuration Files

### Main Configuration File (`config.json`)

Contains all default settings for the application:

- **Application Settings**: Theme, title, port configuration
- **UI Settings**: Layout, avatars, display options
- **Storage Settings**: Local storage behavior, limits
- **File Upload Settings**: Size limits, allowed extensions
- **LLM Provider Settings**: Complete provider configurations
- **Feature Flags**: Enable/disable specific features
- **Performance Settings**: Caching, timeouts, concurrency
- **Security Settings**: Input validation, file scanning
- **Logging Settings**: Log levels, file output

### User Configuration File (`user_config.json`)

Auto-generated file containing user-specific overrides:
- Personal API keys
- Preferred settings
- Custom model configurations
- Theme preferences

## 🤖 LLM Provider System

### Supported Providers

1. **LM Studio** (Local)
   - Local model serving
   - GGUF format support
   - Privacy-focused
   - No API costs

2. **OpenRouter** (Cloud)
   - Access to multiple models
   - Claude, GPT-4, Llama, Gemini
   - Pay-per-use pricing
   - Latest model access

   - Open source local serving
   - Easy model management
   - Free to use
   - Community models

4. **Azure OpenAI** (Cloud)
   - Enterprise features
   - Compliance and security
   - Custom deployments
   - Azure integration

### Provider Configuration Structure

```json
{
  "provider_name": {
    "name": "Display Name",
    "type": "local|cloud",
    "enabled": true|false,
    "settings": {
      "base_url": "http://api.endpoint",
      "api_key": "optional-api-key",
      "model_name": "model-identifier",
      "timeout": 60,
      "max_retries": 3,
      "stream": true,
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
      }
    }
  }
}
```

## 🛠️ Configuration Management

### Via User Interface

1. **Settings Panel**: Access through sidebar
2. **Real-time Updates**: Changes applied immediately
3. **Save Function**: Persist settings to user config
4. **Validation**: Built-in validation for settings

### Via Command Line

Use the `config_utils.py` tool for advanced management:

```bash
# Validate configuration
python config_utils.py validate

# List all providers and their status
python config_utils.py list

# Enable or disable providers
python config_utils.py disable azure_openai

# Set default provider
python config_utils.py default openrouter

# Reset configuration to defaults
python config_utils.py reset

# View current configuration
python config_utils.py show

# Create provider template
python config_utils.py template custom_provider
```

### Programmatic Access

```python
from config_manager import ConfigManager

# Initialize configuration manager
config = ConfigManager()

# Get configuration values
theme = config.get('app.theme', 'light')
providers = config.get_enabled_providers()

# Set configuration values
config.set('app.theme', 'dark')
config.save_config()

# Work with providers
provider_config = config.get_llm_provider_config('openrouter')
config.update_provider_settings('lm_studio', {'base_url': 'http://localhost:1234'})
```

## 🎯 Configuration Best Practices

### Security
- **Never commit API keys** to version control
- Use `user_config.json` for sensitive settings
- API keys are stored locally only
- Input validation enabled by default

### Performance
- **Caching enabled** by default for better performance
- Configurable timeouts and retry limits
- Connection pooling for cloud providers
- Lazy loading for large configurations

### Customization
- **Modular design** allows easy extension
- Provider templates for new integrations
- Feature flags for experimental features
- Flexible parameter system

### Backup and Recovery
- **Automatic backups** of user settings
- Configuration validation before save
- Reset functionality for corrupted configs
- Import/export capabilities

## 🔄 Configuration Lifecycle

1. **Application Start**:
   - Load `config.json` (defaults)
   - Merge `user_config.json` (overrides)
   - Validate configuration
   - Initialize providers

2. **User Interaction**:
   - UI changes update session state
   - Validation in real-time
   - Auto-save on significant changes

3. **Application Shutdown**:
   - Save user preferences
   - Create backup if needed
   - Clean temporary settings

## 🚀 Advanced Features

### Dynamic Provider Loading
- Providers loaded based on configuration
- Runtime enable/disable without restart
- Automatic fallback to backup providers

### Configuration Inheritance
- Base configuration provides defaults
- User configuration overrides specific values
- Environment variables can override config

### Validation System
- JSON schema validation
- Provider-specific validation
- Real-time error reporting
- Automatic correction suggestions

### Extension System
- Plugin architecture for new providers
- Custom parameter types
- Middleware support for preprocessing
- Event hooks for configuration changes

## 📊 Configuration Schema

The complete configuration schema is available in `config.json` with detailed comments and examples for each setting. Key sections include:

- `app`: Application-level settings
- `ui`: User interface customization
- `storage`: Data storage configuration  
- `file_upload`: File handling settings
- `llm_providers`: AI provider configurations
- `features`: Feature flag management
- `performance`: Performance tuning
- `security`: Security settings
- `logging`: Logging configuration

For detailed parameter descriptions and examples, refer to the main `config.json` file.

## 🔍 Troubleshooting

### Common Issues

**Configuration Not Loading**
- Check file permissions
- Validate JSON syntax
- Ensure file encoding is UTF-8

**Provider Not Working**
- Verify provider is enabled
- Check API keys and URLs
- Confirm model names are correct

**Settings Not Persisting**
- Ensure write permissions
- Check available disk space
- Verify backup creation

**Performance Issues**
- Adjust timeout settings
- Enable caching
- Reduce max_tokens if needed

### Debug Mode

Enable debug logging to troubleshoot issues:

```json
{
  "logging": {
    "level": "DEBUG",
    "enable_file_logging": true
  }
}
```

---

This configuration system provides the flexibility and control needed for a professional AI chat application while maintaining ease of use for both developers and end users.