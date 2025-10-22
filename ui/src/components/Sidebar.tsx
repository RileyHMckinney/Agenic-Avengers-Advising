import React from 'react';

interface QuickStartButtonProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
}

const QuickStartButton: React.FC<QuickStartButtonProps> = ({
  title,
  description,
  icon,
  onClick,
}) => {
  return (
    <button
      onClick={onClick}
      className="quick-start-button"
    >
      <div className="button-content">
        <div className="button-icon">
          {icon}
        </div>
        <div className="button-text">
          <h3 className="button-title">
            {title}
          </h3>
          <p className="button-description">{description}</p>
        </div>
      </div>
    </button>
  );
};

interface SidebarProps {
  onQuickStart: (message: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onQuickStart }) => {
  const quickStartOptions = [
    {
      title: 'Resume Advice',
      description: 'Get help crafting the perfect resume',
      icon: (
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      message: 'I need help improving my resume. Can you review it and provide suggestions?',
    },
    {
      title: 'Job Search',
      description: 'Find opportunities and career guidance',
      icon: (
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6" />
        </svg>
      ),
      message: 'I\'m looking for job opportunities in my field. Can you help me with my job search strategy?',
    },
    {
      title: 'Course Planning',
      description: 'Plan your academic journey',
      icon: (
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      message: 'I need help planning my course schedule for next semester. What courses should I consider?',
    },
    {
      title: 'Interview Prep',
      description: 'Prepare for job interviews',
      icon: (
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
      message: 'I have an interview coming up. Can you help me prepare with common questions and tips?',
    },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Quick Start</h2>
        <p className="sidebar-subtitle">
          Choose a topic to get started with personalized advice
        </p>
      </div>
      
      <div>
        {quickStartOptions.map((option, index) => (
          <QuickStartButton
            key={index}
            title={option.title}
            description={option.description}
            icon={option.icon}
            onClick={() => onQuickStart(option.message)}
          />
        ))}
      </div>

      <div className="pro-tip">
        <h3 className="pro-tip-title">💡 Pro Tip</h3>
        <p className="pro-tip-text">
          Be specific about your goals and current situation for more personalized advice!
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
