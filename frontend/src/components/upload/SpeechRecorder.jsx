import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Square, Loader2, Play, AudioLines, CheckCircle2, AlertTriangle, Sparkles, RefreshCw } from 'lucide-react';
import api from '../../api/client';
import useStore from '../../store/useStore';
import toast from 'react-hot-toast';

const SpeechRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  // Status flow state
  const [uploadId, setUploadId] = useState(null);
  const [transcriptionStatus, setTranscriptionStatus] = useState(null); // 'pending' | 'processing' | 'completed' | 'failed'
  const [transcribedText, setTranscribedText] = useState('');
  const [extracting, setExtracting] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const pollIntervalRef = useRef(null);
  const user = useStore(state => state.user);
  const navigate = useNavigate();

  // Polling hook for upload status
  useEffect(() => {
    if (!uploadId || (transcriptionStatus !== 'pending' && transcriptionStatus !== 'processing')) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }

    const checkStatus = async () => {
      try {
        const res = await api.get(`/upload/${uploadId}/status`);
        const { status, raw_text, error_message } = res.data;
        setTranscriptionStatus(status);

        if (status === 'completed' || status === 'processed') {
          setTranscribedText(raw_text || '');
          toast.success('Audio transcribed successfully!');
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        } else if (status === 'failed') {
          toast.error(error_message || 'Transcription failed.');
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        }
      } catch (err) {
        console.error('Failed to poll upload status:', err);
      }
    };

    pollIntervalRef.current = setInterval(checkStatus, 2500);
    // Initial check
    checkStatus();

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [uploadId, transcriptionStatus]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setAudioBlob(null);
      setUploadId(null);
      setTranscriptionStatus(null);
      setTranscribedText('');
    } catch {
      toast.error('Microphone access denied or unavailable.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleUpload = async () => {
    if (!audioBlob || !user) return;
    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', new File([audioBlob], 'recording.webm', { type: 'audio/webm' }));
    formData.append('user_id', user.id);

    try {
      const res = await api.post('/upload/speech', formData);
      setUploadId(res.data.id);
      setTranscriptionStatus('pending');
      toast.success('Audio uploaded! Whisper transcription in progress...');
    } catch (err) {
      console.error(err);
      toast.error('Failed to upload audio recording.');
    } finally {
      setUploading(false);
    }
  };

  const handleExtractKnowledge = async () => {
    if (!uploadId) return;
    setExtracting(true);
    try {
      const res = await api.post('/knowledge/extract', { upload_id: uploadId });
      if (res.data.status === 'no_knowledge_found') {
        toast('No meaningful knowledge patterns found in this audio.', { icon: 'ℹ️' });
      } else {
        toast.success('Knowledge extracted and stored in Memory Bank!');
        navigate('/dashboard');
      }
    } catch (err) {
      console.error(err);
      toast.error('Extraction failed. Check backend logs.');
    } finally {
      setExtracting(false);
    }
  };

  const resetAll = () => {
    setAudioBlob(null);
    setUploadId(null);
    setTranscriptionStatus(null);
    setTranscribedText('');
    setIsRecording(false);
  };

  return (
    <div className="space-y-8 flex flex-col items-center justify-center py-8">
      <div className="text-center">
        <h3 className="text-xl font-medium mb-2">Speech to Knowledge</h3>
        <p className="text-sm text-textMuted max-w-md mx-auto">
          Speak naturally about an experience or historical practice. Local Whisper AI will transcribe and extract the patterns.
        </p>
      </div>

      {/* Recording Control Button */}
      {(!uploadId || transcriptionStatus === 'failed') && (
        <div className="flex flex-col items-center gap-6">
          <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 relative
            ${isRecording ? 'bg-danger/10 scale-105' : 'bg-surfaceHighlight'}`}>
            
            {isRecording && (
              <div className="absolute inset-0 rounded-full border-2 border-danger animate-ping opacity-75"></div>
            )}
            
            <button 
              onClick={isRecording ? stopRecording : startRecording}
              className={`w-20 h-20 rounded-full flex items-center justify-center text-white shadow-xl transition-all z-10
                ${isRecording ? 'bg-danger hover:bg-danger/80' : 'bg-primary hover:bg-primaryHover'}`}
            >
              {isRecording ? <Square size={32} className="fill-current" /> : <Mic size={32} />}
            </button>
          </div>
          
          <p className="font-medium text-textMain">
            {isRecording ? (
              <span className="text-danger flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-danger animate-pulse"></span> Recording... Click to Stop
              </span>
            ) : audioBlob ? 'Recording Ready for Upload' : 'Tap to Record'}
          </p>
        </div>
      )}

      {/* Audio playback & initial transcribe trigger */}
      {audioBlob && !isRecording && !uploadId && (
        <div className="w-full max-w-md bg-surfaceHighlight rounded-xl p-4 border border-surfaceHighlight animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-2 bg-background rounded-lg">
              <AudioLines className="text-primary" size={20} />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">Recording ready</p>
              <p className="text-xs text-textMuted">{(audioBlob.size / 1024).toFixed(1)} KB (WebM audio)</p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button 
              onClick={() => { const url = URL.createObjectURL(audioBlob); new Audio(url).play(); }}
              className="flex-1 py-2 bg-background hover:bg-background/80 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <Play size={16} /> Play
            </button>
            <button 
              onClick={handleUpload}
              disabled={uploading}
              className="flex-1 py-2 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-primary/25"
            >
              {uploading ? <Loader2 size={16} className="animate-spin" /> : 'Transcribe'}
            </button>
          </div>
        </div>
      )}

      {/* Transcription In Progress / Polling State */}
      {(transcriptionStatus === 'pending' || transcriptionStatus === 'processing') && (
        <div className="w-full max-w-md bg-surfaceHighlight/50 border border-surfaceHighlight rounded-2xl p-6 text-center space-y-4 animate-in fade-in">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto text-primary">
            <Loader2 size={24} className="animate-spin" />
          </div>
          <div>
            <h4 className="font-semibold text-textMain">Whisper AI Transcribing</h4>
            <p className="text-xs text-textMuted mt-1">Status: <span className="font-mono text-primary capitalize">{transcriptionStatus}</span></p>
            <p className="text-xs text-textMuted mt-2">Converting speech audio into normalized text patterns. Polling progress automatically...</p>
          </div>
        </div>
      )}

      {/* Transcription Failed State */}
      {transcriptionStatus === 'failed' && (
        <div className="w-full max-w-md bg-danger/10 border border-danger/20 rounded-2xl p-6 text-center space-y-4 animate-in fade-in">
          <div className="w-12 h-12 bg-danger/20 rounded-full flex items-center justify-center mx-auto text-danger">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h4 className="font-semibold text-danger">Transcription Failed</h4>
            <p className="text-xs text-textMuted mt-1">Audio could not be transcribed. Please check microphone clarity and try again.</p>
          </div>
          <button 
            onClick={resetAll}
            className="px-6 py-2 bg-surfaceHighlight hover:bg-surfaceHighlight/80 text-textMain rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2 mx-auto"
          >
            <RefreshCw size={14} /> Try Recording Again
          </button>
        </div>
      )}

      {/* Transcription Completed State */}
      {(transcriptionStatus === 'completed' || transcriptionStatus === 'processed') && (
        <div className="w-full max-w-lg bg-surfaceHighlight rounded-2xl p-6 border border-surfaceHighlight space-y-4 animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center justify-between pb-3 border-b border-surfaceHighlight/50">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={18} className="text-success" />
              <span className="font-medium text-textMain text-sm">Transcription Complete</span>
            </div>
            <button 
              onClick={resetAll}
              className="text-xs text-textMuted hover:text-textMain transition-colors"
            >
              New Recording
            </button>
          </div>

          <div>
            <p className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-2">Transcribed Speech</p>
            <div className="bg-background rounded-xl p-4 text-sm text-textMain max-h-48 overflow-y-auto leading-relaxed border border-surfaceHighlight">
              {transcribedText || "No speech detected in recording."}
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button 
              onClick={handleExtractKnowledge}
              disabled={extracting || !transcribedText.trim()}
              className="px-6 py-2.5 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-xl text-sm font-medium transition-colors shadow-lg shadow-primary/25 flex items-center gap-2"
            >
              {extracting ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
              {extracting ? 'Extracting Knowledge...' : 'Extract Knowledge from Speech'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpeechRecorder;
