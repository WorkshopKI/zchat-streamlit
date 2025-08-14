# Settings Page - ChatBot v1.0

## Overview

The dedicated Settings page provides comprehensive configuration management for the ChatBot v1.0 application with advanced features for testing and managing AI providers.

## 🚀 New Features

### Dedicated Settings Page
- Accessible via "🔧 Open Settings Page" button in sidebar
- Organized into three main tabs: AI Providers, General Settings, Configuration

### LLM Provider Testing
- **Test Connection Button**: Test each provider with a real API call
- **Real-time Feedback**: Shows connection success/failure with response time
- **Error Reporting**: Detailed error messages for troubleshooting
- **Response Preview**: Shows sample response from the provider

### Universal API Configuration
- **API Endpoint**: Configurable base URL for all providers
- **API Key**: Optional authentication for all providers (including local ones)
- **Timeout Settings**: Adjustable connection timeouts
- **Retry Logic**: Configurable retry attempts

### Light Theme Only
- Removed theme switcher from UI
- Application always uses light theme
- Simplified interface and consistent appearance

## 🎯 Settings Page Structure

### Tab 1: 🤖 AI Providers

#### Default Provider Selection
- Choose which provider to use by default
- Only shows enabled providers
- Changes apply immediately

#### Per-Provider Configuration
For each provider (LM Studio, OpenRouter, Azure OpenAI):

**Basic Settings:**
- ✅/❌ Enable/Disable toggle
- 🧪 Test connection button with real-time results
- 🔄 Reload Models button to fetch latest available models
- 🌐 API Endpoint (base URL)
- 🔑 API Key (optional, password field)
- 🤖 Model Name/Selection (dynamically populated from reload)
- ⏱️ Timeout (10-300 seconds)

**Advanced Parameters:**
- Temperature (0.0-2.0)
- Max Tokens (100-4000)
- Top P (0.0-1.0)
- Provider-specific parameters

**Provider-Specific Settings:**
- **OpenRouter**: HTTP Referer, X-Title headers
- **Azure OpenAI**: API version, deployment name
- **LM Studio**: API version compatibility

### Tab 2: 🔧 General Settings

#### File Upload Configuration
- Max file size (1-1000 MB)
- Max files per project (1-200)

#### Chat Settings
- Max chat history display (10-200 messages)
- Enable/disable streaming responses

#### Performance Settings
- Enable/disable caching
- Max concurrent requests (1-20)

### Tab 3: 📊 Configuration

#### Configuration Management
- 💾 **Save Configuration**: Persist all settings
- 🔄 **Reset to Defaults**: Restore factory settings (with confirmation)
- 🔍 **Validate Config**: Check configuration integrity

#### Export/Import
- 📥 **Export**: Download current configuration as JSON
- 📤 **Import**: Upload and apply configuration file
- 🔍 **Preview**: View current configuration in JSON format

## 🧪 Provider Testing System

### Connection Test Process
1. Click "🧪 Test" button for any enabled provider
2. System sends test message: "Hello! Please respond with 'Test successful' to confirm the connection works."
3. Measures response time and captures output
4. Shows results immediately below the test button

### Model Reload Process
1. Click "🔄 Reload Models" button for any enabled provider
2. System queries the provider's API for available models
3. Displays count of found models and detailed list
4. Updates model selection dropdown with fresh options
5. Stores model list in configuration for future use

### Test Results
**Connection Test Success:**
- ✅ Green success message
- Response time in milliseconds
- Preview of actual response (truncated to 200 chars)

**Connection Test Failure:**
- ❌ Red error message
- Detailed error description
- Common issues: connection timeout, authentication failure, model not found

**Model Reload Success:**
- ✅ Green success message showing count of found models
- 📋 Expandable list showing available models with details
- Model selection dropdown automatically updated
- Models sorted by name for easy browsing

**Model Reload Failure:**
- ❌ Red error message with specific failure reason
- Guidance on how to resolve common issues

