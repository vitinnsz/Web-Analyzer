<div align="center">

# 🚀 Website Tester

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Licença](https://img.shields.io/github/license/vitinnsz/Website-Tester?style=for-the-badge&color=green)](https://github.com/vitinnsz/Website-Tester/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/vitinnsz/Website-Tester?style=for-the-badge&color=orange)](https://github.com/vitinnsz/Website-Tester/issues)
[![Stars](https://img.shields.io/github/stars/vitinnsz/Website-Tester?style=for-the-badge)](https://github.com/vitinnsz/Website-Tester/stargazers)
[![Último Commit](https://img.shields.io/github/last-commit/vitinnsz/Website-Tester?style=for-the-badge&color=blueviolet)](https://github.com/vitinnsz/Website-Tester/commits/main)

**Uma ferramenta CLI poderosa para analisar SEO, Segurança e Performance de qualquer site, com relatórios direto no seu terminal.**

</div>

---

**Website Tester** é uma ferramenta de linha de comando (CLI) desenvolvida em Python que realiza uma análise completa de websites. Ela apresenta relatórios detalhados e coloridos no terminal, utilizando BeautifulSoap, Requests, WHOIS e `rich`.

---

<div align="center">

<img src="./assets/1.png" alt="Exemplo de Relatório" width="49%">
<img src="./assets/2.png" alt="Exemplo de Relatório" width="49%">
*Exemplo de relatório gerado pela ferramenta.*

</div>

---

## 📋 Tabela de Conteúdos

- [✨ Funcionalidades](#-funcionalidades)
- [🚀 Como Usar](#-como-usar)
- [🔧 Configuração](#-configuração)
- [🗺️ Roadmap](#-roadmap)
- [🤝 Como Contribuir](#-como-contribuir)
- [📧 Contato](#-contato)
- [📜 Licença](#-licença)

---

## ✨ Funcionalidades

Obtenha uma análise 360º do seu site, dividida em seções claras:

- 🌐 **Informações Gerais**: IP, latência, TTFB, tamanho da página, servidor e compressão.
- 🛠️ **Tecnologias**: Detecção de frameworks (React, WordPress), servidores, CDNs e mais.
- 🔐 **Segurança**: Análise de HTTPS, cabeçalhos essenciais e validade do certificado SSL.
- 📈 **SEO Básico**: Título, meta-descrição, estrutura de cabeçalhos (H1-H6) e idioma.
- 🚀 **SEO Avançado**: Verificação de tags `canonical`, Open Graph e Twitter Cards.
- ♿ **Acessibilidade (A11y)**: Identificação de imagens sem `alt` e links sem texto descritivo.
- 📦 **Recursos**: Contagem de arquivos CSS, JS e imagens.
- 🔗 **Links**: Análise de links internos, externos, `nofollow` e verificação de links quebrados.
- 📁 **Arquivos Padrão**: Checagem da existência de `robots.txt` e `sitemap.xml`.
- 📊 **Score Final**: Pontuações de 0 a 100 para Performance, Segurança, SEO e Acessibilidade.

---

## 🚀 Como Usar

Primeiro, clone o repositório para sua máquina local:

```bash
git clone https://github.com/vitinnsz/Website-Tester.git
cd Website-Tester
```

O projeto utiliza um arquivo `requirements.txt` para listar todas as dependências Python necessárias. Você pode instalá-las de duas maneiras: usando Docker ou em um ambiente virtual local.

### 🐳 Opção 1: Docker (Recomendado)

A forma mais simples de executar, sem se preocupar com dependências. O Docker utiliza o `requirements.txt` para construir um ambiente isolado com tudo o que a ferramenta precisa.

```bash
docker-compose run --rm website-tester
```
> **Nota**: O comando `docker-compose run` permite a entrada interativa de dados, como a URL do site.

### 🐍 Opção 2: Ambiente Local (Python 3.8+)

Para executar localmente, é recomendado criar um ambiente virtual para isolar as dependências do projeto.

#### Usando `uv` (Rápido e Moderno)
`uv` é um instalador de pacotes e gerenciador de ambientes virtuais extremamente rápido. Se você busca a máxima performance na instalação, esta é a melhor opção.

```bash
# Instale uv se ainda não tiver: pip install uv
uv venv
source .venv/bin/activate # No Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
python main.py
```

#### Usando `venv` + `pip` (Padrão)
Se você não tem `uv` ou prefere a abordagem tradicional do Python, use `venv` para criar o ambiente e `pip` para instalar os pacotes listados no `requirements.txt`.

```bash
python -m venv .venv
# No Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 🔧 Configuração

Você pode personalizar o comportamento da ferramenta editando o arquivo `config.py`:

```python
# config.py
LANGUAGE = "pt-br"        # Idioma dos relatórios
FIXED_URL = True          # Usar uma URL fixa ou perguntar a cada execução
URL = "https://exemplo.com" # URL a ser usada se FIXED_URL for True
BROKEN_LINKS = True       # Ativar verificação de links quebrados
CHECK_DOMAIN_INFO = True  # Ativar consulta de informações do domínio
LINK_SAMPLE_SIZE = 50     # Número de links a serem amostrados para verificação
```

---

## 🗺️ Roadmap

Funcionalidades planejadas para o futuro:

- [ ] **Exportação de Relatórios**: Salvar análises em JSON, CSV, TXT e Markdown.
- [ ] **API REST**: Disponibilizar a ferramenta como um serviço para consumo externo.
- [ ] **Integração CI/CD**: Facilitar o uso em pipelines de automação (ex: GitHub Actions).
- [ ] **Análise de Performance Avançada**: Incluir métricas como Core Web Vitals.
- [ ] **Verificação de Cookies**: Analisar conformidade com LGPD e GDPR.

---

## 🤝 Como Contribuir

Sua contribuição é muito bem-vinda! Siga os passos abaixo:

1.  **Fork** o projeto.
2.  Crie uma nova branch: `git checkout -b feature/sua-feature-incrivel`
3.  Faça o commit de suas mudanças: `git commit -m 'feat: Adiciona uma feature incrível'`
4.  Envie para a sua branch: `git push origin feature/sua-feature-incrivel`
5.  Abra um **Pull Request**.

Para bugs ou sugestões, por favor, [abra uma issue](https://github.com/vitinnsz/Website-Tester/issues).

---

## 📧 Contato

Desenvolvido por **Victor**

[![Website](https://img.shields.io/badge/Website-victordeveloper.com-blue?style=flat&logo=world)](https://victordeveloper.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-victorsdev-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/victorsdev/)

---

## 📜 Licença

Distribuído sob a Licença MIT. Veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.

