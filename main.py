from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
import webbrowser
import os
import re
import logging
from urllib.parse import urlparse, quote
import socket
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLHandler:
    """Enhanced URL handling with intelligent completion and validation"""
    
    # Common domain shortcuts
    DOMAIN_SHORTCUTS = {
        'gh': 'github.com',
        'github': 'github.com',
        'google': 'google.com',
        'gmail': 'gmail.com',
        'yt': 'youtube.com',
        'youtube': 'youtube.com',
        'so': 'stackoverflow.com',
        'stackoverflow': 'stackoverflow.com',
        'reddit': 'reddit.com',
        'twitter': 'twitter.com',
        'x': 'x.com',
        'facebook': 'facebook.com',
        'fb': 'facebook.com',
        'linkedin': 'linkedin.com',
        'instagram': 'instagram.com',
        'ig': 'instagram.com',
        'wiki': 'wikipedia.org',
        'wikipedia': 'wikipedia.org',
        'docs': 'docs.google.com',
        'drive': 'drive.google.com',
        'maps': 'maps.google.com',
        'translate': 'translate.google.com'
    }
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Validate domain format"""
        if not domain or len(domain) > 253:
            return False
        
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(domain_pattern, domain) is not None
    
    @staticmethod
    def is_local_network_ip(ip: str) -> bool:
        """Check if IP is in local network ranges"""
        local_ranges = ['192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', 
                       '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                       '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.']
        return ip == '127.0.0.1' or any(ip.startswith(prefix) for prefix in local_ranges)
    
    @staticmethod
    def is_development_port(port: int) -> bool:
        """Check if port is commonly used for development"""
        dev_ports = {3000, 3001, 4200, 5000, 5173, 8000, 8080, 8888, 9000, 9001}
        return port in dev_ports
    
    @classmethod
    def complete_url(cls, query: str, prefer_https: bool = True, enable_shortcuts: bool = True) -> str:
        """Enhanced URL completion with intelligent handling"""
        if not query or not query.strip():
            return "https://google.com"
        
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
            except Exception as e:
                logger.error(f"Error processing file path: {e}")
                return f"https://google.com/search?q={quote(query)}"
        
        # IPv4 address handling
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        if re.match(ipv4_pattern, query):
            ip_parts = query.split(':')
            ip = ip_parts[0]
            port = int(ip_parts[1]) if len(ip_parts) > 1 else 80
            
            # Validate IP octets
            try:
                octets = [int(octet) for octet in ip.split('.')]
                if all(0 <= octet <= 255 for octet in octets):
                    protocol = 'http' if cls.is_local_network_ip(ip) or cls.is_development_port(port) else 'https'
                    return f'{protocol}://{query}'
            except ValueError:
                pass
            
            return f"https://google.com/search?q={quote(query)}"
        
        # Localhost variants
        if query.startswith('localhost') or re.match(r'^localhost:\d+', query):
            return f'http://{query}'
        
        # Development ports on any host
        if ':' in query:
            try:
                host, port_str = query.rsplit(':', 1)
                port = int(port_str)
                if cls.is_development_port(port):
                    return f'http://{query}'
            except ValueError:
                pass
        
        # Email address
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, query):
            return f'mailto:{query}'
        
        # Domain shortcuts
        if enable_shortcuts:
            query_lower = query.lower()
            if query_lower in cls.DOMAIN_SHORTCUTS:
                return f'https://{cls.DOMAIN_SHORTCUTS[query_lower]}'
        
        # Single word without dots - try common extensions
        if re.match(r'^[\w-]+$', query) and len(query) > 1:
            protocol = 'https' if prefer_https else 'http'
            return f'{protocol}://{query}.com'
        
        # Valid domain structure
        if '.' in query and cls.is_valid_domain(query):
            protocol = 'https' if prefer_https else 'http'
            return f'{protocol}://{query}'
        
        # Multi-word or complex queries - search
        if ' ' in query or len(query) < 2 or not re.match(r'^[\w.-]+$', query):
            return f"https://google.com/search?q={quote(query)}"
        
        # Default: try as domain
        protocol = 'https' if prefer_https else 'http'
        return f'{protocol}://{query}'


class SmartBrowserExtension(Extension):
    """Smart Ulauncher extension for intelligent URL opening"""
    
    def __init__(self):
        super(SmartBrowserExtension, self).__init__()
        self.preferences = {
            'enable_shortcuts': True,
            'prefer_https': True,
            'max_suggestions': 5
        }
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        logger.info("SmartBrowserExtension initialized with default preferences")


class PreferencesEventListener(EventListener):
    """Initialize preferences on start"""
    
    def on_event(self, event: PreferencesEvent, extension: SmartBrowserExtension):
        extension.preferences = {
            'enable_shortcuts': event.preferences.get('enable_shortcuts', 'true') == 'true',
            'prefer_https': event.preferences.get('prefer_https', 'true') == 'true',
            'max_suggestions': int(event.preferences.get('max_suggestions', '5'))
        }
        logger.info(f"Preferences loaded: {extension.preferences}")


class PreferencesUpdateEventListener(EventListener):
    """Update preferences when changed"""
    
    def on_event(self, event: PreferencesUpdateEvent, extension: SmartBrowserExtension):
        if event.id == 'enable_shortcuts':
            extension.preferences['enable_shortcuts'] = event.new_value == 'true'
        elif event.id == 'prefer_https':
            extension.preferences['prefer_https'] = event.new_value == 'true'
        elif event.id == 'max_suggestions':
            extension.preferences['max_suggestions'] = int(event.new_value)
        logger.info(f"Updated preference {event.id} to {event.new_value}")


class KeywordQueryEventListener(EventListener):
    """Event listener with smart URL suggestions"""
    
    def on_event(self, event: KeywordQueryEvent, extension: SmartBrowserExtension):
        try:
            query = event.get_argument() or ""
            prefs = extension.preferences
            
            if not query.strip():
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name="Smart URL Opener",
                        description="Type a URL, domain, search term, or use shortcuts (gh, yt, etc.)",
                        on_enter=ExtensionCustomAction(
                            {"url": "https://google.com"}, 
                            keep_app_open=False
                        )
                    )
                ])
            
            primary_url = URLHandler.complete_url(
                query,
                prefer_https=prefs['prefer_https'],
                enable_shortcuts=prefs['enable_shortcuts']
            )
            results = []
            
            # Primary suggestion with smart description
            description = self._get_primary_description(query, primary_url)
            results.append(ExtensionResultItem(
                icon='images/icon.png',
                name=self._format_url_display(primary_url),
                description=description,
                on_enter=ExtensionCustomAction(
                    {"url": primary_url}, 
                    keep_app_open=False
                )
            ))
            
            # Alternative suggestions
            alternatives = self._get_alternatives(
                query, 
                primary_url, 
                prefs['prefer_https'],
                prefs['enable_shortcuts']
            )
            for alt_url, alt_description in alternatives:
                results.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=self._format_url_display(alt_url),
                    description=alt_description,
                    on_enter=ExtensionCustomAction(
                        {"url": alt_url}, 
                        keep_app_open=False
                    )
                ))
            
            # Apply max suggestions preference
            max_results = min(prefs['max_suggestions'], 7)  # Cap at 7 for safety
            return RenderResultListAction(results[:max_results])
            
        except Exception as e:
            logger.error(f"Error in KeywordQueryEventListener: {e}")
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name="Error occurred",
                    description="Failed to process query. Opening Google as fallback.",
                    on_enter=ExtensionCustomAction(
                        {"url": "https://google.com"}, 
                        keep_app_open=False
                    )
                )
            ])
    
    def _get_primary_description(self, query: str, url: str) -> str:
        """Generate description for primary suggestion"""
        if url.startswith('mailto:'):
            return "Open in email client"
        elif url.startswith('file://'):
            return "Open local file"
        elif 'google.com/search' in url:
            return "Search on Google"
        elif url.startswith('http://localhost') or 'http://127.0.0.1' in url:
            return "Open local development server"
        elif any(port in url for port in [':3000', ':8000', ':8080']):
            return "Open development server"
        else:
            return "Open website"
    
    def _format_url_display(self, url: str) -> str:
        """Format URL for display"""
        if len(url) > 60:
            parsed = urlparse(url)
            if parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}/..."
            return url[:57] + "..."
        return url
    
    def _get_alternatives(
        self, 
        query: str, 
        primary_url: str,
        prefer_https: bool,
        enable_shortcuts: bool
    ) -> List[Tuple[str, str]]:
        """Generate smart alternative suggestions"""
        alternatives = []
        
        # Always offer search if primary isn't already a search
        if 'google.com/search' not in primary_url:
            search_url = f"https://google.com/search?q={quote(query)}"
            alternatives.append((search_url, "Search on Google"))
        
        # Domain alternatives for single words
        if re.match(r'^[\w-]+$', query) and len(query) > 1:
            query_lower = query.lower()
            
            # If not already using a shortcut, suggest alternatives
            if not (enable_shortcuts and query_lower in URLHandler.DOMAIN_SHORTCUTS):
                protocol = 'https' if prefer_https else 'http'
                
                if not primary_url.endswith('.org'):
                    alternatives.append((f"{protocol}://{query}.org", "Try .org domain"))
                if not primary_url.endswith('.net'):
                    alternatives.append((f"{protocol}://{query}.net", "Try .net domain"))
                if not primary_url.endswith('.io'):
                    alternatives.append((f"{protocol}://{query}.io", "Try .io domain"))
        
        # HTTPS upgrade for HTTP URLs (but not HTTP to HTTPS downgrade)
        if prefer_https and primary_url.startswith('http://') and not any(local in primary_url for local in ['localhost', '127.0.0.1', '192.168.']):
            https_version = primary_url.replace('http://', 'https://', 1)
            alternatives.append((https_version, "Try HTTPS version"))
        
        # Special shortcuts suggestions
        if enable_shortcuts and len(query) > 2 and not query.lower() in URLHandler.DOMAIN_SHORTCUTS:
            matching_shortcuts = [k for k in URLHandler.DOMAIN_SHORTCUTS.keys() 
                                 if k.startswith(query.lower()) or query.lower() in k]
            for shortcut in matching_shortcuts[:2]:
                shortcut_url = f"https://{URLHandler.DOMAIN_SHORTCUTS[shortcut]}"
                if shortcut_url != primary_url:
                    alternatives.append((shortcut_url, f"Shortcut: {shortcut} → {URLHandler.DOMAIN_SHORTCUTS[shortcut]}"))
        
        return alternatives[:3]  # Limit alternatives


class ItemEnterEventListener(EventListener):
    """Event listener for handling URL opening"""
    
    def on_event(self, event: ItemEnterEvent, extension: SmartBrowserExtension):
        try:
            data = event.get_data()
            url = data.get("url")
            
            if not url:
                logger.error("No URL provided in event data")
                return RenderResultListAction([])
            
            logger.info(f"Opening URL: {url}")
            
            # Additional validation before opening
            try:
                parsed = urlparse(url)
                if not parsed.scheme and not url.startswith(('file://', 'mailto:')):
                    url = f"https://{url}"
                
                webbrowser.open(url)
                logger.info(f"Successfully opened: {url}")
                
            except Exception as browser_error:
                logger.error(f"Failed to open URL {url}: {browser_error}")
                # Fallback: search query
                fallback_url = f"https://google.com/search?q={quote(str(url))}"
                webbrowser.open(fallback_url)
                logger.info(f"Opened fallback search: {fallback_url}")
            
            return RenderResultListAction([])
            
        except Exception as e:
            logger.error(f"Error in ItemEnterEventListener: {e}")
            return RenderResultListAction([])


if __name__ == '__main__':
    try:
        extension = SmartBrowserExtension()
        extension.run()
    except Exception as e:
        logger.error(f"Failed to start extension: {e}")
        raise
