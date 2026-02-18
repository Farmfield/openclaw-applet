# Claw Control

A **Cinnamon desktop environment** panel applet for managing [OpenClaw](https://github.com/openclaw/openclaw) gateway operations during configuration and debugging.

> ⚠️ **Cinnamon Only** - This applet uses Cinnamon-specific APIs and will not work on GNOME, KDE, or other desktop environments.

## Features

- **Model Switching** - Quick-switch between LLM models grouped by API provider
- **Gateway Control** - Start, stop, and restart the OpenClaw gateway
- **Configuration Access** - Open config files and workspace folder
- **Diagnostic Tools** - Run OpenClaw Doctor directly from the menu
- **Customizable Menu** - Show/hide menu items and add custom commands

## Installation

1. Clone or download this repository
2. Copy the `oc-applet@farmfield.se` folder to `~/.local/share/cinnamon/applets/`
3. Right-click the Cinnamon panel → **Applets** → **Claw Control** → Add to panel
4. Configure via the applet's Settings menu

## Requirements

- **Cinnamon desktop environment** (tested on Cinnamon 5.x+)
- OpenClaw CLI installed (`/usr/bin/openclaw`)

**Not compatible with:** GNOME, KDE Plasma, XFCE, or other desktop environments.

## Configuration

Right-click the applet icon and select **Settings** to configure:

- **Menu** - Toggle visibility of menu items and add custom commands
- **Model List** - Select which LLM models appear in the Models submenu
- **Manual Models** - Add custom models by provider/model ID
- **Ollama** - Configure local Ollama instance and models

## License

MIT License - See [LICENSE](LICENSE) file for details.

Use with attribution appreciated but not required.

## Credits

Created by Farmfield (Johnny Farmfield) - 2026
