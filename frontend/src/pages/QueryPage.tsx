/**
 * Query page component for natural language document search
 */
import React, { useState } from 'react';
import { Search, MessageSquare, FileText } from 'lucide-react';
import { QueryInput } from '../components/Query/QueryInput';
import { ResultsTable } from '../components/Query/ResultsTable';
import { QueryResponse } from '../types/api';

export const QueryPage: React.FC = () => {
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [isQuerying, setIsQuerying] = useState(false);

  const handleQueryStart = () => {
    setIsQuerying(true);
  };

  const handleQueryResult = (result: QueryResponse) => {
    setIsQuerying(false);
    setQueryResponse(result);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-primary-100 rounded-full">
              <Search className="w-8 h-8 text-primary-600" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Query Your Documents</h1>
          <p className="mt-2 text-gray-600 max-w-2xl mx-auto">
            Ask questions about your legal documents in natural language. 
            Our AI will search across all your uploaded documents and provide structured answers.
          </p>
        </div>

        {/* Query Input */}
        <div className="mb-8">
          <QueryInput 
            onQueryStart={handleQueryStart}
            onQueryResult={handleQueryResult}
          />
        </div>

        {/* Results */}
        <div className="mb-8">
          <ResultsTable queryResponse={queryResponse} />
        </div>

        {/* Help Section */}
        {!queryResponse && !isQuerying && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Query Examples */}
            <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div className="flex items-center mb-4">
                <MessageSquare className="w-6 h-6 text-primary-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-800">Example Queries</h3>
              </div>
              <div className="space-y-3">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-700 mb-1">Filter by jurisdiction:</p>
                  <p className="text-sm text-gray-600">"Which agreements are governed by UAE law?"</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-700 mb-1">Find by agreement type:</p>
                  <p className="text-sm text-gray-600">"Show all NDAs and confidentiality agreements"</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-700 mb-1">Industry analysis:</p>
                  <p className="text-sm text-gray-600">"What industries are covered in our contracts?"</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-700 mb-1">Geographic search:</p>
                  <p className="text-sm text-gray-600">"Find contracts mentioning Middle East or Europe"</p>
                </div>
              </div>
            </div>

            {/* Query Tips */}
          </div>
        )}

        {/* Search Stats */}
        {queryResponse && (
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Search Analytics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-1">
                  {queryResponse.total_matches}
                </div>
                <div className="text-sm text-gray-600">Documents Found</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {Object.keys(queryResponse.results[0]?.data || {}).length}
                </div>
                <div className="text-sm text-gray-600">Data Fields</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 mb-1">
                  {queryResponse.question.split(' ').length}
                </div>
                <div className="text-sm text-gray-600">Query Terms</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};