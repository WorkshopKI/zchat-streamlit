#!/usr/bin/env python3
"""
ChatBot v1.0 - LLM-Integration
============================

LLM-Provider-Integration für verschiedene KI-Services.

Unterstützte Provider:
- LM Studio (lokal)
- OpenRouter (cloud)
- Azure OpenAI (cloud)

Jeder Provider implementiert die einheitliche LLMProvider-Schnittstelle
für nahtlose Integration und Auswechselbarkeit.

Autor: ChatBot v1.0 Team
Version: 1.0
"""

import requests
import json
import streamlit as st
from typing import Dict, List, Generator, Optional, Any
import time
import logging
from config_manager import ConfigManager

# ============================================================================
# BASISKLASSEN
# ============================================================================

class LLMProvider:
    """
    Basisklasse für alle LLM-Provider.
    
    Definiert die einheitliche Schnittstelle, die alle Provider implementieren müssen.
    Verwaltet gemeinsame Konfiguration und Parameter.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.settings = config.get("settings", {})
        self.parameters = self.settings.get("parameters", {})
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_response(self, messages: List[Dict], stream: bool = True) -> Generator[str, None, None]:
        """
        Generiert eine Antwort vom LLM.
        
        Args:
            messages (List[Dict]): Chat-Nachrichten im OpenAI-Format
            stream (bool): Ob Streaming verwendet werden soll
            
        Yields:
            str: Antwort-Chunks (bei Streaming) oder komplette Antwort
            
        Raises:
            NotImplementedError: Muss von Unterklassen implementiert werden
        """
        raise NotImplementedError
    
    def get_parameter(self, key: str, default=None):
        """
        Ruft einen Parameter-Wert mit Fallback-Logik ab.
        
        Args:
            key (str): Parameter-Schlüssel
            default: Standardwert falls nicht gefunden
            
        Returns:
            Any: Parameter-Wert oder Standardwert
        """
        return self.parameters.get(key, self.settings.get(key, default))

# ============================================================================
# PROVIDER-IMPLEMENTIERUNGEN
# ============================================================================

class LMStudioProvider(LLMProvider):
    """
    LM Studio Provider für lokale Modelle.
    
    Verbindet sich mit einer lokalen LM Studio-Instanz über deren OpenAI-kompatible API.
    Standardmäßig auf Port 1234.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.settings.get('base_url', 'http://localhost:1234')
        self.model_name = self.settings.get('model_name', 'llama-3.1-8b-instruct')
        self.timeout = self.settings.get('timeout', 30)
        self.max_retries = self.settings.get('max_retries', 3)
    
    def generate_response(self, messages: List[Dict], stream: bool = True) -> Generator[str, None, None]:
        """Generate response from LM Studio"""
        try:
            url = f"{self.base_url}/v1/chat/completions"
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.get_parameter('temperature', 0.7),
                "max_tokens": self.get_parameter('max_tokens', 2000),
                "top_p": self.get_parameter('top_p', 0.9),
                "frequency_penalty": self.get_parameter('frequency_penalty', 0.0),
                "presence_penalty": self.get_parameter('presence_penalty', 0.0),
                "stream": stream
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add API key if provided
            if self.settings.get('api_key'):
                headers["Authorization"] = f"Bearer {self.settings['api_key']}"
            
            if stream:
                response = requests.post(url, json=payload, headers=headers, stream=True)
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']
                    
        except requests.RequestException as e:
            yield f"Error connecting to LM Studio: {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"

