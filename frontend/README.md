# Xu AI News RAG Frontend

A modern React-based frontend application for an AI-powered news retrieval and generation system using Retrieval-Augmented Generation (RAG) technology.

## 🌟 Features

- **Knowledge Management**: Browse, search, and manage documents in your knowledge base
- **AI Assistant**: Interact with an AI assistant for intelligent question answering
- **RSS Feed Management**: Configure and manage RSS news sources for automatic content collection
- **Document Upload**: Upload various document types to expand your knowledge base
- **Analytics Dashboard**: Visualize data trends and system statistics
- **User Authentication**: Secure login and user management
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## 🛠️ Tech Stack

- **Framework**: React 18.2.0 with TypeScript
- **Build Tool**: Vite 5.0.0
- **Routing**: React Router DOM 6.20.1
- **HTTP Client**: Axios 1.6.2
- **UI Components**: Custom components with Tailwind CSS
- **Icons**: Lucide React 0.294.0
- **Charts**: Recharts 2.8.0
- **Development**: ESLint, TypeScript

## 🚀 Quick Start

### Prerequisites

- Node.js (>= 16.0.0)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd xu-ai-news-rag/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
src/
├── api/                 # API modules and request handling
│   ├── endpoints.ts     # API endpoint definitions
│   ├── index.ts         # API exports
│   ├── modules/         # API modules by feature
│   └── request.ts       # Request configuration
├── components/          # Reusable UI components
│   ├── Layout.tsx       # Main layout component
│   └── ProtectedRoute.tsx # Route protection wrapper
├── contexts/            # React contexts
│   ├── AuthContext.tsx  # Authentication context
│   └── ThemeContext.tsx # Theme context
├── mock/                # Mock data and API simulation
│   └── server.js        # Mock server implementation
├── pages/               # Page components
│   ├── AnalyticsPage.tsx # Analytics dashboard
│   ├── AssistantPage.tsx # AI assistant interface
│   ├── KnowledgePage.tsx # Knowledge management
│   ├── LoginPage.tsx    # User authentication
│   ├── RssPage.tsx      # RSS feed management
│   └── UploadPage.tsx   # Document upload
├── types/               # TypeScript type definitions
│   ├── analytics.ts     # Analytics-related types
│   ├── api.ts           # API response types
│   ├── common.ts        # Common types
│   ├── components.ts    # Component prop types
│   ├── document.ts      # Document-related types
│   ├── index.ts         # Type exports
│   └── rss.ts           # RSS-related types
├── App.css              # Global styles
├── App.tsx              # Main app component
├── index.css            # Base styles
└── main.tsx             # App entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env.development` file in the project root:

```env
# Mock mode toggle (set to true to enable mock data)
VITE_USE_MOCK=true

# API base URL (not used in mock mode)
VITE_API_BASE_URL=http://localhost:3001/api

# App configuration
VITE_APP_TITLE=Xu AI News RAG System
VITE_APP_VERSION=1.0.0
```

### Mock Data

The application includes a comprehensive mock data system for development without a backend:

- **Authentication**: Login, registration, logout functionality
- **Document Management**: Document listing, upload, deletion
- **AI Search**: Semantic search and AI-powered Q&A
- **RSS Management**: RSS source management and web crawling
- **Analytics**: Statistics overview and trend analysis

## 📱 Pages Overview

### Knowledge Page
- Browse and search through documents in your knowledge base
- Filter documents by type, source, and date range
- Pagination with customizable page sizes
- Batch operations for document management

### Assistant Page
- Interact with the AI assistant
- Ask questions and get intelligent responses
- View conversation history
- Toggle knowledge base and online search options

### RSS Page
- Manage RSS news sources
- Add, edit, and delete RSS feeds
- Configure update intervals
- Monitor collection status

### Upload Page
- Upload documents to expand your knowledge base
- Support for various file formats
- Progress tracking for uploads
- Document metadata configuration

### Analytics Page
- Visual dashboard with charts and statistics
- Document trends and usage metrics
- System performance indicators
- Interactive data visualization

### Login Page
- User authentication interface
- Secure login with JWT tokens
- Password recovery functionality

## 🔄 API Integration

The application uses a modular API structure:

```typescript
// Import API modules
import { authAPI, documentAPI, rssAPI, assistantAPI } from './api';

// Example usage
const login = async (email, password) => {
  try {
    const response = await authAPI.login(email, password);
    // Handle successful login
  } catch (error) {
    // Handle error
  }
};
```

## 🧪 Testing with Mock Data

To run the application with mock data:

1. Ensure `VITE_USE_MOCK=true` in your `.env.development` file
2. Start the development server with `npm run dev`
3. Use the following test credentials:
   - Email: `admin@example.com`
   - Password: `admin123`

## 🎨 Styling

The application uses a custom design system with:
- CSS variables for theming
- Responsive layout with mobile-first approach
- Consistent spacing and typography
- Dark/light theme support (via ThemeContext)

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Environment-Specific Builds

Create environment-specific `.env` files:

- `.env.production` for production builds
- `.env.staging` for staging builds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

For support and questions:
- Check the existing documentation
- Review the mock data implementation in `src/mock/server.js`
- Examine the API modules in `src/api/modules/`

---

**Happy coding!** 🎉