import React from 'react';

export const ProgressBar = ({ percentage = 0, className = 'h-2.5' }) => {
  const clamped = Math.min(Math.max(percentage, 0), 100);

  let barColor = 'bg-emerald-500';
  if (percentage >= 100) {
    barColor = 'bg-rose-500';
  } else if (percentage >= 80) {
    barColor = 'bg-amber-500';
  }

  return (
    <div className={`w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden ${className}`}>
      <div
        className={`h-full transition-all duration-500 ease-out rounded-full ${barColor}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
};

export default ProgressBar;
