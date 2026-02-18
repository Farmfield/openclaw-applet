//Claw Control v1 by farmfield

const UUID = "oc-applet@farmfield.se";
const Lang = imports.lang;
const St = imports.gi.St;
const Clutter = imports.gi.Clutter;
const Applet = imports.ui.applet;
const Main = imports.ui.main;
const PopupMenu = imports.ui.popupMenu;
const Util = imports.misc.util;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;

const ICON_NAME = "claw-control-icon";

function MyApplet(metadata, orientation, panelHeight, instanceId) {
    this.metadata = metadata;
    this.orientation = orientation;
    this._init(orientation, panelHeight, instanceId);
}

MyApplet.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _init: function(orientation, panelHeight, instanceId) {
        Applet.IconApplet.prototype._init.call(this, orientation, panelHeight, instanceId);

        // Set tooltip
        this.set_applet_tooltip("OC-Applet");

        // Load icon
        this._loadIcon();

        // Setup popup menu
        this._setupMenu();
    },

    _loadIcon: function() {
        global.log("OC-Applet: Starting icon load");
        
        // Use set_applet_icon_name with the icon name (no extension)
        // This works for icons in the icons/ subdirectory
        try {
            this.set_applet_icon_name(ICON_NAME);
            global.log("OC-Applet: Icon set via set_applet_icon_name: " + ICON_NAME);
        }
        catch (e) {
            global.logError("OC-Applet: set_applet_icon_name failed: " + e);
        }
    },

    _loadModels: function() {
        try {
            let modelsPath = GLib.build_filenamev([global.userdatadir, "applets", UUID, "models.json"]);
            global.log("OC-Applet: Loading models from: " + modelsPath);
            
            if (GLib.file_test(modelsPath, GLib.FileTest.EXISTS)) {
                let [success, contents] = GLib.file_get_contents(modelsPath);
                if (success) {
                    let models = JSON.parse(contents);
                    global.log("OC-Applet: Models loaded successfully");
                    return models;
                } else {
                    global.logError("OC-Applet: Failed to read models file");
                }
            } else {
                global.log("OC-Applet: Models file not found at: " + modelsPath);
            }
        } catch (e) {
            global.logError("OC-Applet: Error loading models: " + e);
        }
        return null;
    },

    _loadMenuSettings: function() {
        try {
            let menuPath = GLib.build_filenamev([global.userdatadir, "applets", UUID, "menu.json"]);
            if (GLib.file_test(menuPath, GLib.FileTest.EXISTS)) {
                let [success, contents] = GLib.file_get_contents(menuPath);
                if (success) {
                    return JSON.parse(contents);
                }
            }
        } catch (e) {
            global.logError("OC-Applet: Error loading menu settings: " + e);
        }
        // Return defaults if no file or error
        return {
            "title": {"enabled": true, "text": "Claw Control"},
            "oc_models": {"enabled": true, "label": "OC Models"},
            "oc_start": {"enabled": true, "label": "OC Start"},
            "oc_stop": {"enabled": true, "label": "OC Stop"},
            "oc_restart": {"enabled": true, "label": "OC Restart"},
            "oc_dashboard": {"enabled": true, "label": "OC Dashboard"},
            "oc_json": {"enabled": true, "label": "OC Json"},
            "oc_folder": {"enabled": true, "label": "OC Folder"},
            "oc_doctor": {"enabled": true, "label": "OC Doctor"},
            "settings": {"enabled": true, "label": "Settings"},
            "credits": {"enabled": true, "text": "v1 - ByFarmfield - 2026"}
        };
    },

    _isEnabled: function(menuConfig, key) {
        return menuConfig[key] && menuConfig[key].enabled !== false;
    },

    _getLabel: function(menuConfig, key, defaultLabel) {
        if (menuConfig[key] && menuConfig[key].label) {
            return menuConfig[key].label;
        }
        if (menuConfig[key] && menuConfig[key].text) {
            return menuConfig[key].text;
        }
        return defaultLabel;
    },

    _setupMenu: function() {
        try {
            this.menuManager = new PopupMenu.PopupMenuManager(this);
            this.menu = new Applet.AppletPopupMenu(this, this.orientation);
            this.menuManager.addMenu(this.menu);

            // Add custom style class and ID for targeting
            this.menu.box.add_style_class_name('oc-menu-box');
            this.menu.box.set_name('OC-Applet');
            
            // Fix margins and spacing
            this.menu.box.set_style('padding: 0px; margin: 0px; spacing: 0px;');
            this.menu.actor.set_style('padding: 0px; margin: 0px;');
            
            // Fix: Set fixed width to prevent layout recalculation shiver
            this.menu.box.set_width(230);

            // Build menu content
            this._buildMenuContent();
        }
        catch (e) {
            global.logError("OC-Applet: Failed to setup menu: " + e);
        }
    },

    _buildMenuContent: function() {
        // Remove all existing items first
        this.menu.removeAll();
        let children = this.menu.box.get_children();
        for (let i = children.length - 1; i >= 0; i--) {
            this.menu.box.remove_actor(children[i]);
        }
        
        // Load menu settings fresh
        let menuConfig = this._loadMenuSettings();

        // Title at top (centered) - add directly to menu box
        if (this._isEnabled(menuConfig, "title")) {
            let titleText = this._getLabel(menuConfig, "title", "Claw Control");
            let titleLabel = new St.Label({ text: titleText, style: "font-size: 14px; font-weight: bold;" });
            this.menu.box.add(titleLabel, { expand: true, x_fill: false, x_align: St.Align.MIDDLE });
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        }

            // Submenu: OC Models (click to open dropdown)
            if (this._isEnabled(menuConfig, "oc_models")) {
                let modelsLabel = this._getLabel(menuConfig, "oc_models", "OC Models");
                this.modelsSubmenu = new PopupMenu.PopupSubMenuMenuItem(modelsLabel, true);
                this.modelsSubmenu.menu._hoverEnabled = false;
                this._refreshModelsMenu();
                this.menu.addMenuItem(this.modelsSubmenu);
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            }

            // Menu Item: OC Start
            if (this._isEnabled(menuConfig, "oc_start")) {
                let label = this._getLabel(menuConfig, "oc_start", "OC Start");
                let item = new PopupMenu.PopupIconMenuItem(label, "start-gateway-icon", St.IconType.FULLCOLOR);
                item.connect('activate', Lang.bind(this, function() {
                    global.log("OC-Applet: OC Start clicked");
                    Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway start'");
                    this.menu.close();
                }));
                this.menu.addMenuItem(item);
            }

            // Menu Item: OC Stop
            if (this._isEnabled(menuConfig, "oc_stop")) {
                let label = this._getLabel(menuConfig, "oc_stop", "OC Stop");
                let item = new PopupMenu.PopupIconMenuItem(label, "stop-gateway-icon", St.IconType.FULLCOLOR);
                item.connect('activate', Lang.bind(this, function() {
                    global.log("OC-Applet: OC Stop clicked");
                    Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway stop'");
                    this.menu.close();
                }));
                this.menu.addMenuItem(item);
            }

            // Menu Item: OC Restart
            if (this._isEnabled(menuConfig, "oc_restart")) {
                let label = this._getLabel(menuConfig, "oc_restart", "OC Restart");
                let item = new PopupMenu.PopupIconMenuItem(label, "restart-gateway-icon", St.IconType.FULLCOLOR);
                item.connect('activate', Lang.bind(this, function() {
                    global.log("OC-Applet: OC Restart clicked");
                    Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway restart'");
                    this.menu.close();
                }));
                this.menu.addMenuItem(item);
            }

            // Separator and Dashboard
            if (this._isEnabled(menuConfig, "oc_dashboard")) {
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                let label = this._getLabel(menuConfig, "oc_dashboard", "OC Dashboard");
                let item = new PopupMenu.PopupIconMenuItem(label, "oc-open-dashboard", St.IconType.FULLCOLOR);
                item.connect('activate', Lang.bind(this, function() {
                    Util.spawnCommandLine("xdg-open http://127.0.0.1:18789/");
                    this.menu.close();
                }));
                this.menu.addMenuItem(item);
            }

            // Separator and Json/Folder
            if (this._isEnabled(menuConfig, "oc_json") || this._isEnabled(menuConfig, "oc_folder")) {
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                
                if (this._isEnabled(menuConfig, "oc_json")) {
                    let label = this._getLabel(menuConfig, "oc_json", "OC Json");
                    let item = new PopupMenu.PopupIconMenuItem(label, "oc-json-icon", St.IconType.FULLCOLOR);
                    item.connect('activate', Lang.bind(this, function() {
                        let homeDir = GLib.get_home_dir();
                        Util.spawnCommandLine("xdg-open " + homeDir + "/.openclaw/openclaw.json");
                        this.menu.close();
                    }));
                    this.menu.addMenuItem(item);
                }
                
                if (this._isEnabled(menuConfig, "oc_folder")) {
                    let label = this._getLabel(menuConfig, "oc_folder", "OC Folder");
                    let item = new PopupMenu.PopupIconMenuItem(label, "oc_folder_open", St.IconType.FULLCOLOR);
                    item.connect('activate', Lang.bind(this, function() {
                        let homeDir = GLib.get_home_dir();
                        Util.spawnCommandLine("xdg-open " + homeDir + "/.openclaw/");
                        this.menu.close();
                    }));
                    this.menu.addMenuItem(item);
                }
            }

            // Separator and Doctor
            if (this._isEnabled(menuConfig, "oc_doctor")) {
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                let label = this._getLabel(menuConfig, "oc_doctor", "OC Doctor");
                let item = new PopupMenu.PopupIconMenuItem(label, "oc-doctor-icon", St.IconType.FULLCOLOR);
                item.connect('activate', Lang.bind(this, function() {
                    Util.spawnCommandLine("x-terminal-emulator -e 'bash -c \"/usr/bin/openclaw doctor --fix; echo; echo Press Enter to close; read\"'");
                    this.menu.close();
                }));
                this.menu.addMenuItem(item);
            }

            // Custom menu items
            this._addCustomMenuItems(menuConfig);

            // Footer separator and settings
            if (this._isEnabled(menuConfig, "settings") || this._isEnabled(menuConfig, "credits")) {
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                
                if (this._isEnabled(menuConfig, "settings")) {
                    let label = this._getLabel(menuConfig, "settings", "Settings");
                    let settingsItem = new PopupMenu.PopupIconMenuItem(label, "settings-icon", St.IconType.FULLCOLOR);
                    settingsItem.label.set_style("font-size: 9px;");
                    settingsItem.connect('activate', Lang.bind(this, this._showSettings));
                    this.menu.addMenuItem(settingsItem);
                }
                
                if (this._isEnabled(menuConfig, "credits")) {
                    let creditsText = this._getLabel(menuConfig, "credits", "v1 - ByFarmfield - 2026");
                    let versionLabel = new St.Label({ text: creditsText, style: "font-size: 9px; color: #888888;" });
                    this.menu.box.add(versionLabel, { expand: true, x_fill: false, x_align: St.Align.END });
                }

                // Spacer at bottom
                let bottomSpacer = new St.Label({ text: "" });
                bottomSpacer.set_height(5);
                this.menu.box.add(bottomSpacer, { expand: false, x_fill: true });
            }
    },

    _addCustomMenuItems: function(menuConfig) {
        // Add custom items if they exist and are enabled
        for (let i = 1; i <= 3; i++) {
            let key = "custom_" + i;
            if (menuConfig[key] && menuConfig[key].enabled !== false) {
                let title = menuConfig[key].title || "Custom " + i;
                let command = menuConfig[key].command || "";
                
                if (title && command) {
                    // Add separator before first custom item
                    if (i === 1) {
                        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                    }
                    
                    let item = new PopupMenu.PopupIconMenuItem(title, "custom-menu-icon", St.IconType.FULLCOLOR);
                    item.connect('activate', Lang.bind(this, function(cmd) {
                        return function() {
                            Util.spawnCommandLine("bash -c '" + cmd + "'");
                            this.menu.close();
                        };
                    }(command)));
                    this.menu.addMenuItem(item);
                }
            }
        }
    },

    _refreshModelsMenu: function() {
        // Clear existing items
        this.modelsSubmenu.menu.removeAll();
        
        // Load models from JSON file
        let models = this._loadModels();
        
        global.log("OC-Applet: Models reloaded from JSON: " + JSON.stringify(models));
        
        // Fallback to empty if load failed
        if (!models) {
            global.logError("OC-Applet: Failed to load models, using empty list");
            models = [];
        }
        
        // Add "No models" message if empty
        if (models.length === 0) {
            let emptyItem = new PopupMenu.PopupMenuItem("No models configured");
            emptyItem.setSensitive(false);
            this.modelsSubmenu.menu.addMenuItem(emptyItem);
        } else {
            // Group models by provider
            let modelsByProvider = {};
            for (let i = 0; i < models.length; i++) {
                let m = models[i];
                let provider = "Other";
                
                // Extract provider from cmd field (e.g., "openclaw models set openrouter/google/...")
                if (m.cmd) {
                    let cmdMatch = m.cmd.match(/set\s+(\S+)/);
                    if (cmdMatch) {
                        let fullModel = cmdMatch[1];
                        // Handle manual_ prefix
                        if (fullModel.startsWith("manual_")) {
                            fullModel = fullModel.substring(7);
                        }
                        // Extract provider from provider/model format
                        if (fullModel.indexOf('/') >= 0) {
                            let parts = fullModel.split('/');
                            provider = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
                        }
                    }
                }
                // Fallback: check if id contains provider/model format
                if (provider === "Other" && m.id.indexOf('/') >= 0) {
                    let modelId = m.id;
                    if (modelId.startsWith("manual_")) {
                        modelId = modelId.substring(7);
                    }
                    let parts = modelId.split('/');
                    provider = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
                }
                
                if (!modelsByProvider[provider]) {
                    modelsByProvider[provider] = [];
                }
                modelsByProvider[provider].push(m);
            }
            
            // Sort providers alphabetically
            let sortedProviders = Object.keys(modelsByProvider).sort();
            
            // Add models grouped by provider
            let isFirstProvider = true;
            for (let j = 0; j < sortedProviders.length; j++) {
                let provider = sortedProviders[j];
                let providerModels = modelsByProvider[provider];
                
                // Add separator between providers (but not before first)
                if (!isFirstProvider) {
                    this.modelsSubmenu.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                }
                isFirstProvider = false;
                
                // Add provider header (small font)
                let headerItem = new PopupMenu.PopupMenuItem(provider + ":");
                headerItem.label.set_style("font-size: 8px; font-weight: bold; color: #888888;");
                headerItem.setSensitive(false);
                this.modelsSubmenu.menu.addMenuItem(headerItem);
                
                // Add models for this provider
                for (let i = 0; i < providerModels.length; i++) {
                    let m = providerModels[i];
                    
                    // Extract display name from model ID or name
                    let displayName = m.name;
                    
                    // If name looks like a path (contains /), extract just the model part
                    if (displayName.indexOf('/') >= 0) {
                        let parts = displayName.split('/');
                        // Get last part and clean it up
                        displayName = parts[parts.length - 1];
                        // Replace dashes with spaces and title case
                        displayName = displayName.replace(/-/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); });
                    }
                    
                    // Strip provider prefix if present (e.g., "Openrouter ")
                    let providerPrefix = provider.toLowerCase();
                    if (displayName.toLowerCase().startsWith(providerPrefix + " ")) {
                        displayName = displayName.substring(providerPrefix.length + 1);
                    }
                    
                    // Truncate to 25 chars max with ellipsis
                    if (displayName.length > 25) {
                        displayName = displayName.substring(0, 25) + "...";
                    }
                    
                    let mItem = new PopupMenu.PopupMenuItem("  " + displayName);
                    // Fix closure capture with let
                    let cmd = m.cmd;
                    let name = m.name;
                    mItem.connect('activate', Lang.bind(this, function() {
                        global.log("OC-Applet: CLICKED model=" + name + ", cmd=" + cmd);
                        if (cmd) {
                            Util.spawnCommandLine("bash -c '" + cmd + "'");
                            Main.notify("Claw Control", "Switched to " + name);
                        }
                        this.menu.close();
                    }));
                    this.modelsSubmenu.menu.addMenuItem(mItem);
                }
            }
        }
    },

    on_applet_clicked: function(event) {
        // Rebuild menu content each time to pick up setting changes
        this._buildMenuContent();
        this.menu.toggle();
    },

    _showSettings: function() {
        this.menu.close();
        
        // Get the applet directory path
        let settingsScript = GLib.build_filenamev([this.metadata.path, "settings-window.py"]);
        
        // Launch the settings window as a separate process
        Util.spawnCommandLine("python3 " + settingsScript);
    },
};

function main(metadata, orientation, panelHeight, instanceId) {
    let myApplet = new MyApplet(metadata, orientation, panelHeight, instanceId);
    return myApplet;
}
