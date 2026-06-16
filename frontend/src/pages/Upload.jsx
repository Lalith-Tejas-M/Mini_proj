import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/upload/FileUploader';
import SpeechRecorder from '../components/upload/SpeechRecorder';
import { Type, Mic, FileText } from 'lucide-react';
import api from '../api/client';
import useStore from '../store/useStore';
import toast from 'react-hot-toast';

const Upload = () => {
  const [activeTab, setActiveTab] = useState('text');
  const [rawText, setRawText] = useState('');
  const [uploading, setUploading] = useState(false);
  const user = useStore(state => state.user);
  const navigate = useNavigate();

  const handleTextUpload = async () => {
    if (!rawText.trim() || !user) return;
    setUploading(true);
    
    try {
      const res = await api.post('/upload/text', {
        text: rawText,
        user_id: user.id
      });
      
      toast.success('Text saved! Extracting intelligence...');
      
      // Kick off extraction
      await api.post('/knowledge/extract', { upload_id: res.data.id });
      toast.success('Knowledge stored in Memory Bank!');
      setRawText('');
      
      // Redirect to dashboard so user can query it immediately
      navigate('/dashboard');
      
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold text-textMain mb-2">Preserve Knowledge</h1>
        <p className="text-textMuted">Upload experiences, practices, or thoughts to process into structured intelligence.</p>
      </div>

      <div className="flex p-1 bg-surfaceHighlight rounded-xl w-fit">
        {[
          { id: 'text', label: 'Raw Text', icon: Type },
          { id: 'audio', label: 'Speech (Whisper)', icon: Mic },
          { id: 'file', label: 'Document (PDF/DOCX)', icon: FileText },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id 
                ? 'bg-primary text-white shadow-md' 
                : 'text-textMuted hover:text-textMain hover:bg-surfaceHighlight/50'
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="glass-panel p-8 min-h-[400px]">
        {activeTab === 'text' && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Text Input</h3>
            <textarea 
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full h-64 bg-background border border-surfaceHighlight rounded-xl p-4 text-textMain focus:outline-none focus:border-primary transition-colors resize-none placeholder:text-surfaceHighlight"
              placeholder="Paste the raw text experiences or stories here..."
            />
            <div className="flex justify-end">
              <button 
                onClick={handleTextUpload}
                disabled={uploading || !rawText.trim()}
                className="px-6 py-2.5 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-xl font-medium transition-colors shadow-lg shadow-primary/25"
              >
                {uploading ? 'Processing...' : 'Process Knowledge'}
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'file' && <FileUploader />}
        {activeTab === 'audio' && <SpeechRecorder />}
      </div>
    </div>
  );
};

export default Upload;
