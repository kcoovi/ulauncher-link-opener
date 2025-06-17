from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
import webbrowser

def complete_url(url):
    """Format URL for browser compatibility"""
    if not url:
        return "https://google.com"
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


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
