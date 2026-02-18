#!/usr/bin/env python3
import gi
import json
import os
import re
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

MODELS_JSON_PATH = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/models.json")

class SettingsWindow(Gtk.Dialog):
    def __init__(self):
        super().__init__(title="Claw Control Settings")
        self.set_default_size(650, 500)
        
        # Track all checkboxes and their model IDs
        self.model_checkboxes = {}
        
        # Add buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save", Gtk.ResponseType.OK)
        
        # Get content area
        content = self.get_content_area()
        content.set_spacing(10)
        content.set_border_width(10)
        
        # Create notebook (tabs)
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        
        # Tab 1: Menu
        tab_menu = self._create_menu_tab()
        notebook.append_page(tab_menu, Gtk.Label(label="Menu"))
        
        # Tab 2: Model List
        tab1 = self._create_model_list_tab()
        notebook.append_page(tab1, Gtk.Label(label="Model List"))
        
        # Tab 3: Model List (manual)
        tab2 = self._create_manual_tab()
        notebook.append_page(tab2, Gtk.Label(label="Model List (manual)"))
        
        # Tab 4: Local Models
        tab3 = self._create_local_tab()
        notebook.append_page(tab3, Gtk.Label(label="Local Models"))
        
        content.pack_start(notebook, True, True, 0)
        
        # Load current models from JSON
        self._load_models_from_json()
        
        self.show_all()
    
    def _normalize_model_id(self, model_id):
        """Normalize model ID to match checkbox keys"""
        # Remove openrouter/ prefix if present
        if model_id.startswith('openrouter/'):
            model_id = model_id[11:]  # len('openrouter/') = 11
        # Normalize moonshotai -> moonshot
        if model_id.startswith('moonshotai/'):
            model_id = 'moonshot/' + model_id[11:]
        return model_id

    def _load_models_from_json(self):
        """Load existing models from JSON and check appropriate boxes"""
        try:
            if os.path.exists(MODELS_JSON_PATH):
                with open(MODELS_JSON_PATH, 'r') as f:
                    models = json.load(f)
                    # Extract full model_id from cmd field (e.g., "set openrouter/gemini...")
                    active_ids = set()
                    for m in models:
                        if 'cmd' in m:
                            # Extract provider/model from cmd
                            match = re.search(r'--model\s+(\S+)', m['cmd'])
                            if match:
                                raw_id = match.group(1)
                                # Normalize to match checkbox keys
                                normalized_id = self._normalize_model_id(raw_id)
                                active_ids.add(normalized_id)
                                # Also add raw ID for openrouter models
                                if raw_id.startswith('openrouter/'):
                                    active_ids.add(raw_id)
                        # Also check legacy format with id containing /
                        if '/' in m.get('id', ''):
                            active_ids.add(m['id'])
                            active_ids.add(self._normalize_model_id(m['id']))

                    # Check boxes that are in the JSON
                    for model_id, checkbox in self.model_checkboxes.items():
                        checkbox.set_active(model_id in active_ids)
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def _save_models_to_json(self):
        """Save checked models to JSON file"""
        models = []
        
        for model_id, checkbox in self.model_checkboxes.items():
            if checkbox.get_active():
                # Get display name from label text
                display_name = checkbox.get_label()
                
                # Generate short_id from model_id (replace / with _)
                short_id = model_id.replace('/', '_').replace('-', '_')
                
                # Construct the cmd
                cmd = f"/usr/bin/openclaw sessions patch agent:main:main --model {model_id} && /usr/bin/openclaw sessions clear"
                
                models.append({
                    "id": short_id,
                    "name": display_name,
                    "cmd": cmd
                })
        
        try:
            with open(MODELS_JSON_PATH, 'w') as f:
                json.dump(models, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def _save_menu_settings(self):
        """Save menu visibility settings to JSON"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            
            # Load existing or create new
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
            else:
                menu_config = {}
            
            # Update enabled states
            default_labels = {
                "oc_models": "OC Models",
                "oc_start": "OC Start",
                "oc_stop": "OC Stop",
                "oc_restart": "OC Restart",
                "oc_dashboard": "OC Dashboard",
                "oc_json": "OC Json",
                "oc_folder": "OC Folder",
                "oc_doctor": "OC Doctor"
            }
            
            for item_id, checkbox in self.menu_checkboxes.items():
                if item_id not in menu_config:
                    menu_config[item_id] = {}
                menu_config[item_id]['enabled'] = checkbox.get_active()
                if 'label' not in menu_config[item_id] and item_id in default_labels:
                    menu_config[item_id]['label' if item_id != 'credits' else 'text'] = default_labels[item_id]
            
            with open(menu_json_path, 'w') as f:
                json.dump(menu_config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving menu settings: {e}")
            return False
    
    def _add_model_checkbox(self, container, model_id, display_name):
        """Add a checkbox for a model and track it"""
        check = Gtk.CheckButton.new_with_label(display_name)
        check.set_halign(Gtk.Align.START)
        container.pack_start(check, False, False, 1)
        self.model_checkboxes[model_id] = check
        return check
    
    def _create_model_list_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        main_box.set_border_width(10)
        
        # Left column
        left_frame = Gtk.Frame(label="Providers")
        left_frame.set_shadow_type(Gtk.ShadowType.NONE)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        left_box.set_border_width(10)
        left_frame.add(left_box)
        
        # Right column
        right_frame = Gtk.Frame(label="OpenRouter Mirrors")
        right_frame.set_shadow_type(Gtk.ShadowType.NONE)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        right_box.set_border_width(10)
        right_frame.add(right_box)
        
        # Left column providers
        providers = [
            ("Anthropic", [
                ("anthropic/claude-opus-4.6", "Claude Opus 4.6"),
                ("anthropic/claude-sonnet-4.5", "Claude Sonnet 4.5")
            ]),
            ("OpenAI", [
                ("openai/gpt-5.3-codex", "GPT-5.3 Codex"),
                ("openai/gpt-5.2", "GPT-5.2")
            ]),
            ("Google", [
                ("google/gemini-3-pro", "Gemini 3 Pro"),
                ("google/gemini-3-flash", "Gemini 3 Flash")
            ]),
            ("Moonshot AI", [
                ("moonshot/kimi-k2.5", "Kimi K2.5")
            ]),
            ("Zhipu AI", [
                ("zai/glm-5", "GLM-5")
            ]),
            ("DeepSeek", [
                ("deepseek/deepseek-v3.2", "DeepSeek V3.2")
            ]),
            ("Alibaba", [
                ("qwen/qwen-3.5-plus", "Qwen 3.5 Plus")
            ]),
            ("xAI", [
                ("xai/grok-4.1-fast", "Grok 4.1 Fast")
            ])
        ]
        
        for provider_name, models in providers:
            label = Gtk.Label()
            label.set_markup(f"<b>{provider_name}</b>")
            label.set_halign(Gtk.Align.START)
            left_box.pack_start(label, False, False, 3)
            
            for model_id, display_name in models:
                self._add_model_checkbox(left_box, model_id, f"{provider_name.lower()}/{display_name.lower().replace(' ', '-')}")
            
            left_box.pack_start(Gtk.Label(), False, False, 8)
        
        # Right column - OpenRouter
        or_label = Gtk.Label()
        or_label.set_markup("<b>OpenRouter</b>")
        or_label.set_halign(Gtk.Align.START)
        right_box.pack_start(or_label, False, False, 3)
        
        openrouter_models = [
            ("openrouter/anthropic/claude-opus-4.6", "Anthropic Claude Opus 4.6"),
            ("openrouter/anthropic/claude-sonnet-4.5", "Anthropic Claude Sonnet 4.5"),
            ("openrouter/openai/gpt-5.3-codex", "OpenAI GPT-5.3 Codex"),
            ("openrouter/openai/gpt-5.2", "OpenAI GPT-5.2"),
            ("openrouter/openai/gpt-5-nano", "OpenAI GPT-5 Nano"),
            ("openrouter/openai/gpt-4o-mini", "OpenAI GPT-4o Mini"),
            ("openrouter/google/gemini-3-pro", "Google Gemini 3 Pro"),
            ("openrouter/google/gemini-3-flash", "Google Gemini 3 Flash"),
            ("openrouter/google/gemini-2.5-flash-lite-preview-09-2025", "Google Gemini 2.5 Flash Lite"),
            ("openrouter/google/gemini-3-flash-preview", "Google Gemini 3 Flash Preview"),
            ("openrouter/moonshotai/kimi-k2.5", "Moonshot Kimi K2.5"),
            ("openrouter/zai/glm-5", "Zhipu GLM-5"),
            ("openrouter/deepseek/deepseek-v3.2", "DeepSeek V3.2"),
            ("openrouter/qwen/qwen-3.5-plus", "Alibaba Qwen 3.5 Plus"),
            ("openrouter/xai/grok-4.1-fast", "xAI Grok 4.1 Fast")
        ]
        
        for model_id, display_name in openrouter_models:
            self._add_model_checkbox(right_box, model_id, model_id)
        
        main_box.pack_start(left_frame, True, True, 0)
        main_box.pack_start(right_frame, True, True, 0)
        
        scrolled.add_with_viewport(main_box)
        return scrolled
    
    def _create_manual_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<b>Manual Model Configuration</b>")
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 5)
        
        # Subtitle
        subtitle = Gtk.Label(label="Add up to 10 custom models")
        subtitle.set_halign(Gtk.Align.START)
        box.pack_start(subtitle, False, False, 3)
        
        # Separator
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)
        
        # Custom model entries
        self.manual_model_entries = {}
        
        for i in range(1, 11):
            # Frame for each model
            frame = Gtk.Frame(label=f"Custom Model #{i}")
            frame.set_shadow_type(Gtk.ShadowType.IN)
            model_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            model_box.set_border_width(10)
            
            # Title input
            title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            title_label = Gtk.Label(label="Title:")
            title_label.set_size_request(100, -1)
            title_entry = Gtk.Entry()
            title_entry.set_placeholder_text("Display name (e.g., GPT-4 Turbo)")
            title_box.pack_start(title_label, False, False, 0)
            title_box.pack_start(title_entry, True, True, 0)
            model_box.pack_start(title_box, False, False, 3)
            
            # Provider/Model input
            model_id_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            model_id_label = Gtk.Label(label="Provider/Model:")
            model_id_label.set_size_request(100, -1)
            model_id_entry = Gtk.Entry()
            model_id_entry.set_placeholder_text("provider/model-id (e.g., openai/gpt-4-turbo)")
            model_id_box.pack_start(model_id_label, False, False, 0)
            model_id_box.pack_start(model_id_entry, True, True, 0)
            model_box.pack_start(model_id_box, False, False, 3)
            
            frame.add(model_box)
            box.pack_start(frame, False, False, 5)
            
            # Store references
            self.manual_model_entries[f"manual_model_{i}"] = {
                "title": title_entry,
                "model_id": model_id_entry
            }
        
        # Load existing manual models
        self._load_manual_models()
        
        scrolled.add_with_viewport(box)
        return scrolled
    
    def _create_local_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<b>Ollama Local Models</b>")
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 5)
        
        # Description
        desc = Gtk.Label(label="Configure Ollama local/remote LLM server")
        desc.set_halign(Gtk.Align.START)
        box.pack_start(desc, False, False, 3)
        
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)
        
        # Enable Ollama checkbox
        self.ollama_enabled_check = Gtk.CheckButton.new_with_label("Enable Ollama models")
        self.ollama_enabled_check.set_halign(Gtk.Align.START)
        box.pack_start(self.ollama_enabled_check, False, False, 5)
        
        # Custom address checkbox
        self.ollama_custom_check = Gtk.CheckButton.new_with_label("Use custom address")
        self.ollama_custom_check.set_halign(Gtk.Align.START)
        box.pack_start(self.ollama_custom_check, False, False, 5)
        
        # Custom address frame
        addr_frame = Gtk.Frame(label="Custom Ollama Address")
        addr_frame.set_shadow_type(Gtk.ShadowType.IN)
        addr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        addr_box.set_border_width(10)
        
        # IP input
        ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ip_label = Gtk.Label(label="IP Address:")
        ip_label.set_size_request(100, -1)
        self.ollama_ip_entry = Gtk.Entry()
        self.ollama_ip_entry.set_placeholder_text("127.0.0.1")
        self.ollama_ip_entry.set_text("127.0.0.1")
        ip_box.pack_start(ip_label, False, False, 0)
        ip_box.pack_start(self.ollama_ip_entry, True, True, 0)
        addr_box.pack_start(ip_box, False, False, 3)
        
        # Port input
        port_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        port_label = Gtk.Label(label="Port:")
        port_label.set_size_request(100, -1)
        self.ollama_port_entry = Gtk.Entry()
        self.ollama_port_entry.set_placeholder_text("11434")
        self.ollama_port_entry.set_text("11434")
        port_box.pack_start(port_label, False, False, 0)
        port_box.pack_start(self.ollama_port_entry, True, True, 0)
        addr_box.pack_start(port_box, False, False, 3)
        
        addr_frame.add(addr_box)
        box.pack_start(addr_frame, False, False, 5)
        
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 10)
        
        # Ollama models section
        models_title = Gtk.Label()
        models_title.set_markup("<b>Ollama Models</b>")
        models_title.set_halign(Gtk.Align.START)
        box.pack_start(models_title, False, False, 5)
        
        desc2 = Gtk.Label(label="Add up to 10 Ollama models (e.g., llama3.3, deepseek-r1:32b)")
        desc2.set_halign(Gtk.Align.START)
        box.pack_start(desc2, False, False, 3)
        
        # Ollama model entries
        self.ollama_model_entries = {}
        
        for i in range(1, 11):
            frame = Gtk.Frame(label=f"Ollama Model #{i}")
            frame.set_shadow_type(Gtk.ShadowType.IN)
            model_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            model_box.set_border_width(10)
            
            # Display name
            name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            name_label = Gtk.Label(label="Display Name:")
            name_label.set_size_request(120, -1)
            name_entry = Gtk.Entry()
            name_entry.set_placeholder_text("e.g., Llama 3.3")
            name_box.pack_start(name_label, False, False, 0)
            name_box.pack_start(name_entry, True, True, 0)
            model_box.pack_start(name_box, False, False, 3)
            
            # Model ID
            id_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            id_label = Gtk.Label(label="Model ID:")
            id_label.set_size_request(120, -1)
            id_entry = Gtk.Entry()
            id_entry.set_placeholder_text("e.g., llama3.3 or ollama/llama3.3")
            id_box.pack_start(id_label, False, False, 0)
            id_box.pack_start(id_entry, True, True, 0)
            model_box.pack_start(id_box, False, False, 3)
            
            frame.add(model_box)
            box.pack_start(frame, False, False, 5)
            
            self.ollama_model_entries[f"ollama_model_{i}"] = {
                "name": name_entry,
                "model_id": id_entry
            }
        
        # Load existing settings
        self._load_ollama_settings()
        
        scrolled.add_with_viewport(box)
        return scrolled
    
    def _create_menu_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<b>Show/Hide Menu Items</b>")
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 5)
        
        # Separator
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)
        
        # Menu items with checkboxes
        self.menu_checkboxes = {}
        
        menu_items = [
            ("oc_models", "OC Models submenu"),
            ("oc_start", "OC Start"),
            ("oc_stop", "OC Stop"),
            ("oc_restart", "OC Restart"),
            ("oc_dashboard", "OC Dashboard"),
            ("oc_json", "OC Json"),
            ("oc_folder", "OC Folder"),
            ("oc_doctor", "OC Doctor")
        ]
        
        for item_id, label_text in menu_items:
            check = Gtk.CheckButton.new_with_label(label_text)
            check.set_halign(Gtk.Align.START)
            check.set_active(True)  # Default enabled
            box.pack_start(check, False, False, 3)
            self.menu_checkboxes[item_id] = check
        
        # Load current settings
        self._load_menu_settings()
        
        # Separator before custom items
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 10)
        
        # Custom menu items section
        custom_title = Gtk.Label()
        custom_title.set_markup("<b>Custom Menu Items</b>")
        custom_title.set_halign(Gtk.Align.START)
        box.pack_start(custom_title, False, False, 5)
        
        # Custom item input fields
        self.custom_entries = {}
        
        for i in range(1, 4):
            # Custom item frame
            custom_frame = Gtk.Frame(label=f"Custom #{i}")
            custom_frame.set_shadow_type(Gtk.ShadowType.IN)
            custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            custom_box.set_border_width(10)
            
            # Title input
            title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            title_label = Gtk.Label(label="Title:")
            title_label.set_size_request(80, -1)
            title_entry = Gtk.Entry()
            title_entry.set_placeholder_text("Menu item title")
            title_box.pack_start(title_label, False, False, 0)
            title_box.pack_start(title_entry, True, True, 0)
            custom_box.pack_start(title_box, False, False, 3)
            
            # Command input
            cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            cmd_label = Gtk.Label(label="Command:")
            cmd_label.set_size_request(80, -1)
            cmd_entry = Gtk.Entry()
            cmd_entry.set_placeholder_text("Command to run")
            cmd_box.pack_start(cmd_label, False, False, 0)
            cmd_box.pack_start(cmd_entry, True, True, 0)
            custom_box.pack_start(cmd_box, False, False, 3)
            
            custom_frame.add(custom_box)
            box.pack_start(custom_frame, False, False, 5)
            
            # Store references
            self.custom_entries[f"custom_{i}"] = {
                "title": title_entry,
                "command": cmd_entry
            }
        
        # Load custom items
        self._load_custom_items()
        
        scrolled.add_with_viewport(box)
        return scrolled
    
    def _load_menu_settings(self):
        """Load menu visibility settings from JSON"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
                    for item_id, checkbox in self.menu_checkboxes.items():
                        if item_id in menu_config:
                            checkbox.set_active(menu_config[item_id].get('enabled', True))
        except Exception as e:
            print(f"Error loading menu settings: {e}")

    def _load_custom_items(self):
        """Load custom menu items from JSON"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
                    for i in range(1, 4):
                        key = f"custom_{i}"
                        if key in menu_config and key in self.custom_entries:
                            self.custom_entries[key]["title"].set_text(menu_config[key].get("title", ""))
                            self.custom_entries[key]["command"].set_text(menu_config[key].get("command", ""))
        except Exception as e:
            print(f"Error loading custom items: {e}")

    def _save_custom_items(self):
        """Save custom menu items to JSON"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            
            # Load existing or create new
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
            else:
                menu_config = {}
            
            # Save custom items
            for i in range(1, 4):
                key = f"custom_{i}"
                if key in self.custom_entries:
                    title = self.custom_entries[key]["title"].get_text().strip()
                    command = self.custom_entries[key]["command"].get_text().strip()
                    
                    if title or command:  # Only save if there's content
                        menu_config[key] = {
                            "title": title,
                            "command": command,
                            "enabled": True
                        }
                    elif key in menu_config:
                        # Remove if empty
                        del menu_config[key]
            
            with open(menu_json_path, 'w') as f:
                json.dump(menu_config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving custom items: {e}")
            return False

    def _load_manual_models(self):
        """Load manual model entries from JSON"""
        try:
            models_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/models.json")
            if os.path.exists(models_json_path):
                with open(models_json_path, 'r') as f:
                    models = json.load(f)
                    
                # Find manual models (those with manual_ prefix in id)
                manual_index = 1
                for model in models:
                    if model.get('id', '').startswith('manual_'):
                        key = f"manual_model_{manual_index}"
                        if key in self.manual_model_entries and manual_index <= 10:
                            self.manual_model_entries[key]["title"].set_text(model.get('name', ''))
                            self.manual_model_entries[key]["model_id"].set_text(model.get('id', '').replace('manual_', ''))
                            manual_index += 1
        except Exception as e:
            print(f"Error loading manual models: {e}")

    def _save_manual_models(self):
        """Save manual models to models.json"""
        try:
            models_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/models.json")
            
            # Load existing models
            if os.path.exists(models_json_path):
                with open(models_json_path, 'r') as f:
                    models = json.load(f)
            else:
                models = []
            
            # Remove existing manual models
            models = [m for m in models if not m.get('id', '').startswith('manual_')]
            
            # Add new manual models
            for i in range(1, 11):
                key = f"manual_model_{i}"
                if key in self.manual_model_entries:
                    title = self.manual_model_entries[key]["title"].get_text().strip()
                    model_id = self.manual_model_entries[key]["model_id"].get_text().strip()
                    
                    if title and model_id:
                        cmd = f"/usr/bin/openclaw sessions patch agent:main:main --model {model_id} && /usr/bin/openclaw sessions clear"
                        models.append({
                            "id": f"manual_{model_id}",
                            "name": title,
                            "cmd": cmd
                        })
            
            with open(models_json_path, 'w') as f:
                json.dump(models, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving manual models: {e}")
            return False

    def _load_ollama_settings(self):
        """Load Ollama settings from menu.json"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
                
                # Load Ollama config
                if 'ollama' in menu_config:
                    ollama = menu_config['ollama']
                    self.ollama_enabled_check.set_active(ollama.get('enabled', False))
                    self.ollama_custom_check.set_active(ollama.get('custom_address', False))
                    self.ollama_ip_entry.set_text(ollama.get('ip', '127.0.0.1'))
                    self.ollama_port_entry.set_text(str(ollama.get('port', 11434)))
                    
                    # Load models
                    for i, model in enumerate(ollama.get('models', []), 1):
                        key = f"ollama_model_{i}"
                        if key in self.ollama_model_entries and i <= 10:
                            self.ollama_model_entries[key]["name"].set_text(model.get('name', ''))
                            self.ollama_model_entries[key]["model_id"].set_text(model.get('id', ''))
        except Exception as e:
            print(f"Error loading Ollama settings: {e}")

    def _save_ollama_settings(self):
        """Save Ollama settings to menu.json and models to models.json"""
        try:
            menu_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/menu.json")
            models_json_path = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/models.json")
            
            # Load existing configs
            if os.path.exists(menu_json_path):
                with open(menu_json_path, 'r') as f:
                    menu_config = json.load(f)
            else:
                menu_config = {}
            
            if os.path.exists(models_json_path):
                with open(models_json_path, 'r') as f:
                    models = json.load(f)
            else:
                models = []
            
            # Remove existing Ollama models from models.json
            models = [m for m in models if not m.get('id', '').startswith('ollama/')]
            
            # Build Ollama config
            ollama_models = []
            for i in range(1, 11):
                key = f"ollama_model_{i}"
                if key in self.ollama_model_entries:
                    name = self.ollama_model_entries[key]["name"].get_text().strip()
                    model_id = self.ollama_model_entries[key]["model_id"].get_text().strip()
                    
                    if name and model_id:
                        # Ensure model_id has ollama/ prefix
                        if not model_id.startswith('ollama/'):
                            model_id = f"ollama/{model_id}"
                        
                        cmd = f"/usr/bin/openclaw sessions patch agent:main:main --model {model_id} && /usr/bin/openclaw sessions clear"
                        ollama_models.append({"name": name, "id": model_id})
                        models.append({"id": model_id, "name": name, "cmd": cmd})
            
            menu_config['ollama'] = {
                'enabled': self.ollama_enabled_check.get_active(),
                'custom_address': self.ollama_custom_check.get_active(),
                'ip': self.ollama_ip_entry.get_text().strip() or '127.0.0.1',
                'port': int(self.ollama_port_entry.get_text().strip() or '11434'),
                'models': ollama_models
            }
            
            # Save configs
            with open(menu_json_path, 'w') as f:
                json.dump(menu_config, f, indent=4)
            
            with open(models_json_path, 'w') as f:
                json.dump(models, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving Ollama settings: {e}")
            return False

if __name__ == "__main__":
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", True)
    
    dialog = SettingsWindow()
    response = dialog.run()
    
    if response == Gtk.ResponseType.CANCEL:
        print("Settings cancelled")
    elif response == Gtk.ResponseType.OK:
        models_saved = dialog._save_models_to_json()
        menu_saved = dialog._save_menu_settings()
        custom_saved = dialog._save_custom_items()
        manual_saved = dialog._save_manual_models()
        ollama_saved = dialog._save_ollama_settings()
        if models_saved and menu_saved and custom_saved and manual_saved and ollama_saved:
            print("Settings saved")
        else:
            print("Failed to save settings")
    
    dialog.destroy()
