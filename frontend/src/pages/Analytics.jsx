import React, { useEffect, useState } from 'react';
import api from '../api/client';
import useStore from '../store/useStore';
import KnowledgeTypeChart from '../components/charts/KnowledgeTypeChart';
import ConfidenceHistogram from '../components/charts/ConfidenceHistogram';
import { Loader2 } from 'lucide-react';

const Analytics = () => {
  const user = useStore(state => state.user);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      api.get(`/visualization/dashboard?user_id=${user.id}`)
        .then(res => {
          setData(res.data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) return <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-primary" size={32} /></div>;
  if (!data) return <div className="text-center text-textMuted mt-12">No data available.</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-textMain mb-2">System Analytics</h1>
        <p className="text-textMuted">Real-time visualizations of the Agentic AI's performance and knowledge distribution.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-textMain mb-6">Knowledge Topography</h3>
          <div className="h-80">
            <KnowledgeTypeChart data={data.type_distribution} />
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-textMain mb-6">AI Confidence Distribution</h3>
          <div className="h-80">
            <ConfidenceHistogram data={data.confidence_scores} />
          </div>
        </div>
      </div>
      
      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 flex flex-col justify-center items-center text-center">
          <p className="text-4xl font-bold text-primary mb-2">
            {data.type_distribution.reduce((acc, curr) => acc + curr.value, 0)}
          </p>
          <p className="text-sm font-medium text-textMuted uppercase tracking-wider">Total Extractions</p>
        </div>
        <div className="glass-panel p-6 flex flex-col justify-center items-center text-center">
          <p className="text-4xl font-bold text-success mb-2">
            {data.confidence_scores.reduce((acc, curr) => acc + curr.count, 0)}
          </p>
          <p className="text-sm font-medium text-textMuted uppercase tracking-wider">Generated Insights</p>
        </div>
        <div className="glass-panel p-6 flex flex-col justify-center items-center text-center">
          <p className="text-4xl font-bold text-warning mb-2">V1.0</p>
          <p className="text-sm font-medium text-textMuted uppercase tracking-wider">Structuring Agent</p>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
