import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import InputBar from './InputBar';
import '../chatbot.css';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: 'Hi there, ask me anything',
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState('chat');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ✅ Updated to call AWS API Gateway instead of using mock data
  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(
        'https://hmgfjd373a.execute-api.us-east-1.amazonaws.com/chat',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: content }),
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: data.reply || 'Sorry, I didn’t get a response from the AI agent.',
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content:
          'There was a problem connecting to the server. Please try again later.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickStart = (message: string) => {
    handleSendMessage(message);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a PDF or Word document (.pdf, .doc, .docx)');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    setIsUploading(true);
    setUploadedFile(file);

    // Simulate file processing feedback for UX only
    setTimeout(() => {
      const uploadMessage: ChatMessage = {
        id: Date.now().toString(),
        content:
          "I see you've uploaded a resume! I can help you improve it. What specific section would you like me to review?",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, uploadMessage]);
      setIsUploading(false);

      setTimeout(() => {
        setUploadedFile(null);
      }, 3000);
    }, 2000);
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const quickStartOptions = [
    'Resume Advice',
    'Job Search',
    'Course Planning',
    'Interview Prep',
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'contact':
        return (
          <div className="page-content">
            <h2>Contact Us</h2>
            <div className="contact-info">
              <p><strong>Email:</strong> advisor@utdallas.edu</p>
              <p><strong>Phone:</strong> (972) 883-2111</p>
              <p><strong>Office Hours:</strong> Monday-Friday, 9:00 AM - 5:00 PM</p>
              <p><strong>Location:</strong> Student Services Building, Room 1.200</p>
            </div>
            <div className="contact-methods">
              <h3>Get Help</h3>
              <ul>
                <li>Schedule an appointment through MyUTD</li>
                <li>Visit our walk-in hours</li>
                <li>Email us for quick questions</li>
                <li>Call for urgent matters</li>
              </ul>
            </div>
          </div>
        );

      case 'aws-bedrock':
        return (
          <div className="page-content">
            <h2>Built on AWS Bedrock</h2>
            <div className="tech-info">
              <p>Eida is powered by advanced AI technology through AWS Bedrock, providing:</p>
              <ul>
                <li>Natural language processing for better understanding</li>
                <li>Contextual responses tailored to UTD students</li>
                <li>Secure and reliable AI infrastructure</li>
                <li>Continuous learning and improvement</li>
              </ul>
              <div className="tech-badges">
                <span className="tech-badge">AWS Bedrock</span>
                <span className="tech-badge">Claude AI</span>
                <span className="tech-badge">Secure</span>
                <span className="tech-badge">Reliable</span>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <>
            {/* Window Controls */}
            <div className="window-controls">
              <div className="window-control close"></div>
              <div className="window-control minimize"></div>
              <div className="window-control maximize"></div>
            </div>

            {/* Chat Area */}
            <div className="chat-area">
              {messages.map(message => (
                <Message
                  key={message.id}
                  content={message.content}
                  isUser={message.isUser}
                  timestamp={message.timestamp}
                  id={message.id}
                />
              ))}

              {isLoading && (
                <div className="loading-indicator">
                  <div className="loading-dots">
                    <div className="loading-dots-content">
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Start Buttons */}
            <div className="quick-start-section">
              {quickStartOptions.map((option, index) => (
                <button
                  key={index}
                  className="quick-start-button"
                  onClick={() => handleQuickStart(`I need help with ${option.toLowerCase()}`)}
                >
                  {option}
                </button>
              ))}
            </div>

            {/* Input Section */}
            <InputBar
              onSendMessage={handleSendMessage}
              disabled={isLoading}
              onFileUpload={handleFileUpload}
              triggerFileUpload={triggerFileUpload}
              isUploading={isUploading}
              uploadedFile={uploadedFile}
              fileInputRef={fileInputRef}
            />
          </>
        );
    }
  };

  return (
    <div className={`chatbot-container ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">EIDA</h1>
          <p className="sidebar-subtitle">the UTD advisor</p>
        </div>

        <div className="sidebar-nav">
          <button
            className={`nav-item ${currentPage === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentPage('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`nav-item ${currentPage === 'contact' ? 'active' : ''}`}
            onClick={() => setCurrentPage('contact')}
          >
            📞 Contact
          </button>
          <button
            className={`nav-item ${currentPage === 'aws-bedrock' ? 'active' : ''}`}
            onClick={() => setCurrentPage('aws-bedrock')}
          >
            ⚡ Built on AWS Bedrock
          </button>
        </div>

        <div className="theme-toggle-section">
          <button
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>

        <div className="sidebar-footer">
          <p className="footer-text">© 2025 UTDallas</p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-chat-area">{renderPage()}</div>
    </div>
  );
};

export default ChatBot;
