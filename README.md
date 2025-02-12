# 🤖 Crypto News Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Models-purple.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent crypto news analysis system powered by RAG (Retrieval Augmented Generation) that automatically scrapes, processes, and analyzes cryptocurrency news to provide real-time insights and answers to your questions! 🚀

<p align="center">
    <img src="https://github.com/user-attachments/assets/06a1f357-7ca5-4a26-9a0a-7ae063465937" alt="demo" width="100%">
</p>

## ✨ Features

- 🔄 **Real-time News Scraping**: Automatically scrapes crypto news from TradingView
- 🧠 **Intelligent Analysis**: Uses advanced RAG architecture to provide context-aware responses
- 💡 **Flexible Model Support**: Works with both OpenAI and local models
- 🔍 **Hybrid Search**: Combines vector and keyword search for better results
- 🎯 **Smart Reranking**: Uses Cohere for intelligent result reranking

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/marsidmali/Crypto-News-Assistant.git
cd Crypto-News-Assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Creat `config.json` (see Configuration example)
   - Add your API keys and configuration

## 🤖 Model Setup

### Using OpenAI
1. Get your API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `config.json`:
```json
{
    "model_type": "openai",
    "openai_api_key": "your-key-here",
    "openai_model": "gpt-4o-mini"
}
```

### Using Ollama (Local Models)
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull your preferred model:
```bash
ollama pull deepseek-r1:32b
```

3. Update your `config.json`:
```json
{
    "model_type": "ollama",
    "ollama_model": "deepseek-r1:32b"
}
```

### Cohere API Setup
1. Create an account at [Cohere](https://cohere.ai/)
2. Get your API key and add it to your `config.json`:
```json
{
    "cohere_api_key": "your-cohere-key-here"
}
```

## 🚀 Usage

1. Start the application:
```bash
streamlit run src/app.py
```

2. Wait for the initial news scraping and indexing
3. Start asking questions about crypto news and trends!

## 🏗️ RAG Architecture

The app uses the following RAG (Retrieval Augmented Generation) architecture:

1. **Data Ingestion**:
   - Scrapes crypto news from TradingView
   - Processes and chunks articles for optimal retrieval

2. **Hybrid Retrieval**:
   - Vector Search (FAISS) with MiniLM embeddings
   - Keyword Search (BM25)
   - Weighted ensemble combination

3. **Smart Reranking**:
   - Cohere Rerank for context-aware result selection
   - Top-N filtering for most relevant context

4. **Response Generation**:
   - Context-aware prompt engineering
   - Flexible model support (OpenAI/Ollama)
   - Streaming response generation

## 📁 Project Structure

```plaintext
crypto-news-assistant/
│
├── src/                 # Source code
│   ├── app.py          # Streamlit application
│   ├── scraper.py      # TradingView scraping logic
│   └── rag.py          # RAG system implementation
│   
├── config.json         # Configuration file
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## ⚙️ Configuration

Example `config.json`:
```json
{
    "model_type": "openai or ollama"
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "ollama_model": "deepseek-r1:32b",
    "cohere_api_key": ""
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
