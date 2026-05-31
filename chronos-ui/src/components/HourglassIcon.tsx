import React from 'react';

export const HourglassIcon: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M5 2h14M5 22h14M6 2v4l6 6-6 6v4M18 2v4l-6 6 6 6v4" />
  </svg>
);
