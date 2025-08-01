/**
 * Drag and drop upload zone component
 */
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService } from '../../services/api';
import { UploadResponse } from '../../types/api';
import toast from 'react-hot-toast';

interface UploadZoneProps {
  onUploadComplete?: (response: UploadResponse) => void;
  onUploadStart?: () => void;
}

interface FileWithPreview extends File {
  preview?: string;
  id: string;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onUploadComplete,
  onUploadStart,
}) => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const filesWithId = acceptedFiles.map((file) => {
      // Ensure file has required properties
      const fileWithId = Object.assign(file, {
        id: Math.random().toString(36).substr(2, 9),
        preview: URL.createObjectURL(file),
      });
      
      console.log('File added:', {
        name: file.name,
        type: file.type,
        size: file.size,
        id: fileWithId.id
      });
      
      return fileWithId;
    });
    
    setFiles((prev) => [...prev, ...filesWithId]);
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
  });

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    console.log('Starting upload for files:', files.map(f => ({ name: f.name, size: f.size, type: f.type })));

    setUploading(true);
    onUploadStart?.();

    try {
      // Validate files before upload
      const invalidFiles = files.filter(file => {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const fileName = file.name || '';
        const fileType = file.type || '';
        
        // Check by MIME type or file extension
        const isValidType = validTypes.includes(fileType);
        const isValidExtension = fileName.toLowerCase().endsWith('.pdf') || fileName.toLowerCase().endsWith('.docx');
        
        return !isValidType && !isValidExtension;
      });

      if (invalidFiles.length > 0) {
        toast.error(`Invalid file types: ${invalidFiles.map(f => f.name).join(', ')}`);
        setUploading(false);
        return;
      }

      // Simulate progress for UI feedback
      files.forEach((file) => {
        setUploadProgress((prev) => ({ ...prev, [file.id]: 0 }));
      });

      // Start progress simulation
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          const newProgress = { ...prev };
          files.forEach((file) => {
            if (newProgress[file.id] < 90) {
              newProgress[file.id] = Math.min(90, newProgress[file.id] + Math.random() * 20);
            }
          });
          return newProgress;
        });
      }, 500);

      // Convert to File objects if needed and validate
      const fileObjects = files.map((f, index) => {
        console.log(`Processing file ${index}:`, {
          name: f.name,
          type: f.type,
          size: f.size,
          constructor: f.constructor.name
        });

        // If it's already a File object, return it
        if (f instanceof File) {
          return f;
        }
        
        // If it's a FileWithPreview, we need to create a proper File object
        // This shouldn't happen with react-dropzone, but let's be safe
        try {
          return new File([f], f.name || 'unknown', { 
            type: f.type || 'application/octet-stream' 
          });
        } catch (error) {
          console.error('Error creating File object:', error);
          throw new Error(`Invalid file at index ${index}: ${f.name || 'unknown'}`);
        }
      });

      console.log('Final file objects for upload:', fileObjects.map(f => ({
        name: f.name,
        type: f.type,
        size: f.size
      })));
      const response = await apiService.uploadDocuments(fileObjects);

      // Complete progress
      clearInterval(progressInterval);
      files.forEach((file) => {
        setUploadProgress((prev) => ({ ...prev, [file.id]: 100 }));
      });

      console.log('Upload response:', response);

      // Show results
      if (response.uploaded_files.length > 0) {
        toast.success(`Successfully uploaded ${response.uploaded_files.length} files`);
      }
      
      if (response.failed_files.length > 0) {
        response.failed_files.forEach((failure) => {
          toast.error(`Failed to upload ${failure.filename}: ${failure.error}`);
        });
      }

      onUploadComplete?.(response);
      
      // Clear files after successful upload
      setTimeout(() => {
        setFiles([]);
        setUploadProgress({});
      }, 2000);

    } catch (error: any) {
      console.error('Upload error:', error);
      
      // Clear progress interval
      files.forEach((file) => {
        setUploadProgress((prev) => ({ ...prev, [file.id]: 0 }));
      });

      const errorMessage = error.message || error.response?.data?.detail || 'Upload failed';
      toast.error(errorMessage);
      
      // Log detailed error for debugging
      if (error.response) {
        console.error('Error response:', error.response.data);
        console.error('Error status:', error.response.status);
      }
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive && !isDragReject 
            ? 'border-blue-400 bg-gradient-to-br from-blue-100 to-indigo-100 shadow-xl ring-4 ring-blue-200/50' 
            : isDragReject 
            ? 'border-red-400 bg-gradient-to-br from-red-50 to-pink-50 shadow-lg' 
            : 'border-blue-300 bg-gradient-to-br from-blue-50 to-indigo-50 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-100 hover:to-indigo-100 hover:shadow-lg'
          }
          ${uploading ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-6">
          <div className={`p-4 rounded-full transition-all duration-300 ${
            isDragActive 
              ? 'bg-gradient-to-br from-blue-500 to-indigo-500 shadow-xl transform scale-110' 
              : 'bg-gradient-to-br from-blue-400 to-indigo-400 shadow-lg hover:shadow-xl hover:scale-105'
          }`}>
            <Upload 
              className="w-16 h-16 text-white" 
            />
          </div>
          
          <div className="space-y-4">
            <h3 className={`text-2xl font-bold transition-colors duration-300 ${
              isDragActive 
                ? 'text-blue-700' 
                : isDragReject 
                  ? 'text-red-600' 
                  : 'text-gray-800'
            }`}>
              {isDragActive 
                ? isDragReject 
                  ? 'Invalid file type!' 
                  : 'Drop your files here!'
                : 'Upload Legal Documents'
              }
            </h3>
            <p className="text-lg text-gray-600 max-w-md mx-auto">
              Drag & drop your PDF or DOCX files here, or{' '}
              <span className="text-blue-600 font-semibold">click to browse</span>
            </p>
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>PDF & DOCX supported</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Up to 50MB each</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span>AI-powered analysis</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-8 space-y-4">
          <div className="flex items-center space-x-3">
            <h3 className="text-xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
              Selected Files
            </h3>
            <div className="px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm font-medium rounded-full shadow-lg">
              {files.length}
            </div>
          </div>
          
          <div className="grid gap-4">
            {files.map((file) => (
              <div
                key={file.id}
                className="card hover-lift p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl">
                    <FileText className="w-8 h-8 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800 truncate max-w-xs">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {/* Progress Bar */}
                  {uploading && uploadProgress[file.id] !== undefined && (
                    <div className="w-32">
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                          className="h-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300 shadow-sm"
                          style={{ width: `${uploadProgress[file.id]}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-center font-medium">
                        {Math.round(uploadProgress[file.id])}%
                      </p>
                    </div>
                  )}

                  {/* Status Icon */}
                  {uploadProgress[file.id] === 100 ? (
                    <div className="p-2 bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg">
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    </div>
                  ) : uploading ? (
                    <div className="p-2 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg">
                      <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : (
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-2 bg-gradient-to-br from-red-100 to-pink-100 hover:from-red-200 hover:to-pink-200 rounded-lg transition-all duration-200 group"
                      disabled={uploading}
                    >
                      <AlertCircle className="w-6 h-6 text-red-500 group-hover:text-red-600" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <div className="flex justify-center pt-6">
            <button
              onClick={uploadFiles}
              disabled={uploading || files.length === 0}
              className={`
                btn-primary text-lg px-8 py-4 rounded-2xl font-semibold
                ${uploading 
                  ? 'opacity-60 cursor-not-allowed transform-none shadow-lg' 
                  : 'hover:shadow-2xl'
                } 
                transition-all duration-300
              `}
            >
              {uploading ? (
                <div className="flex items-center space-x-3">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Processing Magic...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Upload className="w-5 h-5" />
                  <span>Upload {files.length} File{files.length > 1 ? 's' : ''}</span>
                </div>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};