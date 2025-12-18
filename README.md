
---

```markdown
# 🤖 Financial Assistant - AI-Powered Stock Analysis

Un assistant financier intelligent utilisant l'IA pour fournir des analyses boursières **en temps réel** sans hallucinations.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Caractéristiques

- 📊 **Données en temps réel** via yfinance API  
- 🔍 **Recherche web intelligente** avec DuckDuckGo  
- 🚫 **Zéro hallucination** grâce à l'architecture Tool-First  
- 🌍 **Multilingue** (français/anglais)  
- ⚡ **Cache intelligent** (Redis + in-memory fallback)  
- 💬 **Interface conversationnelle** avec mémoire  
- 🎯 **Données vérifiées** : prix, ratios, recommandations analystes  

## 🏗️ Architecture

```

┌─────────────────────────────────────────────────────┐
│           Tool-First Architecture                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Query → Extract Ticker → Call APIs → Format Data  │
│             ↓                 ↓                     │
│        SimpleFinancialAgent   WebSearchTools        │
│             ↓                 ↓                     │
│          yfinance API    DuckDuckGo API            │
│                        ↓                            │
│              MultiAgentOrchestrator                 │
│                        ↓                            │
│            LLM Synthesis (Mixtral-8x7B)            │
│                  (optional formatting)              │
└─────────────────────────────────────────────────────┘

````

### Composants Principaux

- **SimpleFinancialAgent** : Appelle yfinance directement (pas de ReAct)  
- **MultiAgentOrchestrator** : Route les requêtes et orchestre les agents  
- **FinancialTools** : Wrapper pour yfinance (prix, fondamentaux, news)  
- **WebSearchTools** : Recherches DuckDuckGo (actualités récentes)  

## 📦 Installation

### Prérequis
- Python 3.13+  
- UV (gestionnaire de dépendances)  
- Compte HuggingFace (pour l'API)  

### Étapes

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/finance.git
cd finance
````

2. **Installer UV** (si nécessaire)

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Créer l'environnement**

```bash
uv sync
```

4. **Configurer les variables d'environnement**

Créer un fichier `.env` :

```env
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxx
REDIS_HOST=localhost
REDIS_PORT=6379
PRIMARY_MODEL=mistralai/Mistral-7B-Instruct-v0.3
FALLBACK_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
CACHE_TTL=3600
NEWS_CACHE_TTL=300
```

## 🚀 Utilisation

### Mode Interactif

```bash
uv run main.py
```

Exemple :

```
💬 You: What is the current stock price of NVIDIA?

📊 Stock Data for NVDA
- Current Price: $180.93 USD
- Volume: 181,596,600
- Market Cap: $4,405,102,903,296
- P/E Ratio: 44.89
- Target Range: $140.0 - $352.0
```

### Mode CLI

```bash
uv run main.py "Analyse AAPL avec fondamentaux"
```

### Exemples de Questions

**Données financières**

```
- What is the current stock price of Tesla?
- Analyse financière de Microsoft avec les ratios
- Recommandations des analystes pour NVIDIA
```

**Actualités**

```
- Quelles sont les dernières news sur Apple?
- What's happening with AMD stock today?
```

**Analyses complètes**

```
- Donne-moi une analyse complète de NVDA
- Compare AAPL fundamentals with the market
```

## 📚 API Programmatique

```python
import asyncio
from agents.orchestrator import MultiAgentOrchestrator

async def main():
    orchestrator = MultiAgentOrchestrator()
    response = await orchestrator.query("What is NVIDIA stock price?")
    print(response)
    orchestrator.clear_memory()

asyncio.run(main())
```

## 🔧 Configuration Avancée

### Redis (Optionnel)

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Modèles LLM

```env
PRIMARY_MODEL=mistralai/Mistral-7B-Instruct-v0.3
FALLBACK_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

## 🏛️ Structure du Projet

```
FINANCE/
├── agents/
│   ├── base_agent.py
│   ├── simple_financial_agent.py
│   ├── financial_agent.py
│   ├── web_agent.py
│   └── orchestrator.py
├── tools/
│   ├── financial_tools.py
│   └── web_search_tools.py
├── config/
│   └── settings.py
├── memory/
│   └── memory_manager.py
├── cache/
│   └── cache_manager.py
├── main.py
├── test.py
└── .env
```

## 🐛 Dépannage

### `HUGGINGFACEHUB_API_TOKEN not found`

```bash
echo "HUGGINGFACEHUB_API_TOKEN=hf_xxx" >> .env
```

### `Redis not available`

Le système utilise automatiquement un cache in-memory.

Activer Redis :

```bash
docker run -d -p 6379:6379 redis:alpine
```

## 📊 Données Disponibles

### Bourse (yfinance)

* Prix temps réel
* Ratios financiers
* Recommandations analystes
* Targets de prix
* Marges, volumes, capitalisation

### Actualités (DuckDuckGo)

* Sources fiables
* Résumé + lien vers l’article

## 🚧 Limitations Connues

* Pas de graphiques historiques
* Pas de comparaisons multi-actions
* Pas d’alertes temps réel
* HuggingFace parfois lent

## 🗺️ Roadmap

* [ ] Tests automatisés
* [ ] API REST
* [ ] Dashboard Streamlit
* [ ] Graphiques historiques
* [ ] Support crypto
* [ ] Alertes email/SMS

## 🙏 Remerciements

* yfinance
* DuckDuckGo
* LangChain
* HuggingFace

## 📧 Contact

[ismaillamrani2003@gmail.com](mailto:ismaillamrani2003@gmail.com)

---

**⚠️ Disclaimer** : Cet outil est à usage éducatif uniquement. Ne constitue pas un conseil financier.

```

---


```

