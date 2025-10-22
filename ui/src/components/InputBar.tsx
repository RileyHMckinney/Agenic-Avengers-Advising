import React, { useState, useRef, useEffect } from 'react';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  onFileUpload?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  triggerFileUpload?: () => void;
  isUploading?: boolean;
  uploadedFile?: File | null;
  fileInputRef?: React.RefObject<HTMLInputElement | null>;
}

const InputBar: React.FC<InputBarProps> = ({ 
  onSendMessage, 
  disabled = false,
  onFileUpload,
  triggerFileUpload,
  isUploading = false,
  uploadedFile,
  fileInputRef
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 100)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  return (
    <div className="input-section">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question"
        disabled={disabled}
        className="input-textarea"
        rows={1}
      />
      
      {/* Upload Button */}
      <button
        type="button"
        onClick={triggerFileUpload}
        disabled={disabled || isUploading}
        className="upload-button"
        title="Upload Resume"
      >
        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-circle"></div>
          </div>
        ) : uploadedFile ? (
          <div className="upload-success">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        ) : (
          <div className="upload-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="upload-text">Upload Resume</span>
          </div>
        )}
      </button>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={onFileUpload}
        style={{ display: 'none' }}
      />

      <button
        type="submit"
        onClick={handleSubmit}
        disabled={!message.trim() || disabled}
        className="send-button"
      >
        <svg
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
    </div>
  );
};

export default InputBar;
