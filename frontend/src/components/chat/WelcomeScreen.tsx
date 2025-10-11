import React from 'react'
import { Bot } from 'lucide-react'

interface WelcomeScreenProps {
    onExampleClick: (query: string) => void
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onExampleClick }) => {
    const exampleQuestions = [
        "What are the applications of artificial intelligence in healthcare?",
        "What is the difference between deep learning and machine learning?",
        "Development history of GPT models"
    ]

    return (
        <div className="welcome-message">
            <Bot size={48} />
            <h3>Hello! I'm an AI Assistant</h3>
            <p>I can help you answer questions and analyze information. Please enter your question.</p>

            <div className="example-questions">
                <h4>Example Questions:</h4>
                <div className="examples">
                    {exampleQuestions.map((question, index) => (
                        <button
                            key={index}
                            onClick={() => onExampleClick(question)}
                            className="example-btn"
                        >
                            {question}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default WelcomeScreen
