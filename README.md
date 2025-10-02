# Xu AI News RAG System

A comprehensive AI-powered news retrieval and generation system using Retrieval-Augmented Generation (RAG) technology. This system combines intelligent document management, AI-assisted search, and automated news collection to provide a powerful knowledge base solution.

## 🌟 Overview

The Xu AI News RAG System is a full-stack application that enables users to build, manage, and query a personalized knowledge base from various news sources. The system leverages large language models (LLMs) to provide intelligent responses based on retrieved documents, with fallback to online search when necessary.

## 🏗️ Architecture

The system consists of two main components:

### Backend (Flask)
- **RESTful API**: Provides endpoints for authentication, document management, RSS sources, and AI assistant
- **AI Integration**: Uses LangChain with local LLM models (via Ollama) for intelligent responses
- **Vector Database**: FAISS for efficient document retrieval and similarity search
- **Document Processing**: Text splitting, embedding, and clustering capabilities
- **Authentication**: JWT-based user authentication system

### Frontend (React)
- **Modern UI**: React-based interface with TypeScript and Tailwind CSS
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Mock Data System**: Complete mock API for frontend development without backend dependency
- **Interactive Dashboards**: Data visualization with Recharts
- **Modular Architecture**: Clean separation of concerns with organized API modules

## 🚀 Features

### Knowledge Management
- Browse, search, and manage documents in your knowledge base
- Filter documents by type, source, and date range
- Pagination with customizable page sizes
- Batch operations for document management

### AI Assistant
- Intelligent question-answering with source citations
- Conversation history tracking
- Toggle between knowledge base and online search
- Context-aware responses using RAG technology

### RSS Feed Management
- Configure and manage RSS news sources
- Automatic content collection at configurable intervals
- Monitor collection status and error handling
- Support for multiple RSS sources

### Document Upload
- Upload various document types to expand your knowledge base
- Support for Excel files with batch document creation
- Progress tracking for uploads
- Document metadata configuration

### Analytics Dashboard
- Visual dashboard with charts and statistics
- Document trends and usage metrics
- System performance indicators
- Interactive data visualization

### User Authentication
- Secure login and user management
- JWT-based authentication
- User profile management
- Role-based access control

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask
- **Database**: SQLite with SQLModel
- **AI Models**: Ollama with qwen2.5:3b
- **Vector Database**: FAISS
- **Embedding Models**: sentence-transformers
- **Authentication**: JWT tokens
- **Online Search**: Tavily API

### Frontend
- **Framework**: React 18.2.0 with TypeScript
- **Build Tool**: Vite 5.0.0
- **Routing**: React Router DOM 6.20.1
- **HTTP Client**: Axios 1.6.2
- **UI Components**: Custom components with Tailwind CSS
- **Icons**: Lucide React 0.294.0
- **Charts**: Recharts 2.8.0
- **Development**: ESLint, TypeScript

## 📋 Prerequisites

### System Requirements
- Node.js (>= 16.0.0)
- Python 3.8+
- Ollama (for running local LLM models)

### API Keys
- Tavily API key for online search functionality

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd xu-ai-news-rag
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
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

4. Start Ollama and pull the required model:
   ```bash
   ollama pull qwen2.5:3b
   ```

5. Initialize the database:
   ```bash
   python -c "from sqlmodel import SQLModel, create_engine; from models.user import User; from models.rss_source import RssSource; from models.document import Document; from models.analysis import Analysis; engine = create_engine('sqlite:///./data/app.db'); SQLModel.metadata.create_all(engine)"
   ```

6. Run the backend:
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`.

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.development` file:
   ```env
   # Mock mode toggle (set to false to use real backend)
   VITE_USE_MOCK=false
   
   # API base URL
   VITE_API_BASE_URL=http://localhost:5000/api
   
   # App configuration
   VITE_APP_TITLE=Xu AI News RAG System
   VITE_APP_VERSION=1.0.0
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`.

## 📁 Project Structure

