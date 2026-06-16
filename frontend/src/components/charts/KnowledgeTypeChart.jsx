import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

const KnowledgeTypeChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="h-full flex items-center justify-center text-textMuted">No extraction data yet.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={80}
          outerRadius={110}
          paddingAngle={5}
          dataKey="value"
          stroke="none"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          contentStyle={{ backgroundColor: '#1a1f33', borderColor: '#2a314d', borderRadius: '12px', color: '#f8fafc' }}
          itemStyle={{ color: '#f8fafc' }}
        />
        <Legend verticalAlign="bottom" height={36} iconType="circle" />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default KnowledgeTypeChart;
