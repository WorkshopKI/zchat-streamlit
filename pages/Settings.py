#!/usr/bin/env python3
"""
ChatBot v1.0 - Einstellungsseite
==============================

Umfassende Konfigurationsoberfläche für die ChatBot-Anwendung.

Funktionen:
- Projektmanagement (Erstellen, Löschen, Wechseln)
- KI-Provider-Konfiguration und Tests
- Allgemeine Anwendungseinstellungen
- Konfigurationsimport/-export

Autor: ChatBot v1.0 Team
Version: 1.0
"""

import streamlit as st
import streamlit_antd_components as sac
import json
import requests
import time
from datetime import datetime
from config_manager import ConfigManager
from llm_integration import get_llm_provider, generate_context_aware_response, fetch_available_models
from storage_service import get_storage_service
import uuid

# Page config
st.set_page_config(
    page_title="Einstellungen",
    page_icon="⚙️",
    layout="wide"
)

# Hide Streamlit's automatic navigation
st.markdown("""
<style>
/* Hide the navigation bar */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Hide navigation for different Streamlit versions */
section[data-testid="stSidebarNav"] {
    display: none !important;
}

.css-1d391kg .css-1v0mbdj {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Custom CSS for compact layout and neutral button styling
st.markdown("""
<style>
/* Override Streamlit's default button colors to neutral gray */
.stButton > button {
    background-color: #f5f5f5 !important;
    color: #262730 !important;
    border: 1px solid #d9d9d9 !important;
    border-radius: 6px !important;
    padding: 4px 8px;
    min-height: 32px;
}

.stButton > button:hover {
    background-color: #e6f4ff !important;
    border-color: #91caff !important;
    color: #262730 !important;
}

.stButton > button:active, .stButton > button:focus {
    background-color: #bae0ff !important;
    border-color: #69b1ff !important;
    color: #262730 !important;
    box-shadow: none !important;
}

/* Reduce padding and margins */
.stContainer {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.stColumns {
    gap: 0.5rem;
}

.stExpander {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    padding: 6px 12px;
}

/* Compact form elements */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    padding: 4px 8px;
    min-height: 32px;
}

.stCheckbox {
    margin-bottom: 4px;
}

/* Reduce space between elements */
.element-container {
    margin-bottom: 0.5rem;
}

/* Compact dividers */
hr {
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = ConfigManager()

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def test_llm_provider(provider_name: str, config_manager: ConfigManager):
    """
    Testet die Verbindung zu einem LLM-Provider.
    
    Args:
        provider_name (str): Name des Providers
        config_manager (ConfigManager): Konfigurationsmanager
        
    Returns:
        Dict[str, Any]: Test-Ergebnis mit Status, Antwort und Antwortzeit
    """
    try:
        # Get provider instance
        provider = get_llm_provider(provider_name, config_manager)
        
        # Test-Nachricht
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond briefly to test the connection."},
            {"role": "user", "content": "Hallo! Bitte antworten Sie mit 'Test erfolgreich', um zu bestätigen, dass die Verbindung funktioniert."}
        ]
        
        # Generate test response
        response_text = ""
        start_time = time.time()
        
        for chunk in provider.generate_response(test_messages, stream=False):
            response_text += chunk
            break  # Just get the first response for testing
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        if response_text and len(response_text.strip()) > 0:
            return {
                "success": True,
                "response": response_text.strip()[:200] + "..." if len(response_text) > 200 else response_text.strip(),
                "response_time": response_time,
                "error": None
            }
        else:
            return {
                "success": False,
                "response": None,
                "response_time": response_time,
                "error": "Leere Antwort erhalten"
            }
            
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "response_time": None,
            "error": str(e)
        }

