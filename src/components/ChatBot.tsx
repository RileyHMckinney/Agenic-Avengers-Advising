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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate realistic bot responses based on the user's question
    setTimeout(() => {
      let botResponse = '';
      
      if (content.toLowerCase().includes('resume')) {
        botResponse = `Great question about resume advice! Here are some key tips:\n\n• Use action verbs like "developed," "managed," or "implemented"\n• Quantify your achievements with numbers and percentages\n• Keep it to 1-2 pages maximum\n• Tailor it to each specific job application\n• Include relevant coursework and projects\n\nWould you like me to help you with a specific section of your resume?`;
      } else if (content.toLowerCase().includes('job search')) {
        botResponse = `I'd be happy to help with your job search strategy! Here's what I recommend:\n\n• Start with UTD's Handshake platform for internships and jobs\n• Network through LinkedIn and attend career fairs\n• Research companies that align with your major and interests\n• Prepare a 30-second elevator pitch about yourself\n• Follow up on applications within 1-2 weeks\n\nWhat field are you most interested in? I can provide more targeted advice!`;
      } else if (content.toLowerCase().includes('course planning')) {
        botResponse = `Course planning is crucial for your academic success! Here's my advice:\n\n• Meet with your academic advisor each semester\n• Check degree requirements in your catalog\n• Balance difficult courses with easier ones\n• Consider prerequisites and course availability\n• Plan for internships, study abroad, or research opportunities\n\nWhat's your major? I can help you create a semester-by-semester plan!`;
      } else if (content.toLowerCase().includes('interview')) {
        botResponse = `Interview preparation is key to landing that job! Here are my top tips:\n\n• Research the company and role thoroughly\n• Practice the STAR method for behavioral questions\n• Prepare thoughtful questions to ask them\n• Dress professionally and arrive 10 minutes early\n• Follow up with a thank-you email within 24 hours\n\nWould you like to practice some common interview questions?`;
      } else {
        botResponse = `I'm here to help with all your academic and career needs! I can assist with:\n\n• Resume and cover letter writing\n• Job search strategies and networking\n• Course planning and degree requirements\n• Interview preparation and practice\n• Internship and research opportunities\n\nWhat specific area would you like to explore? I'm here to guide you through your UTD journey!`;
      }

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: botResponse,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleQuickStart = (message: string) => {
    handleSendMessage(message);
  };

  const quickStartOptions = [
    'Resume Advice',
    'Job Search', 
    'Course Planning',
    'Interview Prep'
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
              {messages.map((message) => (
                <Message
                  key={message.id}
                  content={message.content}
                  isUser={message.isUser}
                  timestamp={message.timestamp}
                  id={message.id}
                />
              ))}
              
              {/* Loading indicator */}
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
            <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
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

        {/* Theme Toggle - Separate box */}
        <div className="theme-toggle-section">
          <button 
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>

        {/* Trademark - Separate box */}
        <div className="sidebar-footer">
          <p className="footer-text">© 2025 UTDallas</p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-chat-area">
        {renderPage()}
      </div>
    </div>
  );
};

export default ChatBot;
