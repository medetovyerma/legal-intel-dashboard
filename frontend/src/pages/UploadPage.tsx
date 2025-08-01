/**
 * Upload page component
 */
import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { UploadZone } from '../components/Upload/UploadZone';
import { UploadResponse } from '../types/api';

export const UploadPage: React.FC = () => {
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadResult(null);
  };

  const handleUploadComplete = (response: UploadResponse) => {
    setIsUploading(false);
    setUploadResult(response);
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl shadow-2xl float-animation">
              <Upload className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold gradient-text mb-4">Upload Legal Documents</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Transform your legal documents with AI-powered analysis. Upload PDF or DOCX files to extract 
            <span className="text-blue-600 font-semibold"> metadata, identify agreement types</span>, and enable 
            <span className="text-indigo-600 font-semibold"> intelligent search</span> across your entire collection.
          </p>
        </div>

        {/* Upload Zone */}
        <div className="mb-8">
          <UploadZone 
            onUploadStart={handleUploadStart}
            onUploadComplete={handleUploadComplete}
          />
        </div>

        {/* Upload Results */}
        {uploadResult && (
          <div className="mb-8">
            <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Upload Results</h3>
              
              {/* Success Files */}
              {uploadResult.uploaded_files.length > 0 && (
                <div className="mb-6">
                  <div className="flex items-center mb-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    <h4 className="font-medium text-green-800">
                      Successfully Uploaded ({uploadResult.uploaded_files.length})
                    </h4>
                  </div>
                  <div className="space-y-2">
                    {uploadResult.uploaded_files.map((file) => (
                      <div 
                        key={file.id} 
                        className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-green-600" />
                          <div>
                            <p className="font-medium text-green-800">{file.original_filename}</p>
                            <p className="text-sm text-green-600">
                              Status: {file.processing_status} • Size: {(file.file_size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {file.processing_status === 'completed' && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                              Ready for Search
                            </span>
                          )}
                          {file.processing_status === 'processing' && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                              Processing...
                            </span>
                          )}
                          {file.processing_status === 'pending' && (
                            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full font-medium">
                              Pending
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Failed Files */}
              {uploadResult.failed_files.length > 0 && (
                <div>
                  <div className="flex items-center mb-3">
                    <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                    <h4 className="font-medium text-red-800">
                      Failed to Upload ({uploadResult.failed_files.length})
                    </h4>
                  </div>
                  <div className="space-y-2">
                    {uploadResult.failed_files.map((failure, index) => (
                      <div 
                        key={index} 
                        className="p-3 bg-red-50 border border-red-200 rounded-lg"
                      >
                        <div className="flex items-start space-x-3">
                          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                          <div>
                            <p className="font-medium text-red-800">{failure.filename}</p>
                            <p className="text-sm text-red-600">{failure.error}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Information Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <div className="card hover-lift p-8">
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="ml-4 text-xl font-bold text-gray-800">Supported Formats</h3>
            </div>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>PDF documents (.pdf)</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                <span>Word documents (.docx)</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Maximum file size: 50MB</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
                <span>Multiple files supported</span>
              </li>
            </ul>
          </div>

          <div className="card hover-lift p-8">
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-br from-green-100 to-emerald-200 rounded-xl">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="ml-4 text-xl font-bold text-gray-800">Smart Features</h3>
            </div>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Automatic text extraction</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <span>Intelligent document analysis</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                <span>Natural language search</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-cyan-500 rounded-full"></div>
                <span>Real-time processing</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Next Steps */}
        {uploadResult && uploadResult.uploaded_files.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">What's Next?</h3>
            <p className="text-blue-700 mb-4">
              Your documents are being processed in the background. Once processing is complete, you can:
            </p>
            <div className="flex flex-wrap gap-3">
              <a 
                href="/query" 
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Ask Questions
              </a>
              <a 
                href="/dashboard" 
                className="inline-flex items-center px-4 py-2 bg-white text-blue-600 border border-blue-300 rounded-md hover:bg-blue-50 transition-colors"
              >
                View Dashboard
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};