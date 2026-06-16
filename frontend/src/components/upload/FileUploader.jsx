import React, { useCallback, useState } from 'react';
import { Upload as UploadIcon, File, X, Loader2 } from 'lucide-react';
import api from '../../api/client';
import useStore from '../../store/useStore';
import toast from 'react-hot-toast';

const FileUploader = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const user = useStore(state => state.user);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragging(true);
    else if (e.type === 'dragleave') setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleUpload = async () => {
    if (!file || !user) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', user.id);

    try {
      const res = await api.post('/upload/document', formData);
      toast.success('Document uploaded and processed successfully!');
      
      // Immediately kick off extraction in background
      api.post('/knowledge/extract', { upload_id: res.data.id })
        .then(() => toast.success('Knowledge extracted from document!'))
        .catch(err => console.error(err));
        
      setFile(null);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Document Upload</h3>
      
      {!file ? (
        <div 
          className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center transition-colors cursor-pointer
            ${isDragging ? 'border-primary bg-primary/5' : 'border-surfaceHighlight hover:border-textMuted/50 hover:bg-surfaceHighlight/30'}`}
          onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input type="file" id="file-input" className="hidden" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} />
          <div className="w-16 h-16 bg-surfaceHighlight rounded-full flex items-center justify-center mb-4">
            <UploadIcon className="text-primary" size={28} />
          </div>
          <p className="text-lg font-medium text-textMain mb-1">Click or drag file to this area to upload</p>
          <p className="text-sm text-textMuted">Support for a single PDF, DOCX, or TXT file.</p>
        </div>
      ) : (
        <div className="bg-surfaceHighlight rounded-xl p-4 flex items-center justify-between border border-surfaceHighlight">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-background rounded-lg">
              <File className="text-primary" size={24} />
            </div>
            <div>
              <p className="font-medium text-textMain">{file.name}</p>
              <p className="text-xs text-textMuted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <button onClick={() => setFile(null)} className="p-2 hover:bg-background rounded-lg transition-colors text-textMuted hover:text-danger">
            <X size={20} />
          </button>
        </div>
      )}

      {file && (
        <div className="flex justify-end">
          <button 
            onClick={handleUpload} 
            disabled={uploading}
            className="px-6 py-2.5 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-xl font-medium transition-colors shadow-lg shadow-primary/25 flex items-center gap-2"
          >
            {uploading ? <><Loader2 size={18} className="animate-spin" /> Processing...</> : 'Upload & Process'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
