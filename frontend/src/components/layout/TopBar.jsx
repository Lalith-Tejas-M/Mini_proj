import { useState, useEffect, useRef } from 'react';
import { Search, Bell, Loader2, X, Sparkles, BookOpen } from 'lucide-react';
import useStore from '../../store/useStore';
import api from '../../api/client';

const TopBar = () => {
  const user = useStore(state => state.user);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  
  const searchContainerRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleQueryChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    if (!val.trim() || val.trim().length < 2) {
      setResults([]);
      setIsSearching(false);
      setSearchError(null);
    } else {
      setIsOpen(true);
    }
  };

  // Debounced semantic search
  useEffect(() => {
    if (!query.trim() || query.trim().length < 2 || !user?.id) {
      return;
    }

    let isCancelled = false;
    const timer = setTimeout(async () => {
      setIsSearching(true);
      setSearchError(null);
      try {
        const res = await api.get('/knowledge/search', {
          params: {
            q: query.trim(),
            user_id: user.id,
            limit: 5
          }
        });
        if (!isCancelled) {
          setResults(res.data.results || []);
          setIsOpen(true);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Semantic search error:', err);
          setSearchError('Failed to search memory bank.');
          setIsOpen(true);
        }
      } finally {
        if (!isCancelled) {
          setIsSearching(false);
        }
      }
    }, 350);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [query, user?.id]);

  return (
    <div className="h-16 bg-surface/50 backdrop-blur-md border-b border-surfaceHighlight flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex-1 max-w-xl relative" ref={searchContainerRef}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={18} />
          <input 
            type="text" 
            value={query}
            onChange={handleQueryChange}
            onFocus={() => { if (query.trim().length >= 2) setIsOpen(true); }}
            onKeyDown={(e) => { if (e.key === 'Escape') setIsOpen(false); }}
            placeholder="Search memory (semantic embeddings)..." 
            className="w-full bg-background border border-surfaceHighlight rounded-full py-2 pl-10 pr-10 text-sm focus:outline-none focus:border-primary transition-colors text-textMain"
          />
          {query && (
            <button 
              onClick={() => { setQuery(''); setResults([]); setIsOpen(false); }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-textMuted hover:text-textMain"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Semantic Search Dropdown Modal */}
        {isOpen && query.trim().length >= 2 && (
          <div className="absolute top-12 left-0 right-0 bg-surface border border-surfaceHighlight rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2">
            <div className="p-3 bg-surfaceHighlight/30 border-b border-surfaceHighlight flex items-center justify-between text-xs text-textMuted">
              <span className="flex items-center gap-1.5 font-medium">
                <Sparkles size={14} className="text-primary" /> Semantic FAISS Retrieval
              </span>
              <span>Scoped to your memory</span>
            </div>

            <div className="max-h-96 overflow-y-auto p-2">
              {isSearching && (
                <div className="py-8 flex flex-col items-center justify-center gap-2 text-textMuted text-xs">
                  <Loader2 size={20} className="animate-spin text-primary" />
                  <span>Searching dense vector store...</span>
                </div>
              )}

              {searchError && !isSearching && (
                <div className="p-4 text-center text-xs text-danger">
                  {searchError}
                </div>
              )}

              {!isSearching && !searchError && results.length === 0 && (
                <div className="p-6 text-center text-xs text-textMuted space-y-1">
                  <BookOpen size={24} className="mx-auto text-textMuted/50 mb-2" />
                  <p className="font-medium text-textMain">No matching knowledge found</p>
                  <p>Try searching for life stories, frugal practices, or generational values.</p>
                </div>
              )}

              {!isSearching && !searchError && results.length > 0 && (
                <div className="space-y-1.5">
                  {results.map((item, idx) => (
                    <div 
                      key={item.id || idx}
                      className="p-3 hover:bg-surfaceHighlight/50 rounded-xl transition-colors cursor-pointer border border-transparent hover:border-surfaceHighlight"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                          {item.category || item.knowledge_type || 'Wisdom'}
                        </span>
                        <span className="text-xs text-textMuted font-mono">
                          {Math.round((item.relevance_score || item.similarity_score || 0) * 100)}% match
                        </span>
                      </div>
                      <h5 className="text-xs font-bold text-textMain">{item.topic}</h5>
                      <p className="text-xs text-textMuted line-clamp-2 mt-0.5 leading-relaxed">
                        {item.snippet || item.pattern || item.raw_snippet}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4 ml-4">
        <button className="p-2 text-textMuted hover:text-textMain transition-colors relative">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full"></span>
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-surfaceHighlight">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-textMain">{user?.name || 'Guest'}</p>
            <p className="text-xs text-textMuted">{user?.email || 'Not logged in'}</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-primaryHover flex items-center justify-center font-bold text-white shadow-lg">
            {user?.name?.charAt(0) || 'G'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
