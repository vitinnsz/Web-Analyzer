# analysis.py
import time
import socket
import re
import requests
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from datetime import datetime

# --- Additional Tools ---
import whois
import ssl
from ping3 import ping

def fetch_page_data(url):
    """
    Fetches the content of a URL, measures the total load time, and the TTFB (Time To First Byte).

    Args:
        url (str): The URL of the page to be fetched.

    Returns:
        tuple: A tuple containing the response object (requests.Response), the total load time (float), and the TTFB (float) on success. On failure, returns (None, None, Exception) with the captured error.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        end_time = time.time()
        total_time = end_time - start_time
        ttfb = response.elapsed.total_seconds()
        response.raise_for_status()
        return response, total_time, ttfb
    except requests.exceptions.RequestException as e:
        return None, None, e

def get_ip_address(hostname):
    """
    Resolves a hostname to get its IP address.

    Args:
        hostname (str): The hostname (domain) to be resolved. E.g., 'google.com'.

    Returns:
        str: The corresponding IP address as a string, or None if the resolution fails.
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def get_ping_latency(hostname):
    """
    Measures the network latency (ping) to a given host.

    Args:
        hostname (str): The hostname for which the latency will be measured.

    Returns:
        float: The latency time in milliseconds (ms), or None if the ping test fails (e.g., due to ICMP blocking).
    """
    try:
        return ping(hostname, unit='ms')
    except Exception:
        return None

def analyze_security_headers(headers):
    """
    Checks and counts the presence of recommended HTTP security headers.

    Args:
        headers (dict): A dictionary representing the HTTP response headers.

    Returns:
        tuple: A tuple containing two integers: the number of security headers found and the total number of recommended headers checked.
    """
    security_headers = {'Content-Security-Policy', 'Strict-Transport-Security', 'X-Content-Type-Options', 'X-Frame-Options', 'Referrer-Policy'}
    found_headers_count = sum(1 for h in security_headers if h.lower() in {k.lower() for k in headers.keys()})
    return found_headers_count, len(security_headers)

def analyze_domain_and_ssl(hostname):
    """
    Performs analysis of domain information (WHOIS) and the SSL certificate.

    How it works:
    - For the domain, it uses the `whois` library to query the creation date and the registrar.
    - For SSL, it establishes a secure connection on port 443 to get the certificate details,
      calculating the expiration date and the remaining days of validity.

    Args:
        hostname (str): The hostname to be analyzed.

    Returns:
        tuple: A tuple containing two dictionaries: (`domain_info_data`, `ssl_data`). Each dictionary contains the collected information or an 'error' key if the analysis failed.
    """
    domain_info_data = {'creation_date': None, 'registrar': None, 'error': None}
    try:
        domain_info = whois.whois(hostname)
        if domain_info.creation_date:
            domain_info_data['creation_date'] = domain_info.creation_date[0] if isinstance(domain_info.creation_date, list) else domain_info.creation_date
        if domain_info.registrar:
            domain_info_data['registrar'] = domain_info.registrar
    except Exception as e:
        domain_info_data['error'] = str(e)

    ssl_data = {'valid_until': None, 'days_left': None, 'error': None}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                valid_until = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (valid_until - datetime.now()).days
                ssl_data['valid_until'] = valid_until
                ssl_data['days_left'] = days_left
    except Exception as e:
        ssl_data['error'] = str(e)
        
    return domain_info_data, ssl_data

def analyze_seo_structure(soup):
    """
    Extracts basic SEO and page structure information from the HTML.

    How it works:
    Uses BeautifulSoup to find and extract the content of the `<title>` tag, the `lang` attribute of the `<html>` tag,
    the meta description tag, the meta viewport tag, and to count the quantity of each header tag (h1 to h6).

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed page HTML.
    Returns:
        dict: A dictionary with the extracted SEO data (title, language, meta description, viewport, and header count).
    """
    data = {}
    title_tag = soup.find('title')
    data['title'] = title_tag.get_text(strip=True) if title_tag else None
    data['lang'] = soup.find('html').get('lang')
    
    data['meta_description'] = soup.find('meta', attrs={'name': 'description'})
    if data['meta_description']:
        data['meta_description'] = data['meta_description'].get('content')
        
    data['meta_viewport'] = soup.find('meta', attrs={'name': 'viewport'})
    
    data['headings'] = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    
    return data

