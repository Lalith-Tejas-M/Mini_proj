import React from 'react';
import useStore from '../store/useStore';
import InsightCard from '../components/insights/InsightCard';

const History = () => {
  const { recentInsights } = useStore();

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-textMain mb-2">Memory History</h1>
        <p className="text-textMuted">A complete timeline of all synthesized intelligence from this node.</p>
      </div>

      <div className="space-y-6">
        {recentInsights.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-surfaceHighlight rounded-2xl">
            <p className="text-textMuted">No history available.</p>
          </div>
        ) : (
          recentInsights.map((insight, idx) => (
            <InsightCard key={insight.id || idx} insight={insight} />
          ))
        )}
      </div>
    </div>
  );
};

export default History;
