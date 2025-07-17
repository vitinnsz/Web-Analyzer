# display.py
"""
This module handles all data display in the terminal.
It uses the `rich` library to create styled panels, tables, and text, 
presenting the analysis results in a clear and organized way.
"""
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.theme import Theme
from collections import defaultdict

# --- Console Initialization ---
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "green",
})
console = Console(theme=custom_theme)

def display_error(title, message):
    """Displays a critical error panel."""
    console.print(Panel(message, title=title, border_style="danger"))

def display_general_info(data, optimization_score, STRINGS):
    """
    Displays the general information and performance panel.
    
    Args:
        data (dict): A dictionary containing general page and performance data.
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []
    
    render_list.append(Text.from_markup(f"{STRINGS['final_url_analyzed']} {data['final_url']}"))
    ip_text = data['ip_address'] if data['ip_address'] else STRINGS["could_not_resolve_ip"]
    render_list.append(Text.from_markup(f"{STRINGS['ip_address']} {ip_text}"))
    render_list.append(Text.from_markup(f"{STRINGS['status_code']} [success]{data['status_code']}[/success]"))
    
    if data['latency'] is not None:
        ping_color = "success" if data['latency'] < 100 else "warning"
        render_list.append(Text.from_markup(f"{STRINGS['network_latency']} [{ping_color}]{data['latency']:.2f} ms[/{ping_color}]"))
    else:
        render_list.append(Text.from_markup(f"{STRINGS['network_latency']} {STRINGS['not_measured_icmp']}"))

    total_time = data['total_time']
    time_color = "success" if total_time <= 3 else "warning"
    time_warning = "" if total_time <= 3 else STRINGS['slow_warning_3s']
    if total_time > 3: optimization_score['performance'] -= 10
    else: optimization_score['performance'] += 10
    render_list.append(Text.from_markup(f"{STRINGS['total_load_time']} [{time_color}]{total_time:.2f} {STRINGS['seconds']}{time_warning}[/{time_color}]"))

    ttfb = data['ttfb']
    ttfb_color = "success" if ttfb <= 0.8 else "warning"
    ttfb_warning = "" if ttfb <= 0.8 else STRINGS['slow_warning_0.8s']
    if ttfb > 0.8: optimization_score['performance'] -= 10
    else: optimization_score['performance'] += 10
    render_list.append(Text.from_markup(f"{STRINGS['ttfb']} [{ttfb_color}]{ttfb:.2f} {STRINGS['seconds']}{ttfb_warning}[/{ttfb_color}]"))

    render_list.append(Text.from_markup(f"{STRINGS['page_size']} {data['page_size_kb']:.2f} KB"))
    render_list.append(Text.from_markup(f"{STRINGS['server']} {data.get('server', STRINGS['not_provided'])}"))

    compression = data.get('compression', STRINGS['none'])
    compression_color = "success" if compression != STRINGS['none'] else "warning"
    if compression != STRINGS['none']: optimization_score['performance'] += 5
    render_list.append(Text.from_markup(f"{STRINGS['compression']} [{compression_color}]{compression}[/{compression_color}]"))

    console.print(Panel(Group(*render_list), title=STRINGS["panel_general_info"], border_style="blue"))


def display_onpage_security(is_https, headers_data, optimization_score, STRINGS):
    """
    Displays the on-page security analysis panel.
    
    Args:
        is_https (bool): True if the page uses HTTPS.
        headers_data (tuple): A tuple with counts of found and total security headers.
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []
    https_status = STRINGS["https_yes"] if is_https else STRINGS["https_no"]
    if is_https: optimization_score['security'] += 20
    render_list.append(Text.from_markup(f"{STRINGS['using_https']} {https_status}"))
    
    render_list.append(Text.from_markup(STRINGS["security_headers"]))
    found_count, total_count = headers_data
    render_list.append(Text.from_markup(STRINGS["headers_found"].format(count=found_count, total=total_count)))
    optimization_score['security'] += found_count * 2

    console.print(Panel(Group(*render_list), title=STRINGS["panel_onpage_security"], border_style="blue"))


