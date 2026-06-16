import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, Search } from 'lucide-react';
import api from '../api/client';
import useStore from '../store/useStore';
import InsightCard from '../components/insights/InsightCard';

const Dashboard = () => {
  const [topic, setTopic] = useState('');
  const [generating, setGenerating] = useState(false);
  const user = useStore(state => state.user);
  const { recentInsights, addInsight, setRecentInsights } = useStore();

  // Load latest on mount
  useEffect(() => {
    if (user?.id) {
      api.get(`/visualization/dashboard?user_id=${user.id}`)
        .then(res => {
          if (res.data.recent_insights) {
            setRecentInsights(res.data.recent_insights);
          }
        })
        .catch(console.error);
    }
  }, [user]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim() || !user) return;
    
    setGenerating(true);
    try {
      const res = await api.post('/insights/generate', {
        topic: topic,
        user_id: user.id
      });
      // Add new insight to the top of the list
      addInsight(res.data);
      setTopic('');
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Hero Section */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-surface to-background border border-surfaceHighlight p-8 sm:p-12">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/20 blur-[100px] rounded-full pointer-events-none"></div>
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl font-bold text-textMain mb-4">Generate Structural Insights</h1>
          <p className="text-lg text-textMuted mb-8">
            Query the intergenerational memory bank. The Agentic AI will retrieve historical context, validate patterns, and generate grounded recommendations.
          </p>
          
          <form onSubmit={handleGenerate} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-textMuted" size={20} />
              <input 
                type="text" 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., How did people save money in the 1980s?"
                className="w-full bg-surfaceHighlight/50 border border-surfaceHighlight rounded-2xl py-4 pl-12 pr-4 text-textMain focus:outline-none focus:border-primary focus:bg-surfaceHighlight transition-all shadow-inner"
              />
            </div>
            <button 
              type="submit"
              disabled={generating || !topic.trim()}
              className="px-8 py-4 bg-primary hover:bg-primaryHover disabled:opacity-50 disabled:hover:bg-primary text-white rounded-2xl font-semibold transition-all shadow-lg shadow-primary/25 flex items-center gap-2"
            >
              {generating ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
              {generating ? 'Synthesizing...' : 'Generate'}
            </button>
          </form>
        </div>
      </div>

      {/* Feed Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-textMain">Recent Intelligence</h2>
        </div>
        
        <div className="space-y-6">
          {recentInsights.length === 0 ? (
            <div className="text-center py-12 border border-dashed border-surfaceHighlight rounded-2xl">
              <p className="text-textMuted">No insights generated yet. Query the bank above!</p>
            </div>
          ) : (
            recentInsights.map((insight, idx) => (
              <InsightCard key={insight.id || idx} insight={insight} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
