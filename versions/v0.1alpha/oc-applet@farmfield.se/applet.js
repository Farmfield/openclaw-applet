//OC-Applet by farmfield

const UUID = "oc-applet@farmfield.se";
const Lang = imports.lang;
const St = imports.gi.St;
const Applet = imports.ui.applet;
const Main = imports.ui.main;
const PopupMenu = imports.ui.popupMenu;
const Util = imports.misc.util;
const TextureCache = St.TextureCache.get_default();

function MyApplet(orientation) {
    this._init(orientation);
}

MyApplet.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _init: function(orientation) {
        Applet.IconApplet.prototype._init.call(this, orientation);

        try {
            // Load icon using absolute path and TextureCache
            let iconPath = "/home/johnny/Documents/cinnanon-OC-applet-dev/assets/icons/oc-applet-trey-icon.svg";
            let iconTexture = TextureCache.load_uri_sync("file://" + iconPath);
            this.set_applet_icon_texture(iconTexture);
        }
        catch (e) {
            // Fallback to system-run icon if texture loading fails
            try {
                this.set_applet_icon_symbolic_name("system-run");
            }
            catch (fallbackError) {
                global.logError(fallbackError);
            }
        }

        try {
            this.set_applet_tooltip("OC-Applet");

            this.menuManager = new PopupMenu.PopupMenuManager(this);
            this.menu = new Applet.AppletPopupMenu(this, orientation);
            this.menuManager.addMenu(this.menu);

            this._contentSection = new PopupMenu.PopupMenuSection();
            this.menu.addMenuItem(this._contentSection);

            this.menu.addAction("Test Action", function(event) {
                Main.notify("OC-Applet", "Button clicked!");
            });
        }
        catch (e) {
            global.logError(e);
        }
    },

    on_applet_clicked: function(event) {
        this.menu.toggle();
    },
};

function main(metadata, orientation) {
    let myApplet = new MyApplet(orientation);
    return myApplet;
}
