/**
 * Dashboard page component with beautiful design
 */
import React from 'react';
import { BarChart3, TrendingUp } from 'lucide-react';
import { DashboardView } from '../components/Dashboard/DashboardView';

export const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Beautiful Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="p-4 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-3xl shadow-2xl float-animation">
              <BarChart3 className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold gradient-text mb-4">Analytics Dashboard</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Comprehensive insights into your 
            <span className="text-purple-600 font-semibold"> legal document collection</span> with 
            <span className="text-indigo-600 font-semibold"> real-time processing statistics</span> and 
            intelligent analytics.
          </p>
        </div>

        {/* Dashboard Content */}
        <DashboardView />
      </div>
    </div>
  );
};