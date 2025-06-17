from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
import webbrowser
import os
import re

def complete_url(url):
    """Format URL for browser compatibility with enhanced rules"""
    if not url:
        return "https://google.com"
    
    # Already has protocol or is file URI
    if re.match(r'^\w+://', url):
        return url
    
    # File path handling
    if url.startswith('/') or url.startswith('./') or url.startswith('../') or url.startswith('~'):
        if url.startswith('~'):
            url = os.path.expanduser(url)
        return "file://" + os.path.abspath(url)
    
    # IP address (IPv4 with optional port)
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
    if re.match(ipv4_pattern, url):
        return f'http://{url}' if url.startswith('192.168.') else f'https://{url}'
    
    # Localhost with optional port
    if url.startswith('localhost') or re.match(r'^localhost:\d+', url):
        return f'http://{url}'
    
    # Plain keyword (single word without special characters)
    if re.match(r'^[\w-]+$', url):
        return f'https://{url}.com'
    
    # Add protocol if missing
    return url if url.startswith(('http://', 'https://')) else f'https://{url}'


class DefaultBrowserExtension(Extension):
    def __init__(self):
        super(DefaultBrowserExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        url = event.get_argument() or ""
        completed_url = complete_url(url)
        
        return RenderResultListAction([
            ExtensionResultItem(
                icon='images/icon.png',
                name=f"Open in default browser",
                description=f"Will open: {completed_url}",
                on_enter=ExtensionCustomAction(
                    {"url": completed_url}, 
                    keep_app_open=False
                )
            )
        ])


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        webbrowser.open(data["url"])
        return RenderResultListAction([])  # Close window immediately


if __name__ == '__main__':
    DefaultBrowserExtension().run()
