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
```

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
```

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

Créer un fichier `.env` à la racine :
```env
# HuggingFace API Token (OBLIGATOIRE)
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Redis (OPTIONNEL - utilise in-memory si absent)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Modèles LLM (OPTIONNEL - valeurs par défaut)
PRIMARY_MODEL=mistralai/Mistral-7B-Instruct-v0.3
FALLBACK_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# Cache TTL (OPTIONNEL)
CACHE_TTL=3600
NEWS_CACHE_TTL=300
```

**Obtenir une clé HuggingFace :**
1. Créer un compte sur [huggingface.co](https://huggingface.co)
2. Aller dans Settings → Access Tokens
3. Créer un nouveau token (Read access suffit)

## 🚀 Utilisation

### Mode Interactif

```bash
uv run main.py
```

Ensuite, posez vos questions :
```
💬 You: What is the current stock price of NVIDIA?

📊 Stock Data for NVDA
- Current Price: $180.93 USD
- Volume: 181,596,600
- Market Cap: $4,405,102,903,296
- P/E Ratio: 44.89
- Target Range: $140.0 - $352.0
```

### Mode CLI (requête unique)

```bash
uv run main.py "Analyse AAPL avec fondamentaux"
```

### Exemples de Questions

**Données financières :**
```
- What is the current stock price of Tesla?
- Analyse financière de Microsoft avec les ratios
- Recommandations des analystes pour NVIDIA
```

**Actualités :**
```
- Quelles sont les dernières news sur Apple?
- What's happening with AMD stock today?
- Contexte marché pour les actions tech
```

**Analyses complètes :**
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
    
    # Requête simple
    response = await orchestrator.query(
        "What is NVIDIA stock price?"
    )
    print(response)
    
    # Nettoyer le cache
    orchestrator.clear_memory()

asyncio.run(main())
```

## 🔧 Configuration Avancée

### Redis (Optionnel mais Recommandé)

Pour un cache persistant :

```bash
# Docker
docker run -d -p 6379:6379 redis:alpine

# Ou avec docker-compose
docker-compose up -d redis
```

### Modèles LLM

Modifier dans `.env` :
```env
# Mistral (rapide, bon pour données structurées)
PRIMARY_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# Mixtral (meilleur pour synthèse, mais plus lent)
FALLBACK_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

## 🏛️ Structure du Projet

```
FINANCE/
├── agents/
│   ├── base_agent.py           # Agent ReAct de base (legacy)
│   ├── simple_financial_agent.py  # Tool-First agent (UTILISÉ)
│   ├── financial_agent.py      # Agent financier avec tools
│   ├── web_agent.py            # Agent recherche web
│   └── orchestrator.py         # Orchestrateur principal
├── tools/
│   ├── financial_tools.py      # Wrapper yfinance
│   └── web_search_tools.py     # Wrapper DuckDuckGo
├── config/
│   └── settings.py             # Configuration centralisée
├── memory/
│   └── memory_manager.py       # Gestion mémoire conversationnelle
├── cache/
│   └── cache_manager.py        # Cache Redis/in-memory
├── main.py                     # Point d'entrée CLI
├── test.py                     # Tests de validation
└── .env                        # Variables d'environnement
```

## 🐛 Dépannage

### Problème : `HUGGINGFACEHUB_API_TOKEN not found`

**Solution :**
```bash
# Vérifier que .env existe
ls .env

# Ajouter le token
echo "HUGGINGFACEHUB_API_TOKEN=hf_xxx" >> .env
```

### Problème : `Redis not available`

**Ce n'est pas grave !** Le système utilise un cache in-memory automatiquement.

Pour activer Redis :
```bash
docker run -d -p 6379:6379 redis:alpine
```

### Problème : Réponses lentes (>30s)

**Cause :** HuggingFace Inference API peut être lent aux heures de pointe.

**Solutions :**
1. Utiliser un modèle local (Ollama)
2. Passer à l'API OpenAI/Anthropic
3. Activer le cache Redis pour réutiliser les réponses

### Problème : `StopIteration` dans les logs

**Ce n'est pas bloquant !** Le système utilise un fallback propre qui retourne les données brutes (toujours correctes).

## 📊 Données Disponibles

### Données Boursières (yfinance)
- ✅ Prix en temps réel
- ✅ Volume, capitalisation
- ✅ Ratios financiers (P/E, PEG, Debt/Equity)
- ✅ Marges (profit, opérationnelle)
- ✅ Recommandations analystes
- ✅ Targets de prix (min, max, moyenne)

### Actualités (DuckDuckGo)
- ✅ News récentes (24h-7j)
- ✅ Sources fiables (CNBC, Bloomberg, Reuters...)
- ✅ Citations avec liens

## 🚧 Limitations Connues

- ❌ Pas de graphiques historiques
- ❌ Pas de comparaisons multi-actions
- ❌ Pas d'alertes en temps réel
- ⚠️ Synthèse LLM parfois instable (fallback OK)
- ⚠️ HuggingFace API peut être lent (10-30s)

## 🗺️ Roadmap

- [ ] Tests automatisés (pytest)
- [ ] API REST (FastAPI)
- [ ] Dashboard (Streamlit/Gradio)
- [ ] Graphiques historiques
- [ ] Comparaisons multi-actions
- [ ] Support crypto-monnaies
- [ ] Alertes email/SMS



## 🙏 Remerciements

- [yfinance](https://github.com/ranaroussi/yfinance) pour les données financières
- [LangChain](https://langchain.com/) pour l'orchestration
- [DuckDuckGo](https://duckduckgo.com/) pour les recherches
- [HuggingFace](https://huggingface.co/) pour l'infrastructure LLM

## 📧 Contact

Pour questions ou support : [ismaillamrani2003@gmail.com]

---

**⚠️ Disclaimer** : Cet outil est à usage éducatif uniquement. Ne constitue pas un conseil financier. Toujours faire ses propres recherches avant d'investir.
#   f i n a n c i a l _ a n a l y s t e _ a g e n t _ u s i n g _ l a n g c h a i n -  
 