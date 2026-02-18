from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
import webbrowser
import os
import re
import logging
from urllib.parse import urlparse, quote
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ICON = 'images/icon.png'

class URLHandler:
    """Enhanced URL handling with intelligent completion and validation"""
    
    # Common domain shortcuts
    DOMAIN_SHORTCUTS = {
        'gh': 'github.com',
        'github': 'github.com',
        'gl': 'gitlab.com',
        'google': 'google.com',
        'gmail': 'gmail.com',
        'yt': 'youtube.com',
        'youtube': 'youtube.com',
        'tw': 'twitch.tv',
        'so': 'stackoverflow.com',
        'reddit': 'reddit.com',
        'x': 'x.com',
        'twitter': 'x.com',
        'fb': 'facebook.com',
        'linkedin': 'linkedin.com',
        'ig': 'instagram.com',
        'wiki': 'wikipedia.org',
        'amzn': 'amazon.com',
        'nf': 'netflix.com',
        'chat': 'chatgpt.com',
        'docs': 'docs.google.com',
        'drive': 'drive.google.com',
        'maps': 'maps.google.com',
        # Developer shortcuts
        'lh': 'localhost:3000',
        'lh8': 'localhost:8000',
        'lh80': 'localhost:8080'
    }

    SEARCH_ENGINES = {
        'google': 'https://google.com/search?q={}',
        'duckduckgo': 'https://duckduckgo.com/?q={}',
        'bing': 'https://www.bing.com/search?q={}',
        'brave': 'https://search.brave.com/search?q={}',
        'ecosia': 'https://www.ecosia.org/search?q={}',
        'yandex': 'https://yandex.com/search/?text={}'
    }
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Validate domain format"""
        if not domain or len(domain) > 253:
            return False
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(domain_pattern, domain) is not None
    
    @classmethod
    def complete_url(cls, query: str, prefer_https: bool = True, enable_shortcuts: bool = True, search_engine: str = 'google') -> str:
        """Enhanced URL completion with intelligent handling"""
        
        # Safe handling of search engine key
        engine_key = str(search_engine).lower().strip()
        if engine_key not in cls.SEARCH_ENGINES:
            engine_key = 'google'
            
        if not query or not query.strip():
            return cls.SEARCH_ENGINES[engine_key].format("")
        
        query = query.strip()
        
        # Already has protocol
        if re.match(r'^\w+://', query):
            return query
        
        # File path handling
        if query.startswith(('/', './', '../', '~')):
            try:
                if query.startswith('~'):
                    query = os.path.expanduser(query)
                abs_path = os.path.abspath(query)
                return f"file://{abs_path}"
            except Exception:
                pass
        
        # IPv4 address handling
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        if re.match(ipv4_pattern, query):
            return f'http://{query}' # Default to http for IPs usually
        
        # Localhost variants
        if query.startswith('localhost'):
            return f'http://{query}'
        
        # Email address
        if '@' in query and '.' in query and ' ' not in query and not query.startswith('mailto:'):
             return f'mailto:{query}'
        
        # Domain shortcuts
        if enable_shortcuts:
            query_lower = query.lower()
            if query_lower in cls.DOMAIN_SHORTCUTS:
                target = cls.DOMAIN_SHORTCUTS[query_lower]
                # If shortcut target contains localhost, use http, else https
                proto = 'http' if 'localhost' in target else ('https' if prefer_https else 'http')
                return f'{proto}://{target}'
        
        # Single word without dots - try com
        if re.match(r'^[a-zA-Z0-9-]+$', query) and len(query) > 1:
            protocol = 'https' if prefer_https else 'http'
            return f'{protocol}://{query}.com'
        
        # Valid domain structure (has dot, no spaces)
        if '.' in query and ' ' not in query and cls.is_valid_domain(query):
            protocol = 'https' if prefer_https else 'http'
            return f'{protocol}://{query}'
        
        # Fallback: Search
        return cls.SEARCH_ENGINES[engine_key].format(quote(query))


class SmartBrowserExtension(Extension):
    """Smart Ulauncher extension for intelligent URL opening"""
    
    def __init__(self):
        super(SmartBrowserExtension, self).__init__()
        # Default preferences to avoid startup errors
        self.preferences = {
            'enable_shortcuts': True,
            'prefer_https': True,
            'max_suggestions': 5,
            'search_engine': 'Google'
        }
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())


class PreferencesEventListener(EventListener):
    """Initialize preferences on start"""
    def on_event(self, event: PreferencesEvent, extension: SmartBrowserExtension):
        # Convert 'Yes'/'No' strings from select to boolean safely
        extension.preferences['enable_shortcuts'] = event.preferences.get('enable_shortcuts', 'Yes') == 'Yes'
        extension.preferences['prefer_https'] = event.preferences.get('prefer_https', 'Yes') == 'Yes'
        
        try:
            val = event.preferences.get('max_suggestions', '5')
            extension.preferences['max_suggestions'] = int(val)
        except (ValueError, TypeError):
            extension.preferences['max_suggestions'] = 5
            
        extension.preferences['search_engine'] = event.preferences.get('search_engine', 'Google')


class PreferencesUpdateEventListener(EventListener):
    """Update preferences when changed"""
    def on_event(self, event: PreferencesUpdateEvent, extension: SmartBrowserExtension):
        if event.id == 'max_suggestions':
            try:
                extension.preferences[event.id] = int(event.new_value)
            except (ValueError, TypeError):
                pass
        elif event.id in ['enable_shortcuts', 'prefer_https']:
            # Handle boolean conversion from 'Yes'/'No'
            extension.preferences[event.id] = event.new_value == 'Yes'
        else:
            extension.preferences[event.id] = event.new_value


class KeywordQueryEventListener(EventListener):
    """Event listener with smart URL suggestions"""
    
    def on_event(self, event: KeywordQueryEvent, extension: SmartBrowserExtension):
        try:
            query = event.get_argument() or ""
            prefs = extension.preferences
            
            # Handle empty query
            engine_key = str(prefs.get('search_engine', 'Google')).lower()
            engine_display = prefs.get('search_engine', 'Google')
            
            if not query.strip():
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon=ICON,
                        name="Smart URL Opener",
                        description=f"Type to search on {engine_display} or enter a URL",
                        on_enter=ExtensionCustomAction({"url": "about:blank"}, keep_app_open=False)
                    )
                ])
            
            # Get Primary URL
            primary_url = URLHandler.complete_url(
                query,
                prefer_https=prefs.get('prefer_https', True),
                enable_shortcuts=prefs.get('enable_shortcuts', True),
                search_engine=prefs.get('search_engine', 'Google')
            )
            
            results = []
            
            # 1. Primary Result
            results.append(ExtensionResultItem(
                icon=ICON,
                name=self._format_url_display(primary_url),
                description=self._get_description(primary_url, engine_display),
                on_enter=ExtensionCustomAction({"url": primary_url}, keep_app_open=False),
                on_alt_enter=CopyToClipboardAction(primary_url)
            ))
            
            # 2. Generate Alternatives
            alternatives = self._get_alternatives(query, primary_url, prefs)
            
            for alt_url, alt_desc in alternatives:
                results.append(ExtensionResultItem(
                    icon=ICON,
                    name=self._format_url_display(alt_url),
                    description=alt_desc,
                    on_enter=ExtensionCustomAction({"url": alt_url}, keep_app_open=False),
                    on_alt_enter=CopyToClipboardAction(alt_url)
                ))
            
            # FIX: Ensure limit is always an integer
            try:
                limit = int(prefs.get('max_suggestions', 5))
            except (ValueError, TypeError):
                limit = 5
            
            return RenderResultListAction(results[:limit])

        except Exception as e:
            logger.error(f"CRITICAL ERROR: {e}", exc_info=True)
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=ICON,
                    name="Extension Error",
                    description=f"Error: {str(e)[:50]}...",
                    on_enter=ExtensionCustomAction({"url": "about:blank"}, keep_app_open=False)
                )
            ])

    def _get_description(self, url: str, search_engine: str) -> str:
        if url.startswith('mailto:'): return "Send email"
        if url.startswith('file://'): return "Open local file"
        if 'search?q=' in url or '/?q=' in url or 'search/?text=' in url: 
            return f"Search on {search_engine}"
        if 'localhost' in url or '127.0.0.1' in url: return "Open local server"
        return "Open website (Alt+Enter to copy)"

    def _format_url_display(self, url: str) -> str:
        if len(url) > 65:
            return url[:62] + "..."
        return url

    def _get_alternatives(self, query: str, primary_url: str, prefs: dict) -> List[Tuple[str, str]]:
        alts = []
        engine_key = str(prefs.get('search_engine', 'Google')).lower().strip()
        engine_display = prefs.get('search_engine', 'Google')
        
        if engine_key not in URLHandler.SEARCH_ENGINES: 
            engine_key = 'google'
        
        # If primary IS NOT a search, offer search
        is_search = 'search?q=' in primary_url or '/?q=' in primary_url or 'search/?text=' in primary_url
        if not is_search:
            search_url = URLHandler.SEARCH_ENGINES[engine_key].format(quote(query))
            alts.append((search_url, f"🔍 Search on {engine_display}"))
        
        # If query looks like a plain word, suggest TLDs
        if re.match(r'^[\w-]+$', query) and len(query) > 1:
            protocol = 'https' if prefs.get('prefer_https', True) else 'http'
            
            # Suggest .net/.org if primary ended up being .com
            if primary_url.endswith('.com'):
                alts.append((f"{protocol}://{query}.net", "Try .net domain"))
                alts.append((f"{protocol}://{query}.org", "Try .org domain"))
                alts.append((f"{protocol}://{query}.io", "Try .io domain"))
            
            # Suggest www. prefix
            if not primary_url.startswith('file') and 'www.' not in primary_url:
                alts.append((f"{protocol}://www.{query}.com", "Try www. prefix"))

        # Protocol toggle (useful for devs)
        if primary_url.startswith('http://') and 'localhost' not in primary_url:
             alts.append((primary_url.replace('http://', 'https://'), "🔒 Force HTTPS"))
        elif primary_url.startswith('https://'):
             alts.append((primary_url.replace('https://', 'http://'), "🔓 Force HTTP"))

        return alts


class ItemEnterEventListener(EventListener):
    """Event listener for handling URL opening"""
    
    def on_event(self, event: ItemEnterEvent, extension: SmartBrowserExtension):
        try:
            data = event.get_data()
            url = data.get("url")
            if url:
                webbrowser.open(url)
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            
if __name__ == '__main__':
    SmartBrowserExtension().run()
