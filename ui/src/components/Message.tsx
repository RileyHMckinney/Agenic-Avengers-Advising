import React from 'react';

interface MessageProps {
  content: string;
  isUser: boolean;
  timestamp: Date;
  id: string;
}

const Message: React.FC<MessageProps> = ({ content, isUser, timestamp, id }) => {
  return (
    <div
      className={`message-container ${isUser ? 'user' : 'bot'}`}
      key={id}
    >
      <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
        <div className="message-content">{content}</div>
        <div className="message-timestamp">
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

export default Message;
