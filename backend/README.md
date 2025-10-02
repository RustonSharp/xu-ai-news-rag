# AI News RAG Backend

This is the backend component of the AI News RAG (Retrieval-Augmented Generation) system, which provides intelligent news search and question-answering capabilities.

## Overview

The backend is built with Flask and provides a RESTful API for managing news sources, documents, and AI-powered search functionality. It integrates with large language models (LLMs) to provide intelligent responses based on retrieved news articles.

## Features

- **RSS Source Management**: Add, update, delete, and monitor RSS news sources
- **Document Management**: Store, retrieve, and analyze news documents
- **AI Assistant**: Intelligent question-answering with source citations
- **Knowledge Base**: Vector database for efficient document retrieval
- **Online Search**: Fallback to web search when information is not available in the knowledge base
- **Cluster Analysis**: Automatic categorization and analysis of document collections
- **User Authentication**: JWT-based authentication system

## Architecture

The backend follows a modular architecture with the following main components:

- **API Layer**: Flask Blueprints for different functionalities (auth, rss, document, assistant)
- **Data Models**: SQLModel for database entities (User, Document, RSS Source, Analysis)
- **AI Components**: LangChain integration for LLM orchestration and tool usage
- **Vector Database**: FAISS for efficient similarity search
- **Document Processing**: Text splitting, embedding, and clustering capabilities

## API Endpoints

### Authentication (`/api/auth`)
- `POST /login` - User login
- `POST /register` - User registration
- `POST /refresh` - Refresh access token
- `POST /logout` - User logout
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### RSS Sources (`/api/rss`)
- `GET /sources` - Get all RSS sources
- `GET /sources/<id>` - Get specific RSS source
- `POST /sources` - Create new RSS source
- `PUT /sources/<id>` - Update RSS source
- `DELETE /sources/<id>` - Delete RSS source
- `GET /feeds/<id>` - Get RSS feeds
- `POST /feeds/<id>` - Trigger RSS collection

### Documents (`/api/documents`)
- `GET /` - Get all documents
- `GET /page` - Get paginated documents with filtering
- `GET /<id>` - Get specific document
- `GET /get_documents_by_source_id/<source_id>` - Get documents by RSS source
- `GET /cluster_analysis` - Perform cluster analysis on documents
- `GET /cluster_analysis/latest` - Get latest cluster analysis results
- `POST /upload_excel` - Upload documents from Excel file

### Assistant (`/api/assistant`)
- `POST /query` - Submit query to AI assistant
- `GET /health` - Check assistant service health

## Setup and Installation

### Prerequisites

- Python 3.8+
- Ollama (for running local LLM models)
- SQLite database (automatically created)

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_PATH=./data/app.db

# AI Models
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
RERANK_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2

# Vector Database
FAISS_INDEX_PATH=./data/vectorstore_faiss/index.faiss

# Online Search
TAVILY_API_KEY=your_tavily_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Ollama and pull the required model:
```bash
ollama pull qwen2.5:3b
```

3. Initialize the database:
```bash
python -c "from sqlmodel import SQLModel, create_engine; from models.user import User; from models.rss_source import RssSource; from models.document import Document; from models.analysis import Analysis; engine = create_engine('sqlite:///./data/app.db'); SQLModel.metadata.create_all(engine)"
```

4. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## Usage

### Adding RSS Sources

To add a new RSS source:

```bash
curl -X POST http://localhost:5000/api/rss/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example News",
    "url": "https://example.com/rss",
    "interval": "HOUR"
  }'
```

### Querying the AI Assistant

To submit a query to the AI assistant:

```bash
curl -X POST http://localhost:5000/api/assistant/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "What are the latest developments in AI?"
  }'
```

### Performing Cluster Analysis

To analyze document clusters:

```bash
curl -X GET http://localhost:5000/api/documents/cluster_analysis \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## AI Components

### Knowledge Base

The system uses a FAISS vector database to store document embeddings for efficient retrieval. Documents are processed using text splitting and embedding models to create searchable vector representations.

### Online Search

When the knowledge base doesn't contain relevant information, the system falls back to online search using the Tavily API to provide up-to-date information.

### Assistant

The AI assistant is built using LangChain and integrates with local LLM models (via Ollama). It uses a combination of retrieval-augmented generation and tool use to provide accurate, sourced responses.

## Testing

Run the test suite:

```bash
python -m pytest tests/
```