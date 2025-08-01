/**
 * Dynamic results table component for query responses
 */
import React, { useState } from 'react';
import { FileText, Download, Eye, Filter } from 'lucide-react';
import { QueryResponse, QueryResult } from '../../types/api';

interface ResultsTableProps {
  queryResponse: QueryResponse | null;
  className?: string;
}

export const ResultsTable: React.FC<ResultsTableProps> = ({
  queryResponse,
  className = '',
}) => {
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [filterValue, setFilterValue] = useState('');

  if (!queryResponse || queryResponse.results.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        {queryResponse ? (
          <div className="space-y-3">
            <FileText className="w-16 h-16 text-gray-300 mx-auto" />
            <h3 className="text-lg font-medium text-gray-600">No Results Found</h3>
            <p className="text-gray-500">
              No documents match your query: "<em>{queryResponse.question}</em>"
            </p>
            <p className="text-sm text-gray-400">
              Try rephrasing your question or using different keywords
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <FileText className="w-16 h-16 text-gray-300 mx-auto" />
            <h3 className="text-lg font-medium text-gray-600">Ask a Question</h3>
            <p className="text-gray-500">
              Use natural language to search across your documents
            </p>
          </div>
        )}
      </div>
    );
  }

  // Get all unique column keys from results
  const allColumns = new Set<string>();
  queryResponse.results.forEach((result) => {
    Object.keys(result.data).forEach((key) => allColumns.add(key));
  });
  const columns = ['document', ...Array.from(allColumns)];

  // Filter and sort results
  let filteredResults = queryResponse.results;
  
  if (filterValue) {
    filteredResults = filteredResults.filter((result) => {
      const searchText = [
        result.document,
        ...Object.values(result.data).map(String)
      ].join(' ').toLowerCase();
      return searchText.includes(filterValue.toLowerCase());
    });
  }

  if (sortField) {
    filteredResults = [...filteredResults].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (sortField === 'document') {
        aValue = a.document;
        bValue = b.document;
      } else {
        aValue = a.data[sortField] || '';
        bValue = b.data[sortField] || '';
      }

      // Convert to strings for consistent sorting
      aValue = String(aValue).toLowerCase();
      bValue = String(bValue).toLowerCase();

      if (sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    });
  }

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const formatColumnName = (column: string) => {
    return column
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const exportToCSV = () => {
    const headers = columns.map(formatColumnName);
    const rows = filteredResults.map((result) => 
      columns.map((col) => {
        if (col === 'document') return result.document;
        return result.data[col] || '';
      })
    );

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query-results-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Query Results</h3>
            <p className="text-sm text-gray-600 mt-1">
              Found {queryResponse.total_matches} document{queryResponse.total_matches !== 1 ? 's' : ''} for: 
              <span className="font-medium italic"> "{queryResponse.question}"</span>
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={exportToCSV}
              className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        {/* Filter */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            value={filterValue}
            onChange={(e) => setFilterValue(e.target.value)}
            placeholder="Filter results..."
            className="
              block w-full pl-10 pr-3 py-2 text-sm
              border border-gray-300 rounded-md
              focus:ring-1 focus:ring-primary-500 focus:border-primary-500
              placeholder-gray-400
            "
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  onClick={() => handleSort(column)}
                  className="
                    px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider
                    cursor-pointer hover:bg-gray-100 transition-colors
                    select-none
                  "
                >
                  <div className="flex items-center space-x-1">
                    <span>{formatColumnName(column)}</span>
                    {sortField === column && (
                      <span className="text-primary-600">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredResults.map((result, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                {columns.map((column) => (
                  <td key={column} className="px-6 py-4 whitespace-nowrap text-sm">
                    {column === 'document' ? (
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span className="font-medium text-gray-900 max-w-xs truncate">
                          {result.document}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-700">
                        {result.data[column] || '—'}
                      </span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      {filteredResults.length !== queryResponse.total_matches && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
          Showing {filteredResults.length} of {queryResponse.total_matches} results
        </div>
      )}
    </div>
  );
};