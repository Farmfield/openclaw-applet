//OC-Applet v2 by farmfield

const UUID = "oc-applet@farmfield.se";
const Lang = imports.lang;
const St = imports.gi.St;
const Applet = imports.ui.applet;
const Main = imports.ui.main;
const PopupMenu = imports.ui.popupMenu;
const Util = imports.misc.util;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;

const ICON_NAME = "oc-applet-trey-icon";

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

            // Submenu: OC Models (click to open dropdown)
            let modelsSubmenu = new PopupMenu.PopupSubMenuMenuItem("OC Models", true);
            
            // Disable default hover behavior - only open on click
            modelsSubmenu.menu._hoverEnabled = false;
            
            // Model items
            let models = [
                {name: "Gemini 2.5 Flash Lite", cmd: "/usr/bin/openclaw models set openrouter/google/gemini-2.5-flash-lite-preview-09-2025"},
                {name: "DeepSeek 3.2", cmd: "/usr/bin/openclaw models set openrouter/deepseek/deepseek-v3.2"},
                {name: "Kimi K2.5", cmd: "/usr/bin/openclaw models set openrouter/moonshotai/kimi-k2.5"},
                {name: "GPT-5 Nano", cmd: "/usr/bin/openclaw models set openai/gpt-5-nano"},
                {name: "Minimax M2.5", cmd: "/usr/bin/openclaw models set openrouter/minimax/minimax-m2.5"},
                {name: "Grok 4.1 Fast", cmd: "/usr/bin/openclaw models set openrouter/x-ai/grok-4.1-fast"},
                {name: "GPT-5.2", cmd: "/usr/bin/openclaw models set openrouter/openai/gpt-5.2"},
                {name: "Claude Opus 4.6", cmd: "/usr/bin/openclaw models set openrouter/anthropic/claude-opus-4.6"}
            ];
            
            for (let i = 0; i < models.length; i++) {
                let m = models[i];
                let mItem = new PopupMenu.PopupMenuItem(m.name);
                mItem.connect('activate', Lang.bind(this, function() {
                    Util.spawnCommandLine(m.cmd);
                    Main.notify("OC Models", "Switched to " + m.name);
                    this.menu.close();
                }));
                modelsSubmenu.menu.addMenuItem(mItem);
            }
            
            this.menu.addMenuItem(modelsSubmenu);

            // Menu Item 1: OC Start
            let item1 = new PopupMenu.PopupIconMenuItem(
                "OC Start",
                "start-gateway-icon",
                St.IconType.FULLCOLOR
            );
            item1.connect('activate', Lang.bind(this, function() {
                global.log("OC-Applet: OC Start clicked");
                Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway start'");
                this.menu.close();
            }));
            this.menu.addMenuItem(item1);

            // Menu Item 2: OC Stop
            let item2 = new PopupMenu.PopupIconMenuItem(
                "OC Stop",
                "stop-gateway-icon",
                St.IconType.FULLCOLOR
            );
            item2.connect('activate', Lang.bind(this, function() {
                global.log("OC-Applet: OC Stop clicked");
                Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway stop'");
                this.menu.close();
            }));
            this.menu.addMenuItem(item2);

            // Menu Item 3: OC Restart
            let item3 = new PopupMenu.PopupIconMenuItem(
                "OC Restart",
                "restart-gateway-icon",
                St.IconType.FULLCOLOR
            );
            item3.connect('activate', Lang.bind(this, function() {
                global.log("OC-Applet: OC Restart clicked");
                Util.spawnCommandLine("bash -c '/usr/bin/openclaw gateway restart'");
                this.menu.close();
            }));
            this.menu.addMenuItem(item3);

            // Menu Item 4: OC Dashboard
            let item4 = new PopupMenu.PopupIconMenuItem(
                "OC Dashboard",
                "oc-open-dashboard",
                St.IconType.FULLCOLOR
            );
            item4.connect('activate', Lang.bind(this, function() {
                Util.spawnCommandLine("xdg-open http://127.0.0.1:18789/");
                this.menu.close();
            }));
            this.menu.addMenuItem(item4);

            // Menu Item 5: OC Json (config)
            let item5 = new PopupMenu.PopupIconMenuItem(
                "OC Json",
                "oc-json-icon",
                St.IconType.FULLCOLOR
            );
            item5.connect('activate', Lang.bind(this, function() {
                let homeDir = GLib.get_home_dir();
                Util.spawnCommandLine("xdg-open " + homeDir + "/.openclaw/openclaw.json");
                this.menu.close();
            }));
            this.menu.addMenuItem(item5);

            // Menu Item 6: OC Folder
            let item6 = new PopupMenu.PopupIconMenuItem(
                "OC Folder",
                "oc_folder_open",
                St.IconType.FULLCOLOR
            );
            item6.connect('activate', Lang.bind(this, function() {
                let homeDir = GLib.get_home_dir();
                Util.spawnCommandLine("xdg-open " + homeDir + "/.openclaw/");
                this.menu.close();
            }));
            this.menu.addMenuItem(item6);

            // Menu Item 7: OC Doctor
            let item7 = new PopupMenu.PopupIconMenuItem(
                "OC Doctor",
                "oc-doctor-icon",
                St.IconType.FULLCOLOR
            );
            item7.connect('activate', Lang.bind(this, function() {
                Util.spawnCommandLine("x-terminal-emulator -e 'bash -c \"/usr/bin/openclaw doctor --fix; echo; echo Press Enter to close; read\"'");
                this.menu.close();
            }));
            this.menu.addMenuItem(item7);

        }
        catch (e) {
            global.logError("OC-Applet: Failed to setup menu: " + e);
        }
    },

    on_applet_clicked: function(event) {
        this.menu.toggle();
    },
};

function main(metadata, orientation, panelHeight, instanceId) {
    let myApplet = new MyApplet(metadata, orientation, panelHeight, instanceId);
    return myApplet;
}