import { useState, useEffect } from 'react';
import useStore from '../store/useStore';
import { User, LogOut, Sliders, Save, Loader2, Check } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, setUser, logout } = useStore();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Preference Form States
  const [topics, setTopics] = useState('');
  const [preferredTone, setPreferredTone] = useState('practical');
  const [focusEra, setFocusEra] = useState('all');
  const [actionabilityLevel, setActionabilityLevel] = useState('high');

  const userId = user?.id;

  useEffect(() => {
    let isMounted = true;
    if (!userId) {
      return;
    }
    
    // Fetch profile and preferences from backend
    api.get(`/users/${userId}/profile`)
      .then(res => {
        if (!isMounted) return;
        const prefs = res.data.preferences || {};
        if (prefs.topics_of_interest) {
          setTopics(Array.isArray(prefs.topics_of_interest) ? prefs.topics_of_interest.join(', ') : prefs.topics_of_interest);
        }
        if (prefs.preferred_tone) setPreferredTone(prefs.preferred_tone);
        if (prefs.focus_era) setFocusEra(prefs.focus_era);
        if (prefs.actionability_level) setActionabilityLevel(prefs.actionability_level);
        
        // Sync with store
        useStore.setState(state => ({
          user: state.user ? { ...state.user, preferences: prefs } : null
        }));
      })
      .catch(err => {
        if (isMounted) console.error('Failed to load profile:', err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [userId]);

  const handleSavePreferences = async (e) => {
    e.preventDefault();
    if (!user?.id) return;
    setSaving(true);
    setSavedSuccess(false);

    const payload = {
      preferences: {
        topics_of_interest: topics.split(',').map(t => t.trim()).filter(Boolean),
        preferred_tone: preferredTone,
        focus_era: focusEra,
        actionability_level: actionabilityLevel
      }
    };

    try {
      const res = await api.put(`/users/${user.id}/preferences`, payload);
      toast.success('Agent persona preferences saved!');
      setSavedSuccess(true);
      setUser({ ...user, preferences: res.data.preferences });
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error(err);
      toast.error('Failed to save preferences.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-textMain mb-2">User Profile & Persona</h1>
        <p className="text-textMuted">Customize how the Agentic AI personalizes historical insight generation.</p>
      </div>

      <div className="glass-panel p-8 space-y-8">
        {/* User Info Header */}
        <div className="flex items-center gap-6 pb-8 border-b border-surfaceHighlight">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-primaryHover flex items-center justify-center font-bold text-white text-3xl shadow-lg shadow-primary/25">
            {user?.name?.charAt(0) || <User size={32} />}
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-textMain">{user?.name || 'Guest'}</h2>
            <p className="text-textMuted">{user?.email || 'Not logged in'}</p>
            <p className="text-xs text-textMuted/75 mt-1 font-mono">User ID: {user?.id || 'N/A'}</p>
          </div>
        </div>

        {/* Preferences Form */}
        <form onSubmit={handleSavePreferences} className="space-y-6">
          <div className="flex items-center gap-2 pb-2 border-b border-surfaceHighlight/50">
            <Sliders size={20} className="text-primary" />
            <h3 className="font-semibold text-textMain">Agentic AI Persona Preferences</h3>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-10 gap-2 text-textMuted">
              <Loader2 size={20} className="animate-spin text-primary" />
              <span>Loading preferences...</span>
            </div>
          ) : (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-textMain mb-1.5">
                  Topics of Interest (Comma separated)
                </label>
                <input 
                  type="text"
                  value={topics}
                  onChange={(e) => setTopics(e.target.value)}
                  placeholder="e.g. Frugality, Farming, Traditional Craftsmanship, Community Governance"
                  className="w-full bg-background border border-surfaceHighlight rounded-xl px-4 py-3 text-textMain text-sm focus:outline-none focus:border-primary transition-colors"
                />
                <p className="text-xs text-textMuted mt-1">Insights will be guided towards these traditional themes.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-textMain mb-1.5">
                    Preferred Tone
                  </label>
                  <select 
                    value={preferredTone}
                    onChange={(e) => setPreferredTone(e.target.value)}
                    className="w-full bg-background border border-surfaceHighlight rounded-xl px-3 py-3 text-textMain text-sm focus:outline-none focus:border-primary transition-colors"
                  >
                    <option value="practical">Practical & Direct</option>
                    <option value="philosophical">Philosophical & Reflective</option>
                    <option value="analytical">Analytical & Comparative</option>
                    <option value="storytelling">Narrative & Experiential</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-textMain mb-1.5">
                    Priority Focus Era
                  </label>
                  <select 
                    value={focusEra}
                    onChange={(e) => setFocusEra(e.target.value)}
                    className="w-full bg-background border border-surfaceHighlight rounded-xl px-3 py-3 text-textMain text-sm focus:outline-none focus:border-primary transition-colors"
                  >
                    <option value="all">All Eras (Universal Wisdom)</option>
                    <option value="pre-industrial">Pre-Industrial / Ancient</option>
                    <option value="early-20th-century">Early 20th Century (1900-1940)</option>
                    <option value="mid-20th-century">Mid 20th Century (1940-1980)</option>
                    <option value="late-20th-century">Late 20th Century (1980-2000)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-textMain mb-1.5">
                    Actionability Level
                  </label>
                  <select 
                    value={actionabilityLevel}
                    onChange={(e) => setActionabilityLevel(e.target.value)}
                    className="w-full bg-background border border-surfaceHighlight rounded-xl px-3 py-3 text-textMain text-sm focus:outline-none focus:border-primary transition-colors"
                  >
                    <option value="high">High (Concrete daily action)</option>
                    <option value="balanced">Balanced (Context & steps)</option>
                    <option value="reflective">Reflective (Behavioral mindset)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button 
                  type="submit"
                  disabled={saving}
                  className="px-6 py-2.5 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-xl font-medium text-sm transition-all shadow-lg shadow-primary/25 flex items-center gap-2"
                >
                  {saving ? <Loader2 size={16} className="animate-spin" /> : savedSuccess ? <Check size={16} /> : <Save size={16} />}
                  {saving ? 'Saving...' : savedSuccess ? 'Preferences Saved' : 'Save Preferences'}
                </button>
              </div>
            </div>
          )}
        </form>

        {/* Account Actions */}
        <div className="pt-6 border-t border-surfaceHighlight flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-textMain">Session Management</h4>
            <p className="text-xs text-textMuted">End your session on this browser device.</p>
          </div>
          <button 
            onClick={logout}
            className="flex items-center gap-2 px-5 py-2.5 bg-danger/10 hover:bg-danger/20 text-danger rounded-xl font-medium text-sm transition-colors border border-danger/20"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