def render_provider_settings(provider_name: str, provider_config: dict, config_manager: ConfigManager):
    """
    Rendert die Einstellungen für einen spezifischen LLM-Provider.
    
    Args:
        provider_name (str): Name des Providers
        provider_config (dict): Provider-Konfiguration
        config_manager (ConfigManager): Konfigurationsmanager
        
    Note:
        Zeigt alle Provider-spezifischen Einstellungen, Test-Buttons und Parameter.
    """
    
    # Compact header with inline controls
    col_header, col_enable, col_test, col_reload = st.columns([2, 1, 1, 1])
    
    with col_header:
        st.markdown(f"**🤖 {provider_config.get('name', provider_name.title())}**")
    
    with col_enable:
        enabled = sac.switch(
            label="",
            value=provider_config.get('enabled', False),
            key=f"switch_enabled_{provider_name}",
            size='small'
        )
        st.caption("Aktivieren" if not enabled else "Aktiviert")
        
        if enabled != provider_config.get('enabled', False):
            config_manager.set(f"llm_providers.providers.{provider_name}.enabled", enabled)
            # Save to database
            storage = get_storage_service()
            storage.save_settings(config_manager.config)
    
    with col_test:
        if st.button(f"🧪", key=f"test_{provider_name}", disabled=not enabled, help="Verbindung testen"):
            if enabled:
                with st.spinner("Teste..."):
                    test_result = test_llm_provider(provider_name, config_manager)
                    st.session_state[f"test_result_{provider_name}"] = test_result
    
    with col_reload:
        if st.button(f"🔄", key=f"reload_{provider_name}", disabled=not enabled, help="Modelle neu laden"):
            if enabled:
                with st.spinner("Lade..."):
                    models_result = fetch_available_models(provider_name, config_manager)
                    st.session_state[f"models_result_{provider_name}"] = models_result
                    
                    if models_result["success"]:
                        # Update available models in config for certain providers
                        if provider_name == "openrouter":
                            model_ids = [model["id"] for model in models_result["models"]]
                            config_manager.set(f"llm_providers.providers.{provider_name}.settings.available_models", model_ids)
                        elif provider_name == "azure_openai":
                            model_ids = [model["id"] for model in models_result["models"]]
                            config_manager.set(f"llm_providers.providers.{provider_name}.settings.available_deployments", model_ids)
        
    # Compact status messages
    if f"test_result_{provider_name}" in st.session_state:
        result = st.session_state[f"test_result_{provider_name}"]
        if result["success"]:
            st.success(f"✅ Test erfolgreich ({result['response_time']}ms)")
        else:
            st.error(f"❌ Test fehlgeschlagen: {result['error']}")
    
    if f"models_result_{provider_name}" in st.session_state:
        models_result = st.session_state[f"models_result_{provider_name}"]
        if models_result["success"]:
            st.success(f"✅ {models_result['count']} Modelle geladen")
        else:
            st.error(f"❌ Modell-Abruf fehlgeschlagen: {models_result['error']}")
    
    if enabled:
        # Compact provider settings in columns
        settings = provider_config.get('settings', {})
        
        # API-Konfiguration in einer Zeile
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            current_endpoint = settings.get('base_url', '')
            new_endpoint = st.text_input(
                "API-Endpunkt",
                value=current_endpoint,
                key=f"endpoint_{provider_name}",
                label_visibility="collapsed",
                placeholder="API-Endpunkt URL"
            )
            st.caption("API-Endpunkt")
            if new_endpoint != current_endpoint:
                config_manager.set(f"llm_providers.providers.{provider_name}.settings.base_url", new_endpoint)
                # Auto-save to database
                storage = get_storage_service()
                storage.save_settings(config_manager.config)
        
        with col2:
            current_api_key = settings.get('api_key', '')
            new_api_key = st.text_input(
                "API-Schlüssel",
                value=current_api_key,
                type="password",
                key=f"api_key_{provider_name}",
                label_visibility="collapsed",
                placeholder="API-Schlüssel (optional)"
            )
            st.caption("API-Schlüssel (Optional)")
            if new_api_key != current_api_key:
                config_manager.set(f"llm_providers.providers.{provider_name}.settings.api_key", new_api_key)
                # Auto-save to database
                storage = get_storage_service()
                storage.save_settings(config_manager.config)
        
        with col3:
            current_timeout = settings.get('timeout', 60)
            new_timeout = st.number_input(
                "Zeitlimit",
                min_value=10,
                max_value=300,
                value=current_timeout,
                key=f"timeout_{provider_name}",
                label_visibility="collapsed"
            )
            st.caption("Zeitlimit (s)")
            if new_timeout != current_timeout:
                config_manager.set(f"llm_providers.providers.{provider_name}.settings.timeout", new_timeout)
                # Auto-save to database
                storage = get_storage_service()
                storage.save_settings(config_manager.config)
        
        # Model selection in single row
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Model selection - always use dropdown when models are available
            current_model = settings.get('model_name', '')
            
            # Check if we have fetched models for this provider
            fetched_models = []
            if f"models_result_{provider_name}" in st.session_state:
                models_result = st.session_state[f"models_result_{provider_name}"]
                if models_result["success"]:
                    fetched_models = [model["id"] for model in models_result["models"]]
            
            # Use fetched models first, then fall back to predefined models
            available_models = []
            
            if fetched_models:
                available_models = fetched_models
            elif provider_name == 'lm_studio':
                # LM Studio can have pre-configured models too
                available_models = settings.get('available_models', [])
            elif provider_name == 'openrouter':
                available_models = settings.get('available_models', [])
            elif provider_name == 'azure_openai':
                available_models = settings.get('available_deployments', [])
            
            # Always try to use selectbox when we have models
            if available_models:
                if current_model and current_model not in available_models:
                    available_models.insert(0, current_model)  # Keep current selection
                
                model_index = available_models.index(current_model) if current_model in available_models else 0
                
                label = "Deployment" if provider_name == 'azure_openai' else "Model"
                new_model = st.selectbox(
                    label,
                    available_models,
                    index=model_index,
                    key=f"model_{provider_name}",
                    label_visibility="collapsed",
                    help=f"Select {label.lower()} (use 🔄 to refresh)"
                )
            else:
                # Fallback to text input when no models available
                label = "Deployment Name" if provider_name == 'azure_openai' else "Model Name"
                new_model = st.text_input(
                    label,
                    value=current_model,
                    key=f"model_{provider_name}",
                    label_visibility="collapsed",
                    placeholder=label,
                    help=f"Verwenden Sie 🔄 Modelle neu laden, um verfügbare {label.lower()}s abzurufen"
                )
            
            st.caption("Model" if provider_name != 'azure_openai' else "Deployment")
            
            if new_model != current_model:
                config_manager.set(f"llm_providers.providers.{provider_name}.settings.model_name", new_model)
                # Auto-save to database
                storage = get_storage_service()
                storage.save_settings(config_manager.config)
        
        # Compact Advanced Parameters in a single row
        with st.expander("⚙️ Parameters", expanded=False):
            parameters = settings.get('parameters', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_temp = parameters.get('temperature', 0.7)
                new_temp = st.number_input(
                    "Temperatur",
                    min_value=0.0,
                    max_value=2.0,
                    value=current_temp,
                    step=0.1,
                    format="%.1f",
                    key=f"temp_{provider_name}",
                    label_visibility="collapsed"
                )
                st.caption("Temperatur")
                if new_temp != current_temp:
                    config_manager.set(f"llm_providers.providers.{provider_name}.settings.parameters.temperature", new_temp)
            
            with col2:
                current_tokens = parameters.get('max_tokens', 2000)
                new_tokens = st.number_input(
                    "Max Token",
                    min_value=100,
                    max_value=4000,
                    value=current_tokens,
                    step=100,
                    key=f"tokens_{provider_name}",
                    label_visibility="collapsed"
                )
                st.caption("Max Token")
                if new_tokens != current_tokens:
                    config_manager.set(f"llm_providers.providers.{provider_name}.settings.parameters.max_tokens", new_tokens)
            
            with col3:
                current_top_p = parameters.get('top_p', 0.9)
                new_top_p = st.number_input(
                    "Top P",
                    min_value=0.0,
                    max_value=1.0,
                    value=current_top_p,
                    step=0.05,
                    format="%.2f",
                    key=f"top_p_{provider_name}",
                    label_visibility="collapsed"
                )
                st.caption("Top P")
                if new_top_p != current_top_p:
                    config_manager.set(f"llm_providers.providers.{provider_name}.settings.parameters.top_p", new_top_p)
        
        # Compact provider-specific settings
        if provider_name == 'openrouter':
            with st.expander("🌐 OpenRouter", expanded=False):
                headers = settings.get('headers', {})
                col1, col2 = st.columns(2)
                with col1:
                    current_referer = headers.get('HTTP-Referer', 'https://github.com/chatbot-v1')
                    new_referer = st.text_input(
                        "HTTP Referer",
                        value=current_referer,
                        key=f"referer_{provider_name}",
                        label_visibility="collapsed",
                        placeholder="HTTP Referer"
                    )
                    st.caption("HTTP Referer")
                    if new_referer != current_referer:
                        config_manager.set(f"llm_providers.providers.{provider_name}.settings.headers.HTTP-Referer", new_referer)
                
                with col2:
                    current_title = headers.get('X-Title', 'ChatBot v1.0')
                    new_title = st.text_input(
                        "X-Title",
                        value=current_title,
                        key=f"title_{provider_name}",
                        label_visibility="collapsed",
                        placeholder="App Title"
                    )
                    st.caption("X-Title")
                    if new_title != current_title:
                        config_manager.set(f"llm_providers.providers.{provider_name}.settings.headers.X-Title", new_title)
        
        elif provider_name == 'azure_openai':
            with st.expander("☁️ Azure", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    current_version = settings.get('api_version', '2024-02-01')
                    new_version = st.text_input(
                        "API Version",
                        value=current_version,
                        key=f"version_{provider_name}",
                        label_visibility="collapsed",
                        placeholder="API Version"
                    )
                    st.caption("API Version")
                    if new_version != current_version:
                        config_manager.set(f"llm_providers.providers.{provider_name}.settings.api_version", new_version)
                
                with col2:
                    current_deployment = settings.get('deployment_name', '')
                    new_deployment = st.text_input(
                        "Deployment Name",
                        value=current_deployment,
                        key=f"deployment_{provider_name}",
                        label_visibility="collapsed",
                        placeholder="Deployment Name"
                    )
                    st.caption("Deployment Name")
                    if new_deployment != current_deployment:
                        config_manager.set(f"llm_providers.providers.{provider_name}.settings.deployment_name", new_deployment)

# ============================================================================  
# HAUPTFUNKTION
# ============================================================================

def main():
    """
    Hauptfunktion der Einstellungsseite.
    
    Verwaltet:
    - Seitenleiste mit Navigation und Schnellaktionen
    - Tabs für Projekte, AI-Provider, Einstellungen und Konfiguration
    - Auto-Laden von Modellen für aktivierte Provider
    """
    st.title("⚙️ Einstellungen")
    st.markdown("Konfigurieren Sie Ihre KI-Anbieter und Anwendungseinstellungen")
    
    config_manager = st.session_state.config_manager
    
    # Sidebar with navigation
    with st.sidebar:
        st.title("⚙️ Einstellungen")
        st.markdown("---")
        
        # Back to main page button
        if st.button("🏠 Zurück zur Hauptseite", use_container_width=True):
            # Set flag to prevent immediate redirect back to Settings
            st.session_state.just_returned_from_settings = True
            st.switch_page("app.py")
        
        st.markdown("---")
        st.markdown("**Schnellaktionen:**")
        
        # Quick save button
        if st.button("💾 Speichere alle Einstellungen", use_container_width=True):
            try:
                config_manager.save_config()
                storage = get_storage_service()
                storage.save_settings(config_manager.config)
                st.success("✅ Einstellungen gespeichert!")
            except Exception as e:
                st.error(f"❌ Speichern fehlgeschlagen: {e}")

    # Auto-fetch models for enabled providers on page load
    if 'models_auto_fetched' not in st.session_state:
        st.session_state.models_auto_fetched = True
        
        # Auto-fetch for LM Studio if enabled
        lm_studio_config = config_manager.get_llm_provider_config('lm_studio')
        if lm_studio_config and lm_studio_config.get('enabled', False):
            with st.spinner("Lade LM Studio Modelle..."):
                models_result = fetch_available_models('lm_studio', config_manager)
                if models_result["success"]:
                    st.session_state[f"models_result_lm_studio"] = models_result
    
    # Main settings tabs with Antd
    active_tab = sac.tabs([
        sac.TabsItem(label='Projekte', icon='folder'),
        sac.TabsItem(label='AI-Provider', icon='robot'),
        sac.TabsItem(label='Allgemeine Einstellungen', icon='setting'),
        sac.TabsItem(label='Konfiguration', icon='code'),
    ], align='left', return_index=True, key='settings_tabs')
    
    if active_tab == 0:
        st.header("Projekt Management")
        
        # Create new project section
        st.subheader("➕ Neues Projekt erstellen")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            new_project_name = st.text_input("Projekt Name", placeholder="Projekt Name eingeben...")
            new_project_desc = st.text_area("Beschreibung (optional)", placeholder="Optional Projektbeschreibung...")
        
        with col2:
            st.markdown("**Schnellaktionen:**")
            create_button = sac.buttons([
                sac.ButtonsItem(label='Projekt erstellen', icon='plus-circle'),
            ], variant='outline', key='create_project', return_index=True)
            
            # Store create button state to detect actual clicks
            if 'last_create_button' not in st.session_state:
                st.session_state.last_create_button = None
                
            # FIXED LOGIC: Only create project on actual button clicks
            if (create_button is not None and 
                create_button == 0 and 
                st.session_state.last_create_button is not None):
                if new_project_name:
                    storage = get_storage_service()
                    project_id = storage.create_project(new_project_name, new_project_desc)
                    storage.save_user_preference('current_project', project_id)
                    st.success(f"✅ Projekt '{new_project_name}' erstellt!")
                    st.info("Sie können nun zur Hauptseite navigieren, um Ihr Projekt zu verwenden.")
                else:
                    st.error("Bitte geben Sie einen Projektnamen ein")
                st.session_state.last_create_button = create_button
            else:
                st.session_state.last_create_button = create_button
        
        sac.divider(key='project_section_divider')
        
        # Existing projects management
        st.subheader("📋 Bestehende Projekte")
        storage = get_storage_service()
        projects = storage.get_all_projects()
        
        if projects:
            for project in projects:
                with st.expander(f"📁 {project['name']} ({project['message_count']} messages, {project['document_count']} documents)"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Beschreibung:** {project['description'] or 'Keine Beschreibung'}")
                        st.write(f"**Erstellt:** {project['created_at'][:19]}")
                        st.write(f"**Zuletzt aktualisiert:** {project['updated_at'][:19]}")
                    
                    with col2:
                        if st.button(f"🏠 Wechseln zu", key=f"switch_{project['id']}"):
                            storage.save_user_preference('current_project', project['id'])
                            st.success(f"Wechselt zu Projekt: {project['name']}")
                            st.info("Navigieren Sie zur Hauptseite, um Ihr Projekt zu sehen.")
                    
                    with col3:
                        if st.button(f"🗑️ Löschen", key=f"delete_{project['id']}"):
                            if st.session_state.get(f"confirm_delete_{project['id']}", False):
                                storage.delete_project(project['id'])
                                st.success(f"Projekt '{project['name']}' gelöscht!")
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_{project['id']}"] = True
                                st.warning("Klicken Sie erneut, um die Löschung zu bestätigen")
        else:
            st.info("Keine Projekte gefunden. Erstellen Sie Ihr erstes Projekt oben!")
    
    elif active_tab == 1:
        st.header("AI-Provider Konfiguration")
        
        # Default provider selection
        enabled_providers = config_manager.get_enabled_providers()
        provider_names = list(enabled_providers.keys())
        
        # Show enabled providers as chips
        if provider_names:
            st.subheader("✅ Aktive Provider")
            chip_items = []
            for provider in provider_names:
                chip_items.append(sac.ChipItem(label=enabled_providers[provider].get('name', provider.title())))
            sac.chip(items=chip_items, color='gray', size='small', key='active_providers_chip')
            sac.divider(key='providers_chip_divider')
        
        if provider_names:
            current_default = config_manager.get_default_provider()
            if current_default not in provider_names:
                current_default = provider_names[0] if provider_names else None
            
            if current_default:
                new_default = st.selectbox(
                    "🎯 Standard-Provider",
                    provider_names,
                    index=provider_names.index(current_default),
                    format_func=lambda x: enabled_providers[x].get('name', x.title()),
                    help="Der KI-Anbieter, der standardmäßig für neue Gespräche verwendet wird"
                )
                
                if new_default != current_default:
                    config_manager.set('llm_providers.default_provider', new_default)
                    # Auto-save to database
                    storage = get_storage_service()
                    storage.save_settings(config_manager.config)
                    st.success(f"Standard-Anbieter gesetzt auf {enabled_providers[new_default].get('name', new_default)}")
        
        sac.divider(key='default_provider_divider')
        
        # Provider-Konfigurationen
        all_providers = config_manager.get("llm_providers.providers", {})
        
        for provider_name, provider_config in all_providers.items():
            with st.container():
                render_provider_settings(provider_name, provider_config, config_manager)
                sac.divider(key=f'provider_{provider_name}_divider')
    
    elif active_tab == 2:
        st.header("Allgemeine Einstellungen")
        
        # Compact settings in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📁 Datei Upload**")
            current_max_size = config_manager.get("file_upload.max_file_size_mb", 200)
            new_max_size = st.number_input(
                "Max Size (MB)",
                min_value=1,
                max_value=1000,
                value=current_max_size,
                label_visibility="collapsed"
            )
            st.caption("Max Datei Größe (MB)")
            if new_max_size != current_max_size:
                config_manager.set("file_upload.max_file_size_mb", new_max_size)
            
            current_max_files = config_manager.get("file_upload.max_files_per_project", 50)
            new_max_files = st.number_input(
                "Max Dateien",
                min_value=1,
                max_value=200,
                value=current_max_files,
                label_visibility="collapsed"
            )
            st.caption("Max Dateien pro Projekt")
            if new_max_files != current_max_files:
                config_manager.set("file_upload.max_files_per_project", new_max_files)
        
        with col2:
            st.markdown("**💬 Chat**")
            current_max_history = config_manager.get("ui.max_chat_history_display", 50)
            new_max_history = st.number_input(
                "Verlauf anzeigen",
                min_value=10,
                max_value=200,
                value=current_max_history,
                label_visibility="collapsed"
            )
            st.caption("Max Chat Verlauf anzeigen")
            if new_max_history != current_max_history:
                config_manager.set("ui.max_chat_history_display", new_max_history)
            
            current_streaming = config_manager.get("features.chat.enable_streaming", True)
            new_streaming = sac.switch(
                label="",
                value=current_streaming,
                key='switch_streaming',
                size='small'
            )
            st.caption("Streaming Antworten aktivieren")
            if new_streaming != current_streaming:
                config_manager.set("features.chat.enable_streaming", new_streaming)
        
        with col3:
            st.markdown("**⚡ Leistung**")
            current_cache = config_manager.get("performance.cache_enabled", True)
            new_cache = sac.switch(
                label="",
                value=current_cache,
                key='switch_cache',
                size='small'
            )
            st.caption("Caching aktivieren")
            if new_cache != current_cache:
                config_manager.set("performance.cache_enabled", new_cache)
            
            current_concurrent = config_manager.get("performance.max_concurrent_requests", 5)
            new_concurrent = st.number_input(
                "Concurrent",
                min_value=1,
                max_value=20,
                value=current_concurrent,
                label_visibility="collapsed"
            )
            st.caption("Max Concurrent Requests")
            if new_concurrent != current_concurrent:
                config_manager.set("performance.max_concurrent_requests", new_concurrent)
    
    elif active_tab == 3:
        st.header("Konfiguration")
        
        # Configuration action buttons with Antd
        action_buttons = sac.buttons([
            sac.ButtonsItem(label='Speichern', icon='save'),
            sac.ButtonsItem(label='Zurücksetzen', icon='reload'),
            sac.ButtonsItem(label='Validieren', icon='check-circle'),
            sac.ButtonsItem(label='Export', icon='download'),
        ], variant='outline', key='config_actions', return_index=True)
        
        if action_buttons == 0:  # Save
            try:
                config_manager.save_config()
                user_config = config_manager.create_user_settings_from_session()
                config_manager.save_user_config(user_config)
                st.success("✅ Speichern erfolgreich!")
            except Exception as e:
                st.error(f"❌ Speichern fehlgeschlagen: {e}")
        
        elif action_buttons == 1:  # Reset
            if st.session_state.get('confirm_reset', False):
                try:
                    config_manager.config = config_manager.get_default_config()
                    config_manager.save_config()
                    st.success("✅ Zurückgesetzt!")
                    st.session_state['confirm_reset'] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Zurücksetzen fehlgeschlagen: {e}")
            else:
                st.session_state['confirm_reset'] = True
                st.warning("⚠️ Klicken Sie erneut zur Bestätigung")
        
        elif action_buttons == 2:  # Validate
            if config_manager.validate_config():
                st.success("✅ Gültig!")
            else:
                st.error("❌ Ungültig!")
        
        elif action_buttons == 3:  # Export
            config_json = json.dumps(config_manager.config, indent=2)
            st.download_button(
                label="📥 Export herunterladen",
                data=config_json,
                file_name=f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Compact import
        uploaded_config = st.file_uploader(
            "📤 Konfiguration importieren",
            type=['json'],
            label_visibility="collapsed",
            help="Konfigurationsdatei hochladen"
        )
        
        if uploaded_config is not None:
            try:
                config_data = json.load(uploaded_config)
                config_manager.config = config_data
                st.success("✅ Konfiguration importiert!")
                if st.button("Änderungen anwenden"):
                    config_manager.save_config()
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Import fehlgeschlagen: {e}")
        
        # Compact configuration preview
        with st.expander("🔍 Konfiguration anzeigen", expanded=False):
            st.json(config_manager.config)

if __name__ == "__main__":
    main()