```
xu-ai-news-rag/
├── backend/                 # Backend Flask application
│   ├── apis/               # API endpoints
│   │   ├── assistant.py    # AI assistant endpoints
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── document.py     # Document management endpoints
│   │   └── rss.py          # RSS source endpoints
│   ├── models/             # Database models
│   │   ├── analysis.py     # Analysis data models
│   │   ├── document.py     # Document data models
│   │   ├── enums/          # Enumeration definitions
│   │   ├── rss_source.py   # RSS source data models
│   │   └── user.py         # User data models
│   ├── utils/              # Utility functions
│   │   ├── init_sqlite.py  # Database initialization
│   │   ├── jwt_utils.py    # JWT utility functions
│   │   └── logging_config.py # Logging configuration
│   ├── app.py              # Flask application entry point
│   ├── assistant.py        # AI assistant implementation
│   ├── fetch_document.py   # Document fetching utilities
│   ├── generate_test_excel.py # Test data generation
│   ├── requirements.txt    # Python dependencies
│   └── tools.py            # Additional tools and utilities
├── frontend/               # Frontend React application
│   ├── src/
│   │   ├── api/            # API modules and request handling
│   │   ├── components/     # Reusable UI components
│   │   ├── contexts/       # React contexts
│   │   ├── mock/           # Mock data and API simulation
│   │   ├── pages/          # Page components
│   │   ├── types/          # TypeScript type definitions
│   │   ├── App.css         # Global styles
│   │   ├── App.tsx         # Main app component
│   │   ├── index.css       # Base styles
│   │   └── main.tsx        # App entry point
│   ├── .env.development    # Development environment variables
│   ├── package.json        # Node.js dependencies
│   ├── tsconfig.json       # TypeScript configuration
│   └── vite.config.ts      # Vite configuration
└── prototype/              # Prototype implementations
    ├── backend-prototype/  # Backend prototype
    └── frontend-prototype/ # Frontend prototype
```

## 🔧 Configuration

### Backend Configuration

The backend is configured through environment variables in the `.env` file:

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

### Frontend Configuration

The frontend is configured through environment variables in the `.env.development` file:

```env
# Mock mode toggle (set to true to enable mock data)
VITE_USE_MOCK=true

# API base URL (not used in mock mode)
VITE_API_BASE_URL=http://localhost:5000/api

# App configuration
VITE_APP_TITLE=Xu AI News RAG System
VITE_APP_VERSION=1.0.0
```

## 📊 API Endpoints

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

## 🧪 Development with Mock Data

The frontend includes a comprehensive mock data system that allows development without a running backend:

### Enable Mock Mode

Set `VITE_USE_MOCK=true` in the frontend `.env.development` file.

### Test Credentials

- Email: `admin@example.com`
- Password: `admin123`

### Mock Features

- **Authentication**: Complete login, registration, and profile management
- **Document Management**: Document listing, upload, deletion, and filtering
- **AI Search**: Semantic search and AI-powered Q&A with mock responses
- **RSS Management**: RSS source management and feed collection simulation
- **Analytics**: Statistics overview and trend analysis with mock data

## 🔄 Switching Between Mock and Real Backend

To switch from mock data to the real backend:

1. Set `VITE_USE_MOCK=false` in the frontend `.env.development` file
2. Ensure the backend is running (see Backend Setup above)
3. Restart the frontend development server

## 🐛 Troubleshooting

### Backend Issues

- **Database Errors**: Ensure the database is properly initialized
- **Model Loading**: Verify Ollama is running and the required model is pulled
- **API Errors**: Check the backend logs for detailed error messages

### Frontend Issues

- **Mock Data Not Working**: Ensure `VITE_USE_MOCK=true` in the environment variables
- **API Connection Errors**: Verify the backend is running and accessible
- **Build Errors**: Check TypeScript configurations and dependencies

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- LangChain for the AI framework
- Ollama for local LLM hosting
- FAISS for efficient vector similarity search
- React and Vite for the modern frontend framework
- Flask for the backend API framework