import React, { useState, useRef } from 'react';
import { Mic, Square, Loader2, Play, AudioLines } from 'lucide-react';
import api from '../../api/client';
import useStore from '../../store/useStore';
import toast from 'react-hot-toast';

const SpeechRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [uploading, setUploading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const user = useStore(state => state.user);

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
    } catch (err) {
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
      toast.success('Audio queued for Whisper transcription!');
      // Since it's background processed, we just reset
      setAudioBlob(null);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 flex flex-col items-center justify-center py-8">
      <div className="text-center">
        <h3 className="text-xl font-medium mb-2">Speech to Knowledge</h3>
        <p className="text-sm text-textMuted max-w-md mx-auto">
          Speak naturally about an experience or historical practice. Local Whisper AI will transcribe and extract the patterns.
        </p>
      </div>

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
          {isRecording ? <span className="text-danger flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-danger animate-pulse"></span> Recording...</span> : 'Tap to Record'}
        </p>
      </div>

      {audioBlob && !isRecording && (
        <div className="w-full max-w-md bg-surfaceHighlight rounded-xl p-4 border border-surfaceHighlight animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-2 bg-background rounded-lg">
              <AudioLines className="text-primary" size={20} />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">Recording ready</p>
              <p className="text-xs text-textMuted">{(audioBlob.size / 1024).toFixed(1)} KB</p>
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
    </div>
  );
};

export default SpeechRecorder;
