import React from 'react';

const ConfidenceBar = ({ score }) => {
  // Score is expected to be between 0.0 and 1.0
  const percentage = Math.round((score || 0) * 100);
  
  let color = 'bg-danger';
  if (percentage >= 75) color = 'bg-success';
  else if (percentage >= 50) color = 'bg-warning';

  return (
    <div className="flex items-center gap-3">
      <div className="w-24 h-2 bg-surfaceHighlight rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-1000 ease-out`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-textMuted w-8">{percentage}%</span>
    </div>
  );
};

export default ConfidenceBar;