### Common Test Scenarios

**LM Studio:**
- Tests local server connectivity
- Verifies model is loaded and responding
- Checks API compatibility

**OpenRouter:**
- Validates API key
- Tests model availability
- Checks account credits/limits

- Tests model availability
- Checks API endpoint accessibility

**Azure OpenAI:**
- Validates deployment configuration
- Tests API key and endpoint
- Checks model deployment status

## 🔄 Model Reload Feature

### API Endpoints Used

The reload models functionality queries different API endpoints for each provider:

**LM Studio Models API:**
- Endpoint: `{base_url}/v1/models`
- Method: GET
- Returns: List of loaded models with metadata
- Authentication: Optional Bearer token

**OpenRouter Models API:**
- Endpoint: `{base_url}/models`
- Method: GET  
- Returns: Comprehensive model catalog with pricing, context length
- Authentication: Required Bearer token
- Additional Info: Model descriptions, capabilities, pricing

- Endpoint: `{base_url}/api/tags`
- Method: GET
- Returns: Locally installed models with size and modification info
- Authentication: Optional Bearer token

**Azure OpenAI Deployments API:**
- Endpoint: `{base_url}/openai/deployments?api-version={version}`
- Method: GET
- Returns: Active deployments with status and model info
- Authentication: Required api-key header

### Model Information Retrieved

**LM Studio:**
- Model ID/Name
- Owner information
- Creation timestamp
- Model status

**OpenRouter:**
- Model ID and display name
- Provider/owner
- Description and capabilities
- Context length (tokens)
- Pricing information (input/output)
- Creation date

- Model name and tag
- File size
- Last modified date
- Model digest/hash

**Azure OpenAI:**
- Deployment name
- Base model
- Deployment status
- Created/updated timestamps

### Smart Model Selection

After reloading models:
- Model dropdown automatically updates with fetched options
- Current selection preserved if still available
- New models appear in alphabetical order
- Unavailable models are removed from selection
- Fallback to text input if API fails

## 🔧 Configuration Best Practices

### API Endpoint Configuration
- **LM Studio**: `http://localhost:1234` (default)
- **OpenRouter**: `https://openrouter.ai/api/v1` (default)
- **Azure OpenAI**: `https://your-resource.openai.azure.com` (custom)

### API Key Management
- API keys are stored locally in browser storage
- Never committed to version control
- Optional for local providers (LM Studio)
- Required for cloud providers (OpenRouter, Azure OpenAI)

### Testing Workflow
1. Configure provider settings
2. Enable the provider
3. Click "Test" to verify connection
4. Fix any issues reported
5. Set as default provider if desired
6. Save configuration

## 🚨 Troubleshooting

### Common Issues

**Test Failed: Connection Timeout**
- Check if service is running (for local providers)
- Verify API endpoint URL
- Increase timeout value
- Check firewall/network settings

**Test Failed: Authentication Error**
- Verify API key is correct
- Check API key permissions
- Ensure account has sufficient credits (cloud providers)

**Test Failed: Model Not Found**
- Verify model name spelling
- Check if model is loaded (LM Studio)
- Confirm model availability (cloud providers)
- Try alternative model names

**Settings Not Saving**
- Click "Save Configuration" button
- Check browser storage permissions
- Verify write permissions for config files

### Debug Mode
Enable debug logging in configuration:
```json
{
  "logging": {
    "level": "DEBUG",
    "enable_file_logging": true
  }
}
```

## 📝 Migration Notes

### From Previous Version
- Old sidebar settings automatically migrated
- Theme preference reset to light mode
- All API configurations preserved
- Test functionality is new addition

### Configuration File Changes
- Added `api_key` field to all providers
- Added `force_light_theme` app setting
- Enhanced provider-specific settings
- Backward compatible with existing configs

---

The new Settings page provides professional-grade configuration management with real-time testing capabilities, making it easy to set up and troubleshoot AI provider connections.