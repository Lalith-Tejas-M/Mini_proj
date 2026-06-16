import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import api from '../../api/client';
import useStore from '../../store/useStore';
import toast from 'react-hot-toast';

const FeedbackControls = ({ insightId }) => {
  const [feedback, setFeedback] = useState(null); // 'thumbs_up' | 'thumbs_down' | null
  const user = useStore(state => state.user);

  const handleFeedback = async (rating) => {
    if (!user || !insightId) return;
    
    // Optimistic UI update
    setFeedback(rating);
    
    try {
      await api.post('/feedback/', {
        insight_id: insightId,
        user_id: user.id,
        rating: rating,
        context_tag: "dashboard_ui"
      });
      toast.success('Feedback recorded. The agent will learn from this.', {
        icon: rating === 'thumbs_up' ? '👍' : '👎',
      });
    } catch (err) {
      setFeedback(null); // revert on fail
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button 
        onClick={() => handleFeedback('thumbs_up')}
        className={`p-2 rounded-lg transition-colors border ${
          feedback === 'thumbs_up' 
            ? 'bg-success/20 border-success/50 text-success' 
            : 'bg-background border-surfaceHighlight text-textMuted hover:text-success hover:border-success/30'
        }`}
        title="Helpful insight"
      >
        <ThumbsUp size={16} className={feedback === 'thumbs_up' ? 'fill-current' : ''} />
      </button>
      <button 
        onClick={() => handleFeedback('thumbs_down')}
        className={`p-2 rounded-lg transition-colors border ${
          feedback === 'thumbs_down' 
            ? 'bg-danger/20 border-danger/50 text-danger' 
            : 'bg-background border-surfaceHighlight text-textMuted hover:text-danger hover:border-danger/30'
        }`}
        title="Not helpful / Inaccurate"
      >
        <ThumbsDown size={16} className={feedback === 'thumbs_down' ? 'fill-current' : ''} />
      </button>
    </div>
  );
};

export default FeedbackControls;
