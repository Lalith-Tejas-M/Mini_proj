import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const ConfidenceHistogram = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="h-full flex items-center justify-center text-textMuted">No confidence data yet.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <XAxis 
          dataKey="range" 
          stroke="#94a3b8" 
          tick={{ fill: '#94a3b8', fontSize: 12 }} 
          axisLine={false} 
          tickLine={false} 
        />
        <YAxis 
          stroke="#94a3b8" 
          tick={{ fill: '#94a3b8', fontSize: 12 }} 
          axisLine={false} 
          tickLine={false} 
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#1a1f33', borderColor: '#2a314d', borderRadius: '12px', color: '#f8fafc' }}
          cursor={{ fill: '#2a314d', opacity: 0.5 }}
        />
        <Bar 
          dataKey="count" 
          fill="#6366f1" 
          radius={[6, 6, 0, 0]} 
          animationDuration={1500}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default ConfidenceHistogram;
