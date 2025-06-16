# uLauncher Default Browser Extension

Quickly open websites in your system's **default browser** using a simple keyword shortcut.

## Features

- **Default browser integration**: Uses your system-configured default browser  
- **Smart URL handling**:  
  - Opens `https://google.com` if input is empty  
  - Adds `.com` for plain keywords (e.g., `youtube` → `https://youtube.com`)  
  - Adds `https://` prefix if missing (e.g., `youtube.com` or `192.168.1.1`)  
  - Leaves full URLs intact if they already start with `http://` or `https://`  
- **Instant execution**: Opens websites immediately after typing  
- **Preview before opening**: Displays formatted URL before execution  
- **Cross-platform**: Works with Chrome, Firefox, Edge, Safari, etc.

## Usage

1. Activate uLauncher (`Alt + Space`)  
2. Type your keyword followed by the URL or search term:  
   Example:  
```

go github

```
3. Press `Enter` to open the link in your default browser

## Other Supported Formats

- **Plain keywords** (converted to `.com` domains): `youtube` → `https://youtube.com`  
- **Domain names**: `example.com`  
- **Full URLs**: `https://example.com`  
- **IP addresses**: `192.168.1.1`  
- **Localhost**: `localhost:8000`  
- **Empty input**: opens `https://google.com`  
- **File paths**: `file:///home/user/file.pdf`


