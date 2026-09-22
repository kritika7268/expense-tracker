import React from 'react';

export const LoadingSkeleton = ({ count = 3, className = 'h-16' }) => {
  return (
    <div className="space-y-3 w-full animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`w-full bg-slate-200/70 dark:bg-slate-800/60 rounded-xl ${className}`}
        />
      ))}
    </div>
  );
};

export default LoadingSkeleton;