def display_domain_and_ssl(domain_data, ssl_data, STRINGS):
    """
    Displays the domain and SSL analysis panel.
    
    Args:
        domain_data (dict): A dictionary with WHOIS information.
        ssl_data (dict): A dictionary with SSL certificate information.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []
    if domain_data['error']:
        render_list.append(Text.from_markup(STRINGS["whois_error"]))
    else:
        if domain_data['creation_date']:
            render_list.append(Text.from_markup(f"{STRINGS['domain_creation_date']} {domain_data['creation_date'].strftime('%d/%m/%Y')}"))
        if domain_data['registrar']:
            render_list.append(Text.from_markup(f"{STRINGS['registrar']} {domain_data['registrar']}"))
    
    render_list.append(Rule())

    if ssl_data['error']:
        render_list.append(Text.from_markup(STRINGS["ssl_error"]))
    else:
        days_left = ssl_data['days_left']
        validity_color = "success" if days_left > 30 else "warning" if days_left > 7 else "danger"
        warning_msg = "" if days_left > 30 else STRINGS["ssl_expiry_warning"].format(days_left=days_left)
        render_list.append(Text.from_markup(f"{STRINGS['ssl_validity']} [{validity_color}]OK{warning_msg}[/{validity_color}]"))

    console.print(Panel(Group(*render_list), title=STRINGS["panel_domain_ssl"], border_style="blue"))


def display_seo_and_content(seo_data, optimization_score, STRINGS):
    """
    Displays the SEO and content panel.
    
    Args:
        seo_data (dict): A dictionary with basic SEO and content structure data.
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []

    if seo_data['title']:
        render_list.append(Text.from_markup(f"{STRINGS['title']} {seo_data['title']}"))
        optimization_score['seo'] += 5
    else:
        render_list.append(Text.from_markup(f"{STRINGS['title']} {STRINGS['not_found']}"))

    if seo_data['lang']:
        render_list.append(Text.from_markup(f"{STRINGS['declared_language']} {seo_data['lang']}"))
        optimization_score['accessibility'] += 2
    else:
        render_list.append(Text.from_markup(f"{STRINGS['declared_language']} {STRINGS['lang_not_declared']}"))

    render_list.append(Rule("Meta Tags"))
    if seo_data['meta_description']:
        render_list.append(Text.from_markup(f"    - [bold]description[/bold]: {seo_data['meta_description'][:100]}"))
        optimization_score['seo'] += 5
    else:
        render_list.append(Text.from_markup(STRINGS["meta_desc_missing"]))
    
    if seo_data['meta_viewport']:
        render_list.append(Text.from_markup(f"    - [bold]viewport[/bold]: {seo_data['meta_viewport'].get('content', 'N/A')[:100]}"))
        optimization_score['accessibility'] += 10
    else:
        render_list.append(Text.from_markup(STRINGS["meta_viewport_missing"]))

    render_list.append(Rule(STRINGS["headings_structure"]))
    h1_count = seo_data['headings']['h1']
    if h1_count == 1:
        render_list.append(Text.from_markup(STRINGS["h1_ideal"]))
        optimization_score['seo'] += 10
    else:
        render_list.append(Text.from_markup(STRINGS["h1_warning"].format(count=h1_count)))
        if h1_count > 1: optimization_score['seo'] -= 5
    
    for i in range(2, 7):
        h_tag = f'h{i}'
        count = seo_data['headings'][h_tag]
        if count > 0:
            render_list.append(Text.from_markup(STRINGS["heading_found"].format(tag=h_tag, count=count)))

    console.print(Panel(Group(*render_list), title=STRINGS["panel_seo_content"], border_style="blue"))

