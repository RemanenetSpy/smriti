import React from 'react';

interface LogoProps {
  className?: string;
  variant?: 'full' | 'compact' | 'splash';
}

export const Logo: React.FC<LogoProps> = ({ className = '', variant = 'full' }) => {
  const isCompact = variant === 'compact';
  const isSplash  = variant === 'splash';

  return (
    <div className={`flex ${isCompact ? 'flex-row items-center gap-3' : 'flex-col items-center'} ${className}`}>
      <svg
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
        className={`${isCompact ? 'w-8 h-8' : isSplash ? 'w-24 h-24 sm:w-32 sm:h-32 md:w-40 md:h-40 mb-6 sm:mb-10' : 'w-24 h-24 mb-6'}`}
      >
        {isSplash && (
          <circle cx="50" cy="50" r="49" fill="none" stroke="#1a1a1a" strokeWidth="0.5" opacity="0.5" />
        )}
        <circle cx="50" cy="50" r="46" fill="none" stroke="#1a1a1a" strokeWidth="1" />
        <circle cx="50" cy="50" r="42" fill="none" stroke="#1a1a1a" strokeWidth="0.5" strokeDasharray="1 2" />

        <g className="origin-[50px_50px] animate-[pulse_10s_ease-in-out_infinite]">
          <circle cx="50" cy="50" r="18" fill="#1a1a1a" />
          <circle cx="50" cy="50" r="24" fill="none" stroke="#1a1a1a" strokeWidth="1.5" opacity="0.6" strokeDasharray="4 2" />
          <circle cx="50" cy="50" r="32" fill="none" stroke="#1a1a1a" strokeWidth="0.8" opacity="0.3" strokeDasharray="2 4" />
        </g>
      </svg>

      <div className={`${isCompact ? 'flex items-center tracking-[0.15em]' : 'flex items-center justify-center w-full'}`}>
        <span className={`serif ${isCompact ? 'text-base font-semibold' : isSplash ? 'text-2xl sm:text-4xl md:text-5xl tracking-wide' : 'text-2xl tracking-wide'} text-[#1a1a1a]`}>
          {isCompact ? 'Smriti' : 'Smriti'}
        </span>
      </div>
    </div>
  );
};
