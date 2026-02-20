#!/usr/bin/env python3
import gi
import json
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

MODELS_JSON_PATH = os.path.expanduser("~/.local/share/cinnamon/applets/oc-applet@farmfield.se/models.json")

class SettingsWindow(Gtk.Dialog):
    def __init__(self):
        super().__init__(title="OC Applet Settings")
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
        
        # Tab 1: Model List
        tab1 = self._create_model_list_tab()
        notebook.append_page(tab1, Gtk.Label(label="Model List"))
        
        # Tab 2: Model List (manual)
        tab2 = self._create_manual_tab()
        notebook.append_page(tab2, Gtk.Label(label="Model List (manual)"))
        
        # Tab 3: Local Models
        tab3 = self._create_local_tab()
        notebook.append_page(tab3, Gtk.Label(label="Local Models"))
        
        content.pack_start(notebook, True, True, 0)
        
        # Load current models from JSON
        self._load_models_from_json()
        
        self.show_all()
    
    def _load_models_from_json(self):
        """Load existing models from JSON and check appropriate boxes"""
        try:
            if os.path.exists(MODELS_JSON_PATH):
                with open(MODELS_JSON_PATH, 'r') as f:
                    models = json.load(f)
                    active_ids = {m['id'] for m in models}
                    
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
                # Get display name from label text (remove provider prefix for cleaner name)
                parts = model_id.split('/')
                if len(parts) >= 2:
                    # Use last part as base name, title case it
                    base_name = parts[-1].replace('-', ' ').title()
                    provider = parts[-2].title() if len(parts) > 2 else parts[0].title()
                    name = f"{provider} {base_name}"
                else:
                    name = model_id
                
                models.append({
                    "id": model_id,
                    "name": name
                })
        
        try:
            with open(MODELS_JSON_PATH, 'w') as f:
                json.dump(models, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving models: {e}")
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
            ("MiniMax", [
                ("minimax/minimax-m2.5", "Minimax M2.5")
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
            ("openrouter/google/gemini-3-pro", "Google Gemini 3 Pro"),
            ("openrouter/google/gemini-3-flash", "Google Gemini 3 Flash"),
            ("openrouter/moonshotai/kimi-k2.5", "Moonshot Kimi K2.5"),
            ("openrouter/minimax/minimax-m2.5", "Minimax M2.5"),
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
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        
        label = Gtk.Label(label="Manual model configuration will go here...")
        box.pack_start(label, False, False, 0)
        
        scrolled.add_with_viewport(box)
        return scrolled
    
    def _create_local_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        
        label = Gtk.Label(label="Local models configuration will go here...")
        box.pack_start(label, False, False, 0)
        
        scrolled.add_with_viewport(box)
        return scrolled

if __name__ == "__main__":
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", True)
    
    dialog = SettingsWindow()
    response = dialog.run()
    
    if response == Gtk.ResponseType.CANCEL:
        print("Settings cancelled")
    elif response == Gtk.ResponseType.OK:
        if dialog._save_models_to_json():
            print("Settings saved")
        else:
            print("Failed to save settings")
    
    dialog.destroy()