def display_advanced_seo(adv_seo_data, optimization_score, STRINGS):
    """
    Displays the advanced and social SEO panel.
    
    Args:
        adv_seo_data (dict): A dictionary with advanced SEO data (canonical, OG tags, etc.).
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []

    if adv_seo_data['canonical_url']:
        render_list.append(Text.from_markup(f"{STRINGS['canonical_url']} {adv_seo_data['canonical_url']}"))
        optimization_score['seo'] += 5
    else:
        render_list.append(Text.from_markup(STRINGS['canonical_not_found']))
    
    render_list.append(Rule("Open Graph (Facebook, LinkedIn)"))
    if adv_seo_data['og_tags']:
        for prop, content in adv_seo_data['og_tags'].items():
            render_list.append(Text.from_markup(f"    - [bold]{prop}[/bold]: {content[:100]}"))
        optimization_score['seo'] += 5
    else:
        render_list.append(Text.from_markup(STRINGS['og_tags_missing']))
        
    render_list.append(Rule("Twitter Cards"))
    if adv_seo_data['twitter_tags']:
        for name, content in adv_seo_data['twitter_tags'].items():
            render_list.append(Text.from_markup(f"    - [bold]{name}[/bold]: {content[:100]}"))
        optimization_score['seo'] += 2
    else:
        render_list.append(Text.from_markup(STRINGS['twitter_tags_missing']))

    console.print(Panel(Group(*render_list), title=STRINGS["panel_advanced_seo"], border_style="blue"))

def display_accessibility(a11y_data, optimization_score, STRINGS):
    """
    Displays the accessibility (A11Y) analysis panel.
    
    Args:
        a11y_data (dict): A dictionary with accessibility check results.
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []
    
    if a11y_data['total_images'] > 0:
        images_without_alt = a11y_data['images_without_alt']
        alt_color = "danger" if images_without_alt > 0 else "success"
        render_list.append(Text.from_markup(f"{STRINGS['images_no_alt']} [{alt_color}]{images_without_alt} {STRINGS['images_of']} {a11y_data['total_images']}[/]"))
        if images_without_alt > 0:
            render_list.append(Text.from_markup(STRINGS['alt_text_needed'].format(count=images_without_alt)))
            optimization_score['accessibility'] -= min(10, images_without_alt * 2)
    else:
        render_list.append(Text.from_markup(STRINGS['no_img_tags']))

    links_without_text = a11y_data['links_without_text']
    if links_without_text > 0:
        render_list.append(Text.from_markup(f"{STRINGS['links_no_text']} [danger]{STRINGS['links_found'].format(count=links_without_text)}[/danger]"))
        render_list.append(Text.from_markup(STRINGS['link_text_clarity']))
        optimization_score['accessibility'] -= min(5, links_without_text)

    if render_list:
        console.print(Panel(Group(*render_list), title=STRINGS["panel_accessibility"], border_style="blue"))


def display_resources(resources_data, STRINGS):
    """
    Displays the page resources panel.
    
    Args:
        resources_data (dict): A dictionary with counts of page resources (CSS, JS, images).
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = [
        Text.from_markup(f"{STRINGS['images_label']} {resources_data['images']}"),
        Text.from_markup(f"{STRINGS['css_label']} {resources_data['css_external']} {STRINGS['external']}, {resources_data['css_internal']} {STRINGS['internal']}"),
        Text.from_markup(f"{STRINGS['js_label']} {resources_data['js_external']} {STRINGS['external']}, {resources_data['js_internal']} {STRINGS['internal']}"),
    ]
    console.print(Panel(Group(*render_list), title=STRINGS["panel_resources"], border_style="blue"))


def display_link_analysis(links_data, broken_links_result, STRINGS):
    """
    Displays the link analysis panel and the results of the broken link check.
    
    Args:
        links_data (dict): A dictionary with link statistics.
        broken_links_result (list or None): A list of broken links found, or None if not checked.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = [
        Text.from_markup(f"{STRINGS['total_links']} {links_data['total']}"),
        Text.from_markup(f"{STRINGS['internal_links']} {links_data['internal']}"),
        Text.from_markup(f"{STRINGS['external_links']} {links_data['external']}"),
        Text.from_markup(f"{STRINGS['nofollow_links']} {links_data['nofollow']}"),
    ]
    console.print(Panel(Group(*render_list), title=STRINGS["panel_link_analysis"], border_style="blue"))

    if broken_links_result is None:
        return

    if broken_links_result:
        for link in broken_links_result:
            if link['error']:
                console.print(f"{STRINGS['check_failed']} [link={link['url']}]{link['url']}[/link]")
            else:
                console.print(f"{STRINGS['broken_link'].format(code=link['status'])} [link={link['url']}]{link['url']}[/link]")
        console.print(STRINGS['broken_summary'].format(count=len(broken_links_result)))
    else:
        sample_size = len(links_data['internal_list'])
        console.print(STRINGS['no_broken_links'].format(count=sample_size))


