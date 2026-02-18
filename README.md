# Smart URL Opener - Ulauncher Extension
An intelligent Ulauncher extension that provides smart URL completion, configurable search engines, domain shortcuts, and seamless web browsing with enhanced local development support. 
- Download [ULauncher](https://ulauncher.io/) application (like Spotlight Search for Linux)

## Features
### Configurable Search Engines
- **Custom Search**: Choose your preferred search engine in preferences.
- **Supported Engines**: Google, DuckDuckGo, Bing, Brave, Ecosia, and Yandex.
- **Smart Fallback**: Automatically searches your default engine if the input isn't a valid domain.

### Clipboard Support
- **Alt + Enter**: Press `Alt+Enter` on any result to copy the URL to your clipboard instead of opening it.

### Smart URL Completion
- **Automatic Protocol Detection**: Smartly selects `https://` for web domains and `http://` for local servers.
- **Protocol Toggling**: Offers options to "Force HTTP" or "Force HTTPS" for debugging.
- **File Path Support**: Handles local file paths with `file://` protocol.
- **Email Detection**: Automatically opens email addresses with `mailto:` protocol.
- **"www" Prefixing**: Suggests adding `www.` if a domain doesn't look right.

### Domain & Dev Shortcuts
Built-in shortcuts for popular websites and developers:
- `gh` → github.com
- `lh` → localhost:3000
- `lh8` → localhost:8000
- `lh80` → localhost:8080
- `chat` → chatgpt.com

## Installation
### Method 1: Manual Installation
1. Clone or download this repository
2. Copy the extension folder to your Ulauncher extensions directory:
```bash
~/.local/share/ulauncher/extensions/
```
3. Restart Ulauncher or go to Preferences → Extensions → Reload Extensions

### Method 2: From Ulauncher Extensions Directory
1. Open Ulauncher Preferences
2. Go to Extensions tab
3. Click "Add Extension"
4. Enter the extension URL from Github:
```bash
https://github.com/kcoovi/ulauncher-link-opener
```

## Usage
### Basic Usage
1. Open Ulauncher (default: `Ctrl+Space`)
2. Type your keyword (default: `go`) followed by a space
3. Enter your URL, domain, or search term
4. **Enter** to open in browser, or **Alt+Enter** to copy to clipboard.

### Examples
| Input | Result |
|-------|--------|
|`go` | Defaults to your selected Search Engine |
| `go github.com` | Opens https://github.com |
| `go gh` | Opens https://github.com (shortcut) |
| `go lh` | Opens http://localhost:3000 |
| `go 192.168.1.100` | Opens http://192.168.1.100 |
| `go ~/Documents/file.html` | Opens local file |
| `go user@example.com` | Opens email client |
| `go python tutorial` | Searches (Google/DDG/etc) for "python tutorial" |

### Shortcuts List
The extension includes shortcuts for popular websites:

**Developer Tools:**
- `gh` → github.com
- `gl` → gitlab.com
- `so` → stackoverflow.com
- `lh` → localhost:3000
- `lh8` → localhost:8000
- `lh80` → localhost:8080

**Social & Media:**
- `yt` → youtube.com
- `tw` → twitch.tv
- `reddit` → reddit.com
- `x` / `twitter` → x.com
- `fb` → facebook.com
- `ig` → instagram.com
- `linkedin` → linkedin.com

**Productivity & Shopping:**
- `chat` → chatgpt.com
- `docs` → docs.google.com
- `drive` → drive.google.com
- `maps` → maps.google.com
- `amzn` → amazon.com
- `nf` → netflix.com
- `wiki` → wikipedia.org

## Preferences
You can configure the following settings in Ulauncher preferences:

1.  **Search Engine**: Select between Google, DuckDuckGo, Bing, Brave, Ecosia, or Yandex.
2.  **Prefer HTTPS**: Default to HTTPS for domains (Yes/No).
3.  **Enable Shortcuts**: Enable/Disable the built-in shortcuts like `gh` or `yt`.
4.  **Max Suggestions**: Limit the number of results displayed.

## Gallery
<div align="center">
  <table>
    <tr>
      <td><img src="images/1.png" alt="Email Handling" width="700"></td>
      <td><img src="images/2.png" alt="Local File Handling" width="700"></td>
      <td><img src="images/3.png" alt="Domain Shortcut" width="700"></td>
    </tr>
    <tr>
      <td align="center"><b>Email Handling</b></td>
      <td align="center"><b>Local File Handling</b></td>
      <td align="center"><b>Domain Shortcut</b></td>
    </tr>
    <tr>
      <td><img src="images/4.png" alt="Localhost Development" width="700"></td>
      <td><img src="images/5.png" alt="Domain Suggestions" width="700"></td>
      <td></td>
    </tr>
    <tr>
      <td align="center"><b>Smart handling of localhost</b></td>
      <td align="center"><b>Intelligent completion</b></td>
      <td></td>
    </tr>
  </table>
</div>

## File Structure
```
smart-url-opener/
├── main.py              
├── manifest.json        
├── README.md           
└── images/
    ├── 1.png
    ├── 2.png
    ├── 3.png
    ├── 4.png
    └── 5.png
```

## Advanced Features
### Protocol Toggle
If you type a domain (e.g., `myserver.local`), the extension suggests the default protocol. However, it also provides an alternative option in the dropdown list to **force** the opposite protocol. 
*   Example: If it suggests `https://myserver.local`, the second option will be `http://myserver.local` (Force HTTP).

## Troubleshooting
### Extension Error in Results
If the extension crashes, the error message will now appear directly in the Ulauncher result list instead of loading indefinitely. 

### URLs Not Opening
1. Verify your default browser is set correctly.
2. If the URL looks correct in Ulauncher but fails in the browser, try using the "Force HTTP/HTTPS" option in the result list.

## Development
### Requirements
- Python 3.6+
- Ulauncher 5.0+

## License
This project is open source. Feel free to modify and distribute according to your needs.

## Changelog
### Version 3.0.0
- **New:** Configurable Search Engines (Google, DDG, Brave, etc).
- **New:** Clipboard Support (Alt+Enter).
- **New:** Localhost shortcuts (`lh`, `lh8`).
- **Improved:** Protocol handling with Force HTTP/HTTPS options.
- **Removed:** AI/Gemini integration.
