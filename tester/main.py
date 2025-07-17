# main.py
"""
This is the main entry point for the website analysis application.
It orchestrates the entire process, from handling user input and configuration
to calling the analysis functions and displaying the results.
"""

import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict
from rich.panel import Panel
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn

# --- Local Imports ---
from config import Config
from i18n.i18n import get_strings
from display import (
    console, display_error, display_general_info, display_onpage_security,
    display_domain_and_ssl, display_seo_and_content, display_advanced_seo,
    display_accessibility, display_resources, display_link_analysis,
    display_technologies, display_common_files, display_final_result
)
import analysis

def run_analysis(url, check_broken, check_domain, STRINGS):
    """
    The main function that orchestrates the complete website analysis.

    How it works:
    1.  Fetches the initial page data. If it fails, an error is displayed.
    2.  Prepares base data: the final URL (after redirects), hostname, and a BeautifulSoup object.
    3.  Initializes a dictionary to keep track of the optimization score.
    4.  Sequentially executes various analysis functions from the `analysis` module.
    5.  For each analysis result, it calls the corresponding display function from the `display` module.
    6.  Optionally checks for broken links and domain/SSL info based on flags.
    7.  Displays a final, aggregated optimization score.

    Args:
        url (str): The target URL to analyze.
        check_broken (bool): A flag to determine whether to check for broken internal links.
        check_domain (bool): A flag to determine whether to check for WHOIS and SSL information.
        STRINGS (dict): A dictionary containing the internationalized strings for the UI.
    """
    console.print(Rule(STRINGS["start_analysis"].format(url=url), style="blue"))

    # 1. Fetch page data
    response, total_time, error = analysis.fetch_page_data(url)
    if not response:
        display_error(STRINGS["connection_error_title"], STRINGS["critical_error_accessing_url"].format(e=error))
        return

    # 2. Prepare base data
    final_url = response.url
    hostname = urlparse(final_url).hostname
    soup = BeautifulSoup(response.content, "html.parser")
    optimization_score = defaultdict(int, {'performance': 0, 'security': 0, 'seo': 0, 'accessibility': 27})

    # 3. Run analyses and display results panel by panel
    general_data = {
        'final_url': final_url,
        'ip_address': analysis.get_ip_address(hostname),
        'status_code': response.status_code,
        'latency': analysis.get_ping_latency(hostname),
        'total_time': total_time,
        'ttfb': response.elapsed.total_seconds(),
        'page_size_kb': len(response.content) / 1024,
        'server': response.headers.get('Server'),
        'compression': response.headers.get('Content-Encoding')
    }
    display_general_info(general_data, optimization_score, STRINGS)

    techs = analysis.detect_technologies(soup, response.text, response.headers, final_url)
    display_technologies(techs, STRINGS)

    headers_data = analysis.analyze_security_headers(response.headers)
    display_onpage_security(final_url.startswith('https://'), headers_data, optimization_score, STRINGS)
    
    if check_domain:
        domain_data, ssl_data = analysis.analyze_domain_and_ssl(hostname)
        display_domain_and_ssl(domain_data, ssl_data, STRINGS)

    seo_data = analysis.analyze_seo_structure(soup)
    display_seo_and_content(seo_data, optimization_score, STRINGS)

    adv_seo_data = analysis.analyze_advanced_seo(soup)
    display_advanced_seo(adv_seo_data, optimization_score, STRINGS)
    
    a11y_data = analysis.analyze_accessibility(soup)
    display_accessibility(a11y_data, optimization_score, STRINGS)

    resources_data = analysis.get_page_resources(soup)
    display_resources(resources_data, STRINGS)
    
    links_data = analysis.get_all_links(final_url, soup)
    broken_links_result = None
    if check_broken and links_data['internal_list']:
        links_to_check = links_data['internal_list'][:Config.LINK_SAMPLE_SIZE]
        console.print(STRINGS['checking_links'].format(count=len(links_to_check), limit=Config.LINK_SAMPLE_SIZE))
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True, console=console) as progress:
            task = progress.add_task(STRINGS['checking_progress'], total=len(links_to_check))
            broken_links_result = analysis.check_broken_links(links_to_check)
    display_link_analysis(links_data, broken_links_result, STRINGS)

    files_data = analysis.analyze_common_files(final_url)
    display_common_files(files_data, optimization_score, STRINGS)
    
    display_final_result(optimization_score, STRINGS)

    console.print(Rule(STRINGS["analysis_complete"], style="blue"))

if __name__ == "__main__":
    """
    This block serves as the application's entry point when the script is executed directly.

    It performs the following steps:
    1. Clears the console screen.
    2. Loads language settings from the config and fetches the UI strings.
    3. Prints the application title banner.
    4. Handles user input: either uses a fixed URL from the config file or prompts the user.
    5. Ensures the URL has a scheme (e.g., https://) before processing.
    6. Calls the main `run_analysis` function with the provided URL and options.
    7. Gracefully handles user interruptions (Ctrl+C) and other unexpected errors.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    
    lang_code = Config.Language
    STRINGS = get_strings(lang_code)

    console.print(Panel(STRINGS["app_title"], style="bold blue", subtitle="by https://victordeveloper.com"))

    try:
        if Config.FIXED_URL:
            url_input = Config.URL
            check_broken_links = Config.BROKEN_LINKS
        else:
            url_input = console.input(STRINGS["prompt_url"])
            check_links_input = console.input(STRINGS["prompt_broken_links"]).strip().upper()
            check_broken_links = (check_links_input in ['Y', 'S', 'YES'])

        if not urlparse(url_input).scheme:
            url_input = "https://" + url_input

        # Call the orchestrator function
        run_analysis(url_input, check_broken_links, Config.CHECK_DOMAIN_INFO, STRINGS)

    except KeyboardInterrupt:
        console.print(f"\n{STRINGS['user_interruption']}")
    except Exception as e:
        console.print_exception(show_locals=True)