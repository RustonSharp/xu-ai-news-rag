import React from 'react'

interface SearchResult {
    id: string
    title: string
    content: string
    url: string
    score: number
    type: string
    source: string
    relevance: number
    timestamp: string
}

interface SourcesListProps {
    sources: SearchResult[] | any[]
    isRawAnswer?: boolean
}

const SourcesList: React.FC<SourcesListProps> = ({ sources, isRawAnswer = false }) => {
    if (!sources || sources.length === 0) {
        return null
    }

    // Handle raw answer format
    if (isRawAnswer) {
        return (
            <div className="raw-sources-list">
                {sources.map((source, index) => (
                    <div key={index} className="raw-source-item">
                        <h5>Source {index + 1}:</h5>
                        <div className="raw-source-content">
                            <p><strong>Content:</strong> {source.content || 'No content'}</p>
                            {source.metadata && (
                                <div className="raw-source-meta">
                                    <p><strong>Title:</strong> {source.metadata.title || 'No title'}</p>
                                    <p><strong>Author:</strong> {source.metadata.author || 'Unknown'}</p>
                                    <p><strong>Publish Date:</strong> {source.metadata.pub_date || 'Unknown'}</p>
                                    <p><strong>Tags:</strong> {source.metadata.tags || 'No tags'}</p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        )
    }

    // Handle regular sources format
    return (
        <div className="message-sources">
            <h4>Sources:</h4>
            <div className="sources-list">
                {sources.map((source) => (
                    <div key={source.id} className="source-item">
                        <div className="source-icon">📄</div>
                        <div className="source-info">
                            <h5>{source.title}</h5>
                            <p>{source.content}</p>
                            <div className="source-meta">
                                <span className="relevance">
                                    Relevance: {(source.relevance * 100).toFixed(0)}%
                                </span>
                                {source.url && (
                                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link">
                                        View Source
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default SourcesList
