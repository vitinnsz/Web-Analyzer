# config.py

class Config:
    """
    Classe de configuração para o Website Tester.
    Modifique os valores abaixo para personalizar o comportamento do script conforme necessário.

    Configuration class for Website Tester.
    Modify the values below to customize the script's behavior as needed.
    """

    # Idioma padrão para a interface e mensagens ('en-us' para Inglês ou 'pt-br' para Português).
    # Altere para definir o idioma usado pelo script.
    # -----
    # Default language for the interface and messages ('en-us' for English or 'pt-br' for Portuguese).
    # Change to set the language used by the script.
    Language = "pt-br"

    # Se FIXED_URL for True, o script sempre analisará a URL definida abaixo, sem solicitar ao usuário.
    # Útil para automatizar testes em um site específico.
    # -----
    # If FIXED_URL is True, the script will always analyze the URL defined below, without prompting the user.
    # Useful for automating tests on a specific site.
    FIXED_URL = True

    # URL do site a ser analisado automaticamente se FIXED_URL estiver habilitado.
    # Insira aqui o endereço do site alvo.
    # -----
    # URL of the site to be automatically analyzed if FIXED_URL is enabled.
    # Enter the target site address here.
    URL = "https://www.google.com"

    # Se BROKEN_LINKS for True, o script verificará automaticamente links quebrados no site.
    # Isso pode aumentar o tempo de execução, pois cada link será testado.
    # -----
    # If BROKEN_LINKS is True, the script will automatically check for broken links on the site.
    # This may increase execution time, as each link will be tested.
    BROKEN_LINKS = True

    # Se CHECK_DOMAIN_INFO for True, o script analisará informações do domínio (WHOIS) e certificado SSL.
    # Desabilite para agilizar a análise caso não precise desses dados.
    # -----
    # If CHECK_DOMAIN_INFO is True, the script will analyze domain information (WHOIS) and SSL certificate.
    # Disable to speed up analysis if you don't need this data.
    CHECK_DOMAIN_INFO = True

    # Define o número máximo de links internos a serem verificados durante a análise.
    # Limitar esse valor evita que o script demore muito em sites com muitos links.
    # -----
    # Sets the maximum number of internal links to be checked during analysis.
    # Limiting this value prevents the script from taking too long on sites with many links.
    LINK_SAMPLE_SIZE = 100