def display_technologies(tech_list, STRINGS):
    """
    Displays the detected technologies panel.
    
    Args:
        tech_list (list): A list of detected technology names.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    if tech_list:
        render_list = [Text.from_markup(f"    - {tech}") for tech in tech_list]
        console.print(Panel(Group(*render_list), title=STRINGS["panel_tech"], border_style="blue"))


def display_common_files(files_data, optimization_score, STRINGS):
    """
    Displays the robots.txt and sitemap.xml analysis panel.
    
    Args:
        files_data (dict): A dictionary with the status of robots.txt and sitemap.xml.
        optimization_score (dict): The dictionary holding the analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    render_list = []
    
    # Robots
    if files_data['robots']['status'] == 'found':
        render_list.append(Text.from_markup(STRINGS['robots_found']))
        optimization_score['seo'] += 2
    elif files_data['robots']['status'] == 'not_found':
        render_list.append(Text.from_markup(STRINGS['robots_not_found'].format(code=files_data['robots']['code'])))
    else:
        render_list.append(Text.from_markup(STRINGS['robots_failed']))
        
    # Sitemap
    if files_data['sitemap']['status'] == 'found':
        render_list.append(Text.from_markup(STRINGS['sitemap_found']))
        optimization_score['seo'] += 2
        if 'url_count' in files_data['sitemap']:
            render_list.append(Text.from_markup(f"{STRINGS['sitemap_urls_found']} {files_data['sitemap']['url_count']}"))
        elif 'parse_error' in files_data['sitemap']:
            render_list.append(Text.from_markup(STRINGS['sitemap_parse_error']))
    elif files_data['sitemap']['status'] == 'not_found':
        render_list.append(Text.from_markup(STRINGS['sitemap_not_found'].format(code=files_data['sitemap']['code'])))
    else:
        render_list.append(Text.from_markup(STRINGS['sitemap_failed']))

    console.print(Panel(Group(*render_list), title=STRINGS["panel_common_files"], border_style="blue"))


def display_final_result(optimization_score, STRINGS):
    """
    Displays the final optimization score.
    
    Args:
        optimization_score (dict): The dictionary holding the final analysis scores.
        STRINGS (dict): A dictionary with the UI text strings.
    """
    score_performance = min(30, max(0, optimization_score['performance']))
    score_security = min(30, max(0, optimization_score['security']))
    score_seo = min(30, max(0, optimization_score['seo']))
    score_accessibility = min(10, max(0, optimization_score['accessibility']))
    score_total = score_performance + score_security + score_seo + score_accessibility

    table = Table(title=STRINGS["summary_title"], show_header=True, header_style="bold magenta")
    table.add_column(STRINGS["col_category"], style="info")
    table.add_column(STRINGS["col_score"], justify="right", style="bold")
    table.add_column(STRINGS["col_max"], justify="right")

    table.add_row(STRINGS["cat_perf"], f"[{'success' if score_performance > 20 else 'warning' if score_performance > 10 else 'danger'}]{score_performance}[/]", "30")
    table.add_row(STRINGS["cat_sec"], f"[{'success' if score_security > 20 else 'warning' if score_security > 10 else 'danger'}]{score_security}[/]", "30")
    table.add_row(STRINGS["cat_seo"], f"[{'success' if score_seo > 20 else 'warning' if score_seo > 10 else 'danger'}]{score_seo}[/]", "30")
    table.add_row(STRINGS["cat_a11y"], f"[{'success' if score_accessibility > 7 else 'warning' if score_accessibility > 4 else 'danger'}]{score_accessibility}[/]", "10")
    console.print(table)

    if score_total >= 90: classification = STRINGS["class_excellent"]
    elif score_total >= 70: classification = STRINGS["class_good"]
    elif score_total >= 40: classification = STRINGS["class_needs_improvement"]
    else: classification = STRINGS["class_not_optimized"]
    color = "success" if score_total >= 70 else "warning" if score_total >= 40 else "danger"

    final_text = STRINGS["final_score"].format(score=score_total, classification=classification)
    console.print(Panel(Text(final_text, justify="center", style=f"bold {color}"), title=STRINGS["panel_final_result"], border_style=color))