class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.settings.get('base_url', 'https://openrouter.ai/api/v1')
        self.api_key = self.settings.get('api_key', '')
        self.model_name = self.settings.get('model_name', 'anthropic/claude-3.5-sonnet')
        self.timeout = self.settings.get('timeout', 60)
        self.max_retries = self.settings.get('max_retries', 3)
        self.headers_config = self.settings.get('headers', {})
    
    def generate_response(self, messages: List[Dict], stream: bool = True) -> Generator[str, None, None]:
        """Generate response from OpenRouter"""
        if not self.api_key:
            yield "Error: OpenRouter API key not set. Please configure it in settings."
            return
            
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.get_parameter('temperature', 0.7),
                "max_tokens": self.get_parameter('max_tokens', 2000),
                "top_p": self.get_parameter('top_p', 0.9),
                "frequency_penalty": self.get_parameter('frequency_penalty', 0.0),
                "presence_penalty": self.get_parameter('presence_penalty', 0.0),
                "stream": stream
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            # Add configured headers
            headers.update(self.headers_config)
            
            if stream:
                response = requests.post(url, json=payload, headers=headers, stream=True)
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']
                    
        except requests.RequestException as e:
            yield f"Error connecting to OpenRouter: {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI API provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.settings.get('base_url', '')
        self.api_key = self.settings.get('api_key', '')
        self.api_version = self.settings.get('api_version', '2024-02-01')
        self.deployment_name = self.settings.get('deployment_name', '')
        self.timeout = self.settings.get('timeout', 60)
        self.max_retries = self.settings.get('max_retries', 3)
    
    def generate_response(self, messages: List[Dict], stream: bool = True) -> Generator[str, None, None]:
        """Generate response from Azure OpenAI"""
        if not self.api_key:
            yield "Error: Azure OpenAI API key not set. Please configure it in settings."
            return
        
        if not self.deployment_name:
            yield "Error: Azure deployment name not set. Please configure it in settings."
            return
            
        try:
            url = f"{self.base_url}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            payload = {
                "messages": messages,
                "temperature": self.get_parameter('temperature', 0.7),
                "max_tokens": self.get_parameter('max_tokens', 2000),
                "top_p": self.get_parameter('top_p', 0.9),
                "frequency_penalty": self.get_parameter('frequency_penalty', 0.0),
                "presence_penalty": self.get_parameter('presence_penalty', 0.0),
                "stream": stream
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            if stream:
                response = requests.post(url, json=payload, headers=headers, stream=True, timeout=self.timeout)
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']
                    
        except requests.RequestException as e:
            yield f"Error connecting to Azure OpenAI: {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"

def get_llm_provider(provider_name: str, config_manager: ConfigManager = None) -> LLMProvider:
    """Factory function to get the appropriate LLM provider"""
    if config_manager is None:
        config_manager = ConfigManager()
    
    provider_config = config_manager.get_llm_provider_config(provider_name)
    
    if not provider_config:
        raise ValueError(f"Provider '{provider_name}' not found in configuration")
    
    if not provider_config.get("enabled", False):
        raise ValueError(f"Provider '{provider_name}' is not enabled")
    
    if provider_name == 'lm_studio':
        return LMStudioProvider(provider_config)
    elif provider_name == 'openrouter':
        return OpenRouterProvider(provider_config)
    elif provider_name == 'azure_openai':
        return AzureOpenAIProvider(provider_config)
    else:
        raise ValueError(f"Unknown provider type: {provider_name}")

def generate_context_aware_response(
    messages: List[Dict], 
    documents: Dict, 
    provider_name: str = None,
    config_manager: ConfigManager = None,
    stream: bool = True
) -> Generator[str, None, None]:
    """Generate response with document context"""
    
    if config_manager is None:
        config_manager = ConfigManager()
    
    if provider_name is None:
        provider_name = config_manager.get_default_provider()
    
    # Add document context to the conversation
    context_messages = []
    
    # Add system message with document context
    if documents:
        doc_context = ""
        for doc_id, doc in documents.items():
            doc_context += f"\n\nDocument: {doc['filename']}\n{doc['content'][:2000]}..."
        
        system_message = {
            "role": "system",
            "content": f"""You are a helpful AI assistant for support ticket processing. You have access to the following documents for context:
            
{doc_context}

Use this information to provide accurate and helpful responses. Always reference the source documents when relevant."""
        }
        context_messages.append(system_message)
    
    # Add the conversation messages
    context_messages.extend(messages)
    
    # Get the LLM provider and generate response
    try:
        provider = get_llm_provider(provider_name, config_manager)
        for chunk in provider.generate_response(context_messages, stream=stream):
            yield chunk
    except Exception as e:
        yield f"Error generating response: {str(e)}"

