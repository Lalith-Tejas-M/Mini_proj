import React, { useState } from 'react';
import { Brain, ArrowRight, Activity, Zap } from 'lucide-react';
import ConfidenceBar from './ConfidenceBar';
import ValidationBadge from './ValidationBadge';
import FeedbackControls from '../feedback/FeedbackControls';

const InsightCard = ({ insight }) => {
  const [expanded, setExpanded] = useState(false);

  // Safely parse JSON strings if they came directly from DB rows, else use objects
  const parseJsonSafe = (data) => {
    if (typeof data === 'string') {
      try {
        // DB might return single quotes depending on python str() vs json.dumps()
        // we'll try to handle it gracefully
        return JSON.parse(data.replace(/'/g, '"'));
      } catch (e) {
        return {};
      }
    }
    return data || {};
  };

  const comparison = parseJsonSafe(insight.comparison);
  const recommendations = parseJsonSafe(insight.recommendations);

  return (
    <div className="glass-panel overflow-hidden transition-all duration-300 hover:border-primary/30">
      {/* Header */}
      <div className="p-5 border-b border-surfaceHighlight bg-surface/50 flex flex-wrap gap-4 items-center justify-between cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/20">
            <Brain className="text-primary" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-textMain">Agentic Insight</h3>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-textMuted flex items-center gap-1"><Activity size={12}/> AI Synthesized</span>
              <ValidationBadge passed={insight.validation_passed} />
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="text-right hidden sm:block">
            <p className="text-xs text-textMuted mb-1">Confidence Score</p>
            <ConfidenceBar score={insight.confidence_score} />
          </div>
          <FeedbackControls insightId={insight.id} />
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        <div>
          <p className="text-textMain leading-relaxed">{insight.insight_text}</p>
        </div>

        {/* Comparison Block */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-background rounded-xl p-4 border border-surfaceHighlight border-l-4 border-l-warning">
            <h4 className="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">Historical Practice</h4>
            <p className="text-sm text-textMain">{comparison.traditional_practice || "N/A"}</p>
          </div>
          <div className="bg-background rounded-xl p-4 border border-surfaceHighlight border-l-4 border-l-success relative">
            <div className="absolute -left-[26px] top-1/2 -translate-y-1/2 hidden md:block">
              <div className="bg-surfaceHighlight rounded-full p-1"><ArrowRight size={14} className="text-textMuted"/></div>
            </div>
            <h4 className="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">Modern Equivalent</h4>
            <p className="text-sm text-textMain">{comparison.modern_equivalent || "N/A"}</p>
          </div>
        </div>

        {/* Impact */}
        <div className="bg-surfaceHighlight/30 rounded-xl p-4 border border-surfaceHighlight border-dashed">
          <p className="text-sm text-textMuted"><span className="font-semibold text-textMain">Systemic Impact:</span> {comparison.impact_of_shift || "N/A"}</p>
        </div>

        {/* Actionable Rec */}
        {expanded && (
          <div className="pt-4 border-t border-surfaceHighlight animate-in fade-in slide-in-from-top-2">
            <div className="flex gap-4 p-4 rounded-xl bg-gradient-to-r from-primary/10 to-transparent border border-primary/20">
              <div className="mt-1"><Zap className="text-primary fill-primary/20" size={20} /></div>
              <div>
                <h4 className="font-bold text-primary mb-1">Recommended Action</h4>
                <p className="text-sm text-textMain mb-2">{recommendations.actionable_step || "N/A"}</p>
                <p className="text-xs text-textMuted italic">Benefit: {recommendations.expected_benefit || "N/A"}</p>
              </div>
            </div>
          </div>
        )}
        
        {!expanded && (
          <button 
            onClick={() => setExpanded(true)}
            className="w-full py-2 text-xs font-medium text-textMuted hover:text-primary transition-colors flex items-center justify-center gap-1"
          >
            Show Recommendations
          </button>
        )}
      </div>
    </div>
  );
};

export default InsightCard;
