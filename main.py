
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
import webbrowser
import os
import re
import logging
from urllib.parse import urlparse, quote
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLHandler:
    """Enhanced URL handling with validation and smart completion"""
    
    @staticmethod
    def is_valid_domain(domain):
        """Check if domain is valid"""
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(domain_pattern, domain) is not None
    
    @staticmethod
    def is_reachable_ip(ip, port=80, timeout=1):
        """Quick check if IP is reachable"""
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def complete_url(url):
        """Enhanced URL completion with better validation"""
        if not url or not url.strip():
            return "https://google.com"
        
        url = url.strip()
        
        # Already has protocol
        if re.match(r'^\w+://', url):
            return url
        
        # File path handling with better validation
        if url.startswith(('/', './', '../', '~')):
            try:
                if url.startswith('~'):
                    url = os.path.expanduser(url)
                abs_path = os.path.abspath(url)
                if os.path.exists(abs_path):
                    return f"file://{abs_path}"
                else:
                    logger.warning(f"File path does not exist: {abs_path}")
                    return f"file://{abs_path}"  # Still return it, let browser handle
            except Exception as e:
                logger.error(f"Error processing file path: {e}")
                return f"https://google.com/search?q={quote(url)}"
        
        # IPv4 address with enhanced validation
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        if re.match(ipv4_pattern, url):
            ip_parts = url.split(':')
            ip = ip_parts[0]
            port = int(ip_parts[1]) if len(ip_parts) > 1 else 80
            
            # Validate IP octets
            octets = ip.split('.')
            if all(0 <= int(octet) <= 255 for octet in octets):
                # Use http for local networks, https for others
                if ip.startswith(('192.168.', '10.', '172.')) or ip == '127.0.0.1':
                    return f'http://{url}'
                return f'https://{url}'
            else:
                return f"https://google.com/search?q={quote(url)}"
        
        # Localhost variants
        if url.startswith('localhost') or re.match(r'^localhost:\d+', url):
            return f'http://{url}'
        
        # Handle common development ports
        dev_port_pattern = r'^.+:(3000|3001|4200|5000|8000|8080|8888|9000)$'
        if re.match(dev_port_pattern, url) and not url.startswith('http'):
            return f'http://{url}'
        
        # Email address - open in default email client
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, url):
            return f'mailto:{url}'
        
        # Plain single word - smart completion
        if re.match(r'^[\w-]+$', url):
            common_domains = {
                'github': 'github.com',
                'google': 'google.com',
                'youtube': 'youtube.com',
                'stackoverflow': 'stackoverflow.com',
                'reddit': 'reddit.com',
                'twitter': 'twitter.com',
                'facebook': 'facebook.com',
                'linkedin': 'linkedin.com',
                'instagram': 'instagram.com'
            }
            
            if url.lower() in common_domains:
                return f'https://{common_domains[url.lower()]}'
            
            # Try .com first
            return f'https://{url}.com'
        
        # Contains domain-like structure
        if '.' in url and URLHandler.is_valid_domain(url):
            return f'https://{url}'
        
        # Search query fallback
        if ' ' in url or len(url.split()) > 1:
            return f"https://google.com/search?q={quote(url)}"
        
        # Default: try as HTTPS domain
        return f'https://{url}' if not url.startswith(('http://', 'https://')) else url


class DefaultBrowserExtension(Extension):
    """Enhanced Ulauncher extension for smart URL opening"""
    
    def __init__(self):
        super(DefaultBrowserExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        logger.info("DefaultBrowserExtension initialized")


class KeywordQueryEventListener(EventListener):
    """Enhanced event listener with multiple URL suggestions"""
    
    def on_event(self, event, extension):
        try:
            query = event.get_argument() or ""
            
            if not query.strip():
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name="Enter a URL or search term",
                        description="Type a URL, domain, file path, or search query",
                        on_enter=ExtensionCustomAction(
                            {"url": "https://google.com"}, 
                            keep_app_open=False
                        )
                    )
                ])
            
            primary_url = URLHandler.complete_url(query)
            results = []
            
            # Primary suggestion
            results.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f"Open: {primary_url}",
                description=f"Primary suggestion",
                on_enter=ExtensionCustomAction(
                    {"url": primary_url}, 
                    keep_app_open=False
                )
            ))
            
            # Alternative suggestions
            alternatives = self._get_alternatives(query, primary_url)
            for alt_url, description in alternatives:
                results.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=f"Open: {alt_url}",
                    description=description,
                    on_enter=ExtensionCustomAction(
                        {"url": alt_url}, 
                        keep_app_open=False
                    )
                ))
            
            return RenderResultListAction(results)
            
        except Exception as e:
            logger.error(f"Error in KeywordQueryEventListener: {e}")
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name="Error occurred",
                    description=f"Failed to process query: {str(e)}",
                    on_enter=ExtensionCustomAction(
                        {"url": "https://google.com"}, 
                        keep_app_open=False
                    )
                )
            ])
    
    def _get_alternatives(self, query, primary_url):
        """Generate alternative URL suggestions"""
        alternatives = []
        
        # Search alternative
        if not query.startswith(('http://', 'https://', 'file://', 'mailto:')):
            search_url = f"https://google.com/search?q={quote(query)}"
            if search_url != primary_url:
                alternatives.append((search_url, "Search on Google"))
        
        # Protocol alternatives
        if primary_url.startswith('https://'):
            http_version = primary_url.replace('https://', 'http://', 1)
            alternatives.append((http_version, "Try HTTP instead"))
        elif primary_url.startswith('http://'):
            https_version = primary_url.replace('http://', 'https://', 1)
            alternatives.append((https_version, "Try HTTPS instead"))
        
        # Domain alternatives for single words
        if re.match(r'^[\w-]+$', query) and not query.lower() in ['github', 'google', 'youtube']:
            if not primary_url.endswith('.com'):
                alternatives.append((f"https://{query}.com", "Try .com domain"))
            alternatives.append((f"https://{query}.org", "Try .org domain"))
            alternatives.append((f"https://{query}.net", "Try .net domain"))
        
        return alternatives[:3]  # Limit to 3 alternatives


class ItemEnterEventListener(EventListener):
    """Enhanced event listener with better error handling"""
    
    def on_event(self, event, extension):
        try:
            data = event.get_data()
            url = data.get("url")
            
            if not url:
                logger.error("No URL provided in event data")
                return RenderResultListAction([])
            
            logger.info(f"Opening URL: {url}")
            
            # Validate URL before opening
            try:
                parsed = urlparse(url)
                if not parsed.scheme and not url.startswith('file://'):
                    url = f"https://{url}"
                
                webbrowser.open(url)
                logger.info(f"Successfully opened: {url}")
                
            except Exception as browser_error:
                logger.error(f"Failed to open URL {url}: {browser_error}")
                # Fallback: try to open as search query
                fallback_url = f"https://google.com/search?q={quote(str(url))}"
                webbrowser.open(fallback_url)
                logger.info(f"Opened fallback search: {fallback_url}")
            
            return RenderResultListAction([])
            
        except Exception as e:
            logger.error(f"Error in ItemEnterEventListener: {e}")
            return RenderResultListAction([])


if __name__ == '__main__':
    try:
        extension = DefaultBrowserExtension()
        extension.run()
    except Exception as e:
        logger.error(f"Failed to start extension: {e}")
        raise
