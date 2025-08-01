/**
 * Natural language query input component
 */
import React, { useState } from 'react';
import { Search, Send, Loader2, HelpCircle } from 'lucide-react';
import { apiService } from '../../services/api';
import { QueryResponse } from '../../types/api';
import toast from 'react-hot-toast';

interface QueryInputProps {
  onQueryResult?: (result: QueryResponse) => void;
  onQueryStart?: () => void;
}

const EXAMPLE_QUERIES = [
  "Which agreements are governed by UAE law?",
  "Show all NDAs",
  "What industries are covered in our documents?",
  "List contracts mentioning technology sector",
  "Find agreements with governing law in Europe",
  "Show all Master Service Agreements",
];

export const QueryInput: React.FC<QueryInputProps> = ({
  onQueryResult,
  onQueryStart,
}) => {
  const [question, setQuestion] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [showExamples, setShowExamples] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    if (question.trim().length < 3) {
      toast.error('Question must be at least 3 characters long');
      return;
    }

    setIsQuerying(true);
    onQueryStart?.();

    try {
      const result = await apiService.queryDocuments(question.trim());
      
      if (result.total_matches === 0) {
        toast.info('No documents match your query');
      } else {
        toast.success(`Found ${result.total_matches} matching document${result.total_matches > 1 ? 's' : ''}`);
      }
      
      onQueryResult?.(result);
      
    } catch (error: any) {
      toast.error(error.message || 'Query failed');
      console.error('Query error:', error);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuestion(example);
    setShowExamples(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Query Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your legal documents..."
            className="
              block w-full pl-10 pr-24 py-4 text-lg
              border border-gray-300 rounded-lg
              focus:ring-2 focus:ring-primary-500 focus:border-primary-500
              placeholder-gray-500 bg-white shadow-sm
              transition-all duration-200
            "
            disabled={isQuerying}
            maxLength={500}
          />
          
          <div className="absolute inset-y-0 right-0 flex items-center">
            <button
              type="button"
              onClick={() => setShowExamples(!showExamples)}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors mr-2"
              title="Show example queries"
            >
              <HelpCircle className="h-5 w-5" />
            </button>
            
            <button
              type="submit"
              disabled={isQuerying || !question.trim()}
              className={`
                mr-2 p-2 rounded-md transition-all duration-200
                ${isQuerying || !question.trim()
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-primary-600 hover:text-primary-700 hover:bg-primary-50'
                }
              `}
            >
              {isQuerying ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
        
        {/* Character Counter */}
        <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
          <p>
            Tip: Use Cmd/Ctrl + Enter to submit
          </p>
          <p>
            {question.length}/500 characters
          </p>
        </div>
      </form>

      {/* Example Queries */}
      {showExamples && (
        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Example Questions:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="
                  text-left p-2 text-sm text-gray-600 
                  hover:text-primary-600 hover:bg-white 
                  rounded border border-transparent hover:border-primary-200
                  transition-all duration-200
                "
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Query Status */}
      {isQuerying && (
        <div className="mt-4 flex items-center justify-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600 mr-3" />
          <span className="text-blue-700">
            Analyzing your question across all documents...
          </span>
        </div>
      )}
    </div>
  );
};