def analyze_advanced_seo(soup):
    """
    Extracts advanced SEO and social media metadata.

    How it works:
    Searches the HTML for the `link` tag with `rel="canonical"`, and for meta tags that follow the Open Graph (e.g., `og:title`)
    and Twitter Cards (e.g., `twitter:card`) standards.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed page HTML.
    Returns:
        dict: A dictionary containing the canonical URL, and dictionaries for the found Open Graph and Twitter tags.
    """
    data = {}
    canonical_tag = soup.find('link', rel='canonical')
    data['canonical_url'] = canonical_tag['href'] if canonical_tag and canonical_tag.get('href') else None

    data['og_tags'] = {tag['property']: tag['content'] for tag in soup.find_all('meta', property=re.compile(r'^og:'))}
    data['twitter_tags'] = {tag['name']: tag['content'] for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})}
    
    return data

def analyze_accessibility(soup):
    """
    Performs a basic accessibility (A11Y) analysis on the page.

    How it works:
    1.  Counts the total number of images (`<img>`) and how many of them do not have a filled `alt` attribute.
    2.  Counts the number of links (`<a>`) that do not have visible descriptive text.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed page HTML.
    Returns:
        dict: A dictionary with the accessibility analysis data.
    """
    data = {}
    images = soup.find_all('img')
    data['total_images'] = len(images)
    data['images_without_alt'] = sum(1 for img in images if not img.get('alt', '').strip()) if images else 0
    
    links = soup.find_all('a', href=True)
    data['links_without_text'] = sum(1 for a in links if not a.get_text(strip=True) and not a.find('img'))
    
    return data

def get_page_resources(soup):
    """
    Identifies and counts the different types of static resources referenced on the page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed page HTML.

    Returns:
        dict: A dictionary with the count of images, CSS files (external and internal), and JS scripts (external and internal).
    """
    return {
        'images': len(soup.find_all('img')),
        'css_external': len(soup.find_all('link', rel='stylesheet')),
        'css_internal': len(soup.find_all('style')),
        'js_external': len(soup.find_all('script', src=True)),
        'js_internal': len(soup.find_all('script', src=None)),
    }

def get_all_links(base_url, soup):
    """
    Finds, counts, and categorizes all links (`<a>`) on the page.

    How it works:
    Iterates through all `<a>` tags with an `href` attribute. Ignores anchor links, `mailto:`, and `tel:`.
    Classifies links as internal (same domain), external, or `nofollow`. It also collects a unique list of all internal links.

    Args:
        base_url (str): The base URL of the page, used to resolve relative links.
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed page HTML.
    Returns:
        dict: A dictionary containing the total number of links, counts of internal, external, nofollow links, and a list (`internal_list`) of the internal URLs.
    """
    links_data = {'total': 0, 'internal': 0, 'external': 0, 'nofollow': 0, 'internal_list': []}
    base_domain = urlparse(base_url).netloc
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href or href.startswith(('#', 'mailto:', 'tel:')):
            continue
            
        links_data['total'] += 1
        if 'nofollow' in link.get('rel', []):
            links_data['nofollow'] += 1
            
        full_url = urljoin(base_url, href)
        parsed_href = urlparse(full_url)
        
        if parsed_href.netloc == base_domain:
            links_data['internal'] += 1
            links_data['internal_list'].append(full_url)
        elif parsed_href.scheme in ['http', 'https']:
            links_data['external'] += 1
            
    links_data['internal_list'] = sorted(list(set(links_data['internal_list'])))
    return links_data

def check_broken_links(links_to_check):
    """
    Checks a list of URLs to identify broken links.

    How it works:
    For each URL in the list, it sends an HTTP `HEAD` request (which is lighter as it doesn't download the page body).
    If the response status code is 4xx (client error) or 5xx (server error), the link is considered broken.
    If a connection error occurs, the link is also marked as a failure.

    Args:
        links_to_check (list): A list of strings, where each string is a URL to be checked.
    Returns:
        list: A list of dictionaries. Each dictionary represents a broken link and contains the 'url', the 'status' (HTTP code), and a boolean 'error' for connection failures.
    """
    broken_links = []
    for link_url in links_to_check:
        try:
            resp = requests.head(link_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, allow_redirects=True)
            if 400 <= resp.status_code < 600:
                broken_links.append({'url': link_url, 'status': resp.status_code, 'error': False})
        except requests.RequestException:
            broken_links.append({'url': link_url, 'status': None, 'error': True})
    return broken_links

