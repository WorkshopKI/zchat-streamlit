#!/usr/bin/env python3
"""
Configuration utilities for ChatBot v1.0
Provides command-line tools for managing configuration
"""

import argparse
import json
import sys
from pathlib import Path
from config_manager import ConfigManager

def validate_config(config_file: str = "config.json"):
    """Validate configuration file"""
    print(f"🔍 Validating configuration: {config_file}")
    
    try:
        config_manager = ConfigManager(config_file)
        if config_manager.validate_config():
            print("✅ Configuration is valid")
            
            # Show summary
            enabled_providers = config_manager.get_enabled_providers()
            print(f"\n📊 Configuration Summary:")
            print(f"   Default Provider: {config_manager.get_default_provider()}")
            print(f"   Enabled Providers: {', '.join(enabled_providers.keys())}")
            print(f"   Theme: {config_manager.get('app.theme', 'light')}")
            
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False

def reset_config(config_file: str = "config.json"):
    """Reset configuration to defaults"""
    print(f"🔄 Resetting configuration: {config_file}")
    
    try:
        config_manager = ConfigManager()
        config_manager.config = config_manager.get_default_config()
        config_manager.config_file = config_file
        config_manager.save_config()
        print("✅ Configuration reset to defaults")
        return True
    except Exception as e:
        print(f"❌ Error resetting configuration: {e}")
        return False

def show_config(config_file: str = "config.json"):
    """Show current configuration"""
    print(f"📋 Current configuration: {config_file}")
    
    try:
        config_manager = ConfigManager(config_file)
        print(json.dumps(config_manager.config, indent=2))
        return True
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def create_provider_template(provider_name: str):
    """Create a configuration template for a new provider"""
    print(f"📝 Creating template for provider: {provider_name}")
    
    template = {
        "name": provider_name.title(),
        "type": "cloud",  # or "local"
        "enabled": False,
        "settings": {
            "base_url": "",
            "api_key": "",
            "model_name": "",
            "timeout": 60,
            "max_retries": 3,
            "stream": True,
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": None
            }
        }
    }
    
    template_file = f"{provider_name}_template.json"
    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Template created: {template_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return False

def enable_provider(provider_name: str, config_file: str = "config.json"):
    """Enable a provider in the configuration"""
    print(f"🔧 Enabling provider: {provider_name}")
    
    try:
        config_manager = ConfigManager(config_file)
        provider_config = config_manager.get_llm_provider_config(provider_name)
        
        if not provider_config:
            print(f"❌ Provider '{provider_name}' not found in configuration")
            return False
        
        config_manager.set(f"llm_providers.providers.{provider_name}.enabled", True)
        config_manager.save_config()
        print(f"✅ Provider '{provider_name}' enabled")
        return True
    except Exception as e:
        print(f"❌ Error enabling provider: {e}")
        return False

def disable_provider(provider_name: str, config_file: str = "config.json"):
    """Disable a provider in the configuration"""
    print(f"🔧 Disabling provider: {provider_name}")
    
    try:
        config_manager = ConfigManager(config_file)
        provider_config = config_manager.get_llm_provider_config(provider_name)
        
        if not provider_config:
            print(f"❌ Provider '{provider_name}' not found in configuration")
            return False
        
        config_manager.set(f"llm_providers.providers.{provider_name}.enabled", False)
        config_manager.save_config()
        print(f"✅ Provider '{provider_name}' disabled")
        return True
    except Exception as e:
        print(f"❌ Error disabling provider: {e}")
        return False

def list_providers(config_file: str = "config.json"):
    """List all configured providers"""
    print(f"📋 Configured providers in: {config_file}")
    
    try:
        config_manager = ConfigManager(config_file)
        providers = config_manager.get("llm_providers.providers", {})
        default_provider = config_manager.get_default_provider()
        
        print(f"\nDefault Provider: {default_provider}")
        print(f"{'Provider':<15} {'Status':<8} {'Type':<6} {'Name'}")
        print("-" * 45)
        
        for provider_id, config in providers.items():
            status = "✅ Enabled" if config.get("enabled", False) else "❌ Disabled"
            provider_type = config.get("type", "unknown")
            name = config.get("name", provider_id.title())
            default_mark = "🔹" if provider_id == default_provider else "  "
            
            print(f"{default_mark}{provider_id:<13} {status:<8} {provider_type:<6} {name}")
        
        return True
    except Exception as e:
        print(f"❌ Error listing providers: {e}")
        return False

def set_default_provider(provider_name: str, config_file: str = "config.json"):
    """Set the default provider"""
    print(f"🔧 Setting default provider: {provider_name}")
    
    try:
        config_manager = ConfigManager(config_file)
        provider_config = config_manager.get_llm_provider_config(provider_name)
        
        if not provider_config:
            print(f"❌ Provider '{provider_name}' not found in configuration")
            return False
        
        if not provider_config.get("enabled", False):
            print(f"⚠️  Provider '{provider_name}' is disabled. Enable it first.")
            return False
        
        config_manager.set("llm_providers.default_provider", provider_name)
        config_manager.save_config()
        print(f"✅ Default provider set to '{provider_name}'")
        return True
    except Exception as e:
        print(f"❌ Error setting default provider: {e}")
        return False

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="ChatBot v1.0 Configuration Manager")
    parser.add_argument("--config", "-c", default="config.json", help="Configuration file path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate configuration file")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset configuration to defaults")
    
    # Show command
    subparsers.add_parser("show", help="Show current configuration")
    
    # Template command
    template_parser = subparsers.add_parser("template", help="Create provider template")
    template_parser.add_argument("provider", help="Provider name")
    
    # Enable/Disable commands
    enable_parser = subparsers.add_parser("enable", help="Enable a provider")
    enable_parser.add_argument("provider", help="Provider name")
    
    disable_parser = subparsers.add_parser("disable", help="Disable a provider")
    disable_parser.add_argument("provider", help="Provider name")
    
    # List command
    subparsers.add_parser("list", help="List all providers")
    
    # Default command
    default_parser = subparsers.add_parser("default", help="Set default provider")
    default_parser.add_argument("provider", help="Provider name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute commands
    success = False
    
    if args.command == "validate":
        success = validate_config(args.config)
    elif args.command == "reset":
        success = reset_config(args.config)
    elif args.command == "show":
        success = show_config(args.config)
    elif args.command == "template":
        success = create_provider_template(args.provider)
    elif args.command == "enable":
        success = enable_provider(args.provider, args.config)
    elif args.command == "disable":
        success = disable_provider(args.provider, args.config)
    elif args.command == "list":
        success = list_providers(args.config)
    elif args.command == "default":
        success = set_default_provider(args.provider, args.config)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())