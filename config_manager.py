import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st

class ConfigManager:
    """Configuration manager for ChatBot v1.0"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.user_config_file = "user_config.json"
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            # Load default config
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
            
            # Load user overrides if they exist
            if os.path.exists(self.user_config_file):
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.merge_config(user_config)
            
            logging.info("Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            self.config = self.get_default_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def save_user_config(self, user_settings: Dict[str, Any]):
        """Save user-specific configuration overrides"""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(user_settings, f, indent=2, ensure_ascii=False)
            logging.info("User configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving user configuration: {e}")
    
    def merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with default configuration"""
        def deep_merge(base_dict, override_dict):
            for key, value in override_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(self.config, user_config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file doesn't exist"""
        return {
            "app": {
                "title": "ChatBot v1.0",
                "theme": "light",
                "port": 8501
            },
            "llm_providers": {
                "default_provider": "lm_studio",
                "providers": {
                    "lm_studio": {
                        "enabled": True,
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
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'app.title')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_section = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config_section:
                config_section[key] = {}
            config_section = config_section[key]
        
        # Set the value
        config_section[keys[-1]] = value
    
    def get_llm_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific LLM provider"""
        return self.get(f"llm_providers.providers.{provider_name}", {})
    
    def get_enabled_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled LLM providers"""
        providers = self.get("llm_providers.providers", {})
        return {name: config for name, config in providers.items() 
                if config.get("enabled", False)}
    
    def get_default_provider(self) -> str:
        """Get the default LLM provider name"""
        return self.get("llm_providers.default_provider", "lm_studio")
    
    def update_provider_settings(self, provider_name: str, settings: Dict[str, Any]):
        """Update settings for a specific provider"""
        provider_config = self.get_llm_provider_config(provider_name)
        if provider_config:
            provider_config["settings"].update(settings)
            self.save_config()
    
    def validate_config(self) -> bool:
        """Validate configuration integrity"""
        required_sections = ["app", "llm_providers"]
        
        for section in required_sections:
            if section not in self.config:
                logging.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate LLM providers
        providers = self.get("llm_providers.providers", {})
        if not providers:
            logging.error("No LLM providers configured")
            return False
        
        default_provider = self.get_default_provider()
        if default_provider not in providers:
            logging.error(f"Default provider '{default_provider}' not found in providers")
            return False
        
        return True
    
    def create_user_settings_from_session(self) -> Dict[str, Any]:
        """Create user settings dictionary from Streamlit session state"""
        if 'settings' not in st.session_state:
            return {}
        
        session_settings = st.session_state.settings
        
        user_config = {
            "app": {
                "theme": session_settings.get("theme", "light")
            },
            "llm_providers": {
                "default_provider": session_settings.get("model_provider", "lm_studio"),
                "providers": {}
            }
        }
        
        # LM Studio settings
        if "lm_studio_url" in session_settings or "model_name" in session_settings:
            user_config["llm_providers"]["providers"]["lm_studio"] = {
                "settings": {
                    "base_url": session_settings.get("lm_studio_url", "http://localhost:1234"),
                    "model_name": session_settings.get("model_name", "llama-3.1-8b-instruct"),
                    "parameters": {
                        "temperature": session_settings.get("temperature", 0.7),
                        "max_tokens": session_settings.get("max_tokens", 2000)
                    }
                }
            }
        
        # OpenRouter settings
        if "openrouter_api_key" in session_settings or "openrouter_model" in session_settings:
            user_config["llm_providers"]["providers"]["openrouter"] = {
                "settings": {
                    "api_key": session_settings.get("openrouter_api_key", ""),
                    "model_name": session_settings.get("openrouter_model", "anthropic/claude-3.5-sonnet"),
                    "parameters": {
                        "temperature": session_settings.get("temperature", 0.7),
                        "max_tokens": session_settings.get("max_tokens", 2000)
                    }
                }
            }
        
        return user_config
    
    def sync_with_session_state(self):
        """Sync configuration with Streamlit session state"""
        if 'settings' not in st.session_state:
            st.session_state.settings = {}
        
        # Sync app settings
        st.session_state.settings['theme'] = self.get("app.theme", "light")
        
        # Sync LLM provider settings
        default_provider = self.get_default_provider()
        st.session_state.settings['model_provider'] = default_provider
        
        # Sync provider-specific settings
        if default_provider == "lm_studio":
            lm_config = self.get_llm_provider_config("lm_studio")
            if lm_config:
                settings = lm_config.get("settings", {})
                st.session_state.settings['lm_studio_url'] = settings.get("base_url", "http://localhost:1234")
                st.session_state.settings['model_name'] = settings.get("model_name", "llama-3.1-8b-instruct")
                
                params = settings.get("parameters", {})
                st.session_state.settings['temperature'] = params.get("temperature", 0.7)
                st.session_state.settings['max_tokens'] = params.get("max_tokens", 2000)
        
        elif default_provider == "openrouter":
            or_config = self.get_llm_provider_config("openrouter")
            if or_config:
                settings = or_config.get("settings", {})
                st.session_state.settings['openrouter_api_key'] = settings.get("api_key", "")
                st.session_state.settings['openrouter_model'] = settings.get("model_name", "anthropic/claude-3.5-sonnet")
                
                params = settings.get("parameters", {})
                st.session_state.settings['temperature'] = params.get("temperature", 0.7)
                st.session_state.settings['max_tokens'] = params.get("max_tokens", 2000)

def create_config_template():
    """Create a configuration template file"""
    template_path = "config_template.json"
    config_manager = ConfigManager()
    
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(config_manager.get_default_config(), f, indent=2, ensure_ascii=False)
    
    return template_path

# Global configuration instance
config = ConfigManager()