# AI News RAG Backend

This is the backend component of the AI News RAG (Retrieval-Augmented Generation) system, which provides intelligent news search and question-answering capabilities with comprehensive testing and logging.

## Overview

The backend is built with Flask and provides a RESTful API for managing news sources, documents, and AI-powered search functionality. It integrates with local language models (via Ollama) and online search APIs to provide intelligent responses based on retrieved news articles.

## Features

- **Unified Source Management**: Support for RSS feeds and web scraping with automatic scheduling
- **Document Management**: Store, retrieve, and analyze news documents with Excel import support
- **AI Assistant**: Intelligent question-answering with source citations and detailed logging
- **Knowledge Base**: FAISS vector database for efficient document retrieval with reranking
- **Online Search**: Fallback to Tavily API when information is not available in the knowledge base
- **Cluster Analysis**: Automatic categorization and analysis of document collections using advanced ML algorithms
- **User Authentication**: JWT-based authentication system
- **Comprehensive Testing**: Unit tests, integration tests, and API tests with 34% code coverage
- **Detailed Logging**: Transparent search process logging with emoji indicators
- **Web Scraping**: Advanced web content extraction with Playwright
- **Email Notifications**: Automated email alerts for new content and errors

## Architecture

The backend follows a modular architecture with the following main components:

- **API Layer**: Flask Blueprints for different functionalities (auth, source, document, assistant, scheduler, analytics)
- **Data Models**: SQLModel for database entities (User, Document, Source, Analysis)
- **AI Components**: LangChain integration for LLM orchestration and tool use with Ollama
- **Vector Database**: FAISS for efficient similarity search with reranking support
- **Document Processing**: Text splitting, embedding, and clustering capabilities with UMAP and HDBSCAN
- **Scheduler**: Background data collection with configurable intervals
- **Repository Pattern**: Data access layer with base repository and specialized repositories
- **Service Layer**: Business logic separation with dedicated services
- **Schema Validation**: Pydantic schemas for request/response validation
- **Testing Framework**: Comprehensive test suite with pytest, coverage reporting, and CI/CD support

## API Endpoints

### Authentication (`/api/auth`)
- `POST /login` - User login
- `POST /register` - User registration
- `POST /refresh` - Refresh access token
- `POST /logout` - User logout
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### Data Sources (`/api/sources`)
- `GET /` - Get all data sources (RSS and Web)
- `GET /<id>` - Get specific data source
- `POST /` - Create new data source
- `PUT /<id>` - Update data source
- `DELETE /<id>` - Delete data source
- `POST /<id>/collect` - Trigger data collection
- `GET /stats` - Get source statistics
- `GET /due-for-sync` - Get sources due for sync

### Scheduler (`/api/scheduler`)
- `GET /status` - Get scheduler status
- `POST /start` - Start data collection scheduler
- `POST /stop` - Stop data collection scheduler
- `POST /fetch` - Trigger immediate data collection

### Documents (`/api/documents`)
- `GET /` - Get all documents
- `GET /page` - Get paginated documents with filtering
- `GET /<id>` - Get specific document
- `GET /get_documents_by_source_id/<source_id>` - Get documents by source
- `POST /upload_excel` - Upload documents from Excel file

### Analytics (`/api/analytics`)
- `GET /stats` - Get analytics statistics
- `GET /cluster_analysis` - Perform cluster analysis on documents
- `GET /cluster_analysis/latest` - Get latest cluster analysis results
- `POST /cluster_analysis` - Trigger new cluster analysis

### Assistant (`/api/assistant`)
- `POST /query` - Submit query to AI assistant
- `GET /health` - Check assistant service health

## Setup and Installation

### Prerequisites

- Python 3.11+
- Ollama (for running local LLM models)
- SQLite database (automatically created)
- Conda environment (recommended: `news-rag11`)

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_PATH=./data/ai_news_rag.db

# AI Models
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RERANK_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2

# Vector Database
FAISS_INDEX_PATH=./data/index.faiss

# Online Search
TAVILY_API_KEY=your_tavily_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=5001
APP_DEBUG=true
AUTO_START_SCHEDULER=true

# Email Notifications
NOTIFICATION_EMAILS=your_email@example.com,another@example.com

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=xlsx,xls,pdf,txt

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Installation

1. Create and activate conda environment:
```bash
conda create -n news-rag11 python=3.11
conda activate news-rag11
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Ollama and pull the required model:
```bash
ollama pull qwen2.5:3b
```

4. Initialize the database (automatically created on first run):
```bash
python app.py
```

5. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5001`.

## Usage

### Adding RSS Sources

To add a new RSS source:

```bash
curl -X POST http://localhost:5001/api/rss/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example News",
    "url": "https://example.com/rss",
    "interval": "ONE_DAY"
  }'
```

### Querying the AI Assistant

To submit a query to the AI assistant:

```bash
curl -X POST http://localhost:5001/api/assistant/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "What are the latest developments in AI?"
  }'
```

### Performing Cluster Analysis

To analyze document clusters:

```bash
curl -X GET http://localhost:5001/api/documents/cluster_analysis \
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

The project includes a comprehensive test suite with unit tests, integration tests, and API tests.

### Running Tests

Run all tests:
```bash
python tests/run_tests.py
```

Run specific test types:
```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration

# API tests only
python tests/run_tests.py --type api
```

Run with coverage:
```bash
python tests/run_tests.py --coverage
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **API Tests**: Test REST API endpoints
- **Coverage**: 34% code coverage with detailed reporting

### Test Features

- Comprehensive mocking for external dependencies
- Database isolation for each test
- Detailed logging and error reporting
- CI/CD ready with GitHub Actions

## Logging and Monitoring

The system includes comprehensive logging with emoji indicators for easy debugging:

- 🔍 **Search Process**: Detailed logging of knowledge base and online search
- 📊 **Performance Metrics**: Search timing and result counts
- 🤖 **AI Decisions**: LLM reasoning and tool selection
- ⚠️ **Error Handling**: Clear error messages and stack traces
- 📋 **API Requests**: Request/response logging for debugging

## Development

### Project Structure

```
backend/
├── apis/                    # API blueprints
│   ├── assistant.py        # AI assistant endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── document.py        # Document management
│   ├── rss.py             # RSS source management
│   └── scheduler.py       # Scheduler control
├── models/                 # Data models
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── api/               # API tests
├── utils/                  # Utility functions
├── data/                   # Database and vector store
├── tools.py               # AI tools and knowledge base
├── assistant.py           # Main assistant logic
└── app.py                 # Flask application
```

### Key Technologies

- **Flask**: Web framework
- **SQLModel**: ORM and data validation
- **LangChain**: LLM orchestration
- **FAISS**: Vector similarity search
- **Ollama**: Local LLM hosting
- **Tavily**: Online search API
- **pytest**: Testing framework
- **UMAP/HDBSCAN**: Advanced clustering
