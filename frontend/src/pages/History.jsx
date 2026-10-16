import { useState, useEffect } from 'react';
import useStore from '../store/useStore';
import InsightCard from '../components/insights/InsightCard';
import api from '../api/client';
import { Loader2, RefreshCw, History as HistoryIcon } from 'lucide-react';

const PAGE_LIMIT = 10;

const History = () => {
  const user = useStore(state => state.user);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);

  const userId = user?.id;

  const loadInsights = async (currentOffset = 0, isAppend = false) => {
    if (!userId) return;
    if (isAppend) {
      setLoadingMore(true);
    } else {
      setLoading(true);
      setError(null);
    }

    try {
      const res = await api.get(`/insights/history?user_id=${userId}&limit=${PAGE_LIMIT}&offset=${currentOffset}`);
      const data = res.data;
      if (isAppend) {
        setInsights(prev => [...prev, ...(data.insights || [])]);
      } else {
        setInsights(data.insights || []);
      }
      setTotal(data.total || 0);
      setOffset(currentOffset);
    } catch (err) {
      console.error('Failed to load history:', err);
      setError('Failed to load memory history. Please verify your connection.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    if (!userId) {
      return;
    }

    api.get(`/insights/history?user_id=${userId}&limit=${PAGE_LIMIT}&offset=0`)
      .then(res => {
        if (isMounted) {
          setInsights(res.data.insights || []);
          setTotal(res.data.total || 0);
          setOffset(0);
          setLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          console.error('Failed to load history:', err);
          setError('Failed to load memory history. Please verify your connection.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [userId]);

  const handleLoadMore = () => {
    const nextOffset = offset + PAGE_LIMIT;
    if (nextOffset < total) {
      loadInsights(nextOffset, true);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-textMain mb-2 flex items-center gap-3">
            <HistoryIcon className="text-primary" size={28} />
            Memory History
          </h1>
          <p className="text-textMuted">
            A persisted timeline of all synthesized intelligence for your profile ({total} total insights).
          </p>
        </div>
        <button 
          onClick={() => loadInsights(0, false)} 
          disabled={loading}
          className="p-2.5 bg-surfaceHighlight hover:bg-surfaceHighlight/80 text-textMuted hover:text-textMain rounded-xl transition-colors"
          title="Refresh history"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-20 text-textMuted gap-3">
          <Loader2 className="animate-spin text-primary" size={32} />
          <p className="text-sm">Retrieving persisted insights from database...</p>
        </div>
      )}

      {error && !loading && (
        <div className="glass-panel p-8 text-center space-y-4 border-danger/20">
          <p className="text-danger font-medium">{error}</p>
          <button 
            onClick={() => loadInsights(0, false)}
            className="px-6 py-2 bg-primary hover:bg-primaryHover text-white rounded-xl text-sm font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && insights.length === 0 && (
        <div className="text-center py-16 border border-dashed border-surfaceHighlight rounded-3xl space-y-3">
          <HistoryIcon className="mx-auto text-textMuted/50" size={40} />
          <h3 className="text-lg font-semibold text-textMain">No History Yet</h3>
          <p className="text-sm text-textMuted max-w-sm mx-auto">
            You haven't generated any insights yet. Ask a question from the Dashboard to preserve your first insight!
          </p>
        </div>
      )}

      {!loading && !error && insights.length > 0 && (
        <div className="space-y-6">
          {insights.map((insight, idx) => (
            <InsightCard key={insight.id || idx} insight={insight} />
          ))}

          {insights.length < total && (
            <div className="text-center pt-4">
              <button 
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="px-6 py-2.5 bg-surfaceHighlight hover:bg-surfaceHighlight/80 text-textMain rounded-xl text-sm font-medium transition-colors disabled:opacity-50 inline-flex items-center gap-2"
              >
                {loadingMore && <Loader2 size={16} className="animate-spin" />}
                {loadingMore ? 'Loading older insights...' : `Load More (${total - insights.length} remaining)`}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default History;