def detect_technologies(soup, page_text, headers, url):
    """
    Attempts to identify the technologies (frameworks, libraries, servers) used on the site.

    How it works:
    Uses a dictionary of rules, where each rule is a lambda function that looks for specific patterns in the HTML content (soup), plain text (page_text), HTTP headers (headers), or the URL itself.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the HTML.
        page_text (str): The text content of the page.
        headers (dict): The HTTP response headers.
        url (str): The final URL of the page.
    Returns:
        list: A sorted list of strings with the names of the detected technologies.
    """
    technologies, rules = set(), {
        'WordPress': (lambda s, t, h, u: '/wp-content/' in t or '/wp-includes/' in t), 'Joomla': (lambda s, t, h, u: 'com_content' in t),
        'Drupal': (lambda s, t, h, u: '/sites/default/' in t), 'Shopify': (lambda s, t, h, u: 'cdn.shopify.com' in t),
        'Wix': (lambda s, t, h, u: 'wix.com' in t or 'wixstatic.com' in t), 'React': (lambda s, t, h, u: s.find('div', id='root') or s.find('div', id='__next')),
        'Vue.js': (lambda s, t, h, u: s.find('div', id='app') or 'data-v-' in t), 'Angular': (lambda s, t, h, u: s.find(lambda tag: tag.has_attr('ng-version'))),
        'jQuery': (lambda s, t, h, u: 'jquery' in t.lower()), 'Bootstrap': (lambda s, t, h, u: 'bootstrap' in t.lower()),
        'Google Analytics': (lambda s, t, h, u: 'google-analytics.com' in t or 'googletagmanager.com' in t), 'Hotjar': (lambda s, t, h, u: 'hotjar.com' in t),
        'Cloudflare': (lambda s, t, h, u: 'cloudflare' in h.get('Server', '').lower()), 'Nginx': (lambda s, t, h, u: 'nginx' in h.get('Server', '').lower()),
        'Apache': (lambda s, t, h, u: 'apache' in h.get('Server', '').lower()), 'PHP': (lambda s, t, h, u: 'php' in h.get('X-Powered-By', '').lower() or '.php' in urlparse(u).path),
    }
    for tech, cond in rules.items():
        if cond(soup, page_text, headers, url):
            technologies.add(tech)
    return sorted(list(technologies))

def analyze_common_files(base_url):
    """
    Checks for the existence and basic content of `robots.txt` and `sitemap.xml` files.

    How it works:
    - It attempts to access `[base_url]/robots.txt`. If found (status 200) and it's not an HTML page, it's considered valid.
    - It attempts to access `[base_url]/sitemap.xml`. If found (status 200) and it's an XML file, it tries to parse the file to count the number of listed URLs.

    Args:
        base_url (str): The base URL of the site.
    Returns:
        dict: A dictionary with the verification status for 'robots' and 'sitemap' ('found', 'not_found', or 'failed') and additional information, such as the number of URLs in the sitemap.
    """
    files_data = {'robots': {'status': 'failed'}, 'sitemap': {'status': 'failed'}}
    
    # Robots.txt
    try:
        resp = requests.get(urljoin(base_url, '/robots.txt'), timeout=5)
        if resp.status_code == 200 and 'html' not in resp.headers.get('Content-Type', ''):
            files_data['robots']['status'] = 'found'
        else:
            files_data['robots']['status'] = 'not_found'
            files_data['robots']['code'] = resp.status_code
    except requests.RequestException:
        pass 

    # Sitemap.xml
    try:
        resp = requests.get(urljoin(base_url, '/sitemap.xml'), timeout=10)
        if resp.status_code == 200 and 'xml' in resp.headers.get('Content-Type', ''):
            files_data['sitemap']['status'] = 'found'
            try:
                root = ET.fromstring(resp.content)
                namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                urls = root.findall('sm:url', namespace)
                files_data['sitemap']['url_count'] = len(urls)
            except ET.ParseError:
                files_data['sitemap']['parse_error'] = True
        else:
            files_data['sitemap']['status'] = 'not_found'
            files_data['sitemap']['code'] = resp.status_code
    except requests.RequestException:
        pass 
        
    return files_data