def fetch_available_models(provider_name: str, config_manager: ConfigManager = None) -> Dict[str, Any]:
    """Fetch available models from a provider"""
    if config_manager is None:
        config_manager = ConfigManager()
    
    provider_config = config_manager.get_llm_provider_config(provider_name)
    if not provider_config or not provider_config.get("enabled", False):
        return {"success": False, "error": "Anbieter nicht gefunden oder nicht aktiviert", "models": []}
    
    settings = provider_config.get("settings", {})
    
    try:
        if provider_name == "lm_studio":
            return fetch_lm_studio_models(settings)
        elif provider_name == "openrouter":
            return fetch_openrouter_models(settings)
        elif provider_name == "azure_openai":
            return fetch_azure_openai_models(settings)
        else:
            return {"success": False, "error": f"Model fetching not implemented for {provider_name}", "models": []}
    
    except Exception as e:
        return {"success": False, "error": str(e), "models": []}

def fetch_lm_studio_models(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch available models from LM Studio"""
    base_url = settings.get('base_url', 'http://localhost:1234')
    timeout = settings.get('timeout', 30)
    
    try:
        # LM Studio API endpoint for models
        url = f"{base_url}/v1/models"
        headers = {"Content-Type": "application/json"}
        
        # Add API key if provided
        if settings.get('api_key'):
            headers["Authorization"] = f"Bearer {settings['api_key']}"
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        if "data" in data:
            for model in data["data"]:
                model_info = {
                    "id": model.get("id", ""),
                    "name": model.get("id", ""),  # LM Studio uses id as name
                    "owned_by": model.get("owned_by", "local"),
                    "created": model.get("created", 0)
                }
                models.append(model_info)
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
        
    except requests.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}", "models": []}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}", "models": []}

def fetch_openrouter_models(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch available models from OpenRouter"""
    base_url = settings.get('base_url', 'https://openrouter.ai/api/v1')
    api_key = settings.get('api_key', '')
    timeout = settings.get('timeout', 60)
    
    if not api_key:
        return {"success": False, "error": "API-Schlüssel für OpenRouter erforderlich", "models": []}
    
    try:
        # OpenRouter API endpoint for models
        url = f"{base_url}/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add configured headers
        headers.update(settings.get('headers', {}))
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        if "data" in data:
            for model in data["data"]:
                model_info = {
                    "id": model.get("id", ""),
                    "name": model.get("name", model.get("id", "")),
                    "owned_by": model.get("owned_by", "openrouter"),
                    "created": model.get("created", 0),
                    "context_length": model.get("context_length", 0),
                    "pricing": model.get("pricing", {}),
                    "description": model.get("description", "")
                }
                models.append(model_info)
        
        # Sort by name for better UX
        models.sort(key=lambda x: x["name"])
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
        
    except requests.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}", "models": []}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}", "models": []}


def fetch_azure_openai_models(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch available models from Azure OpenAI"""
    base_url = settings.get('base_url', '')
    api_key = settings.get('api_key', '')
    api_version = settings.get('api_version', '2024-02-01')
    timeout = settings.get('timeout', 60)
    
    if not api_key or not base_url:
        return {"success": False, "error": "API-Schlüssel und Basis-URL für Azure OpenAI erforderlich", "models": []}
    
    try:
        # Azure OpenAI API endpoint for deployments
        url = f"{base_url}/openai/deployments?api-version={api_version}"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        if "data" in data:
            for deployment in data["data"]:
                model_info = {
                    "id": deployment.get("id", ""),
                    "name": deployment.get("id", ""),
                    "owned_by": "azure",
                    "model": deployment.get("model", ""),
                    "status": deployment.get("status", ""),
                    "created_at": deployment.get("created_at", 0),
                    "updated_at": deployment.get("updated_at", 0)
                }
                models.append(model_info)
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
        
    except requests.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}", "models": []}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}", "models": []}

def simulate_typing_effect(text: str, delay: float = 0.02) -> Generator[str, None, None]:
    """Simulate typing effect for responses"""
    words = text.split()
    current_text = ""
    
    for word in words:
        current_text += word + " "
        yield current_text
        time.sleep(delay)