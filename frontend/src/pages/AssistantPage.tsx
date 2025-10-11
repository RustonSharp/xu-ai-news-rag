import React from 'react'
import ChatContainer from '../components/chat/ChatContainer'
import { useChat } from '../hooks/useChat'

const AssistantPage: React.FC = () => {
  const {
    messages,
    loading,
    sendMessage,
    clearChat,
    handleExampleClick
  } = useChat()

  return (
    <div className="assistant-page">
      <div className="page-header">
        <h1>AI Assistant</h1>
        <p>Ask me anything about the knowledge base or get help with your questions.</p>
      </div>

      <div className="assistant-container">
        <ChatContainer
          messages={messages}
          loading={loading}
          onSendMessage={sendMessage}
          onClearChat={clearChat}
          onExampleClick={handleExampleClick}
        />
      </div>
    </div>
  )
}

export default AssistantPage