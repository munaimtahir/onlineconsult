import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ConsultList from '../components/ConsultList';

type TabType = 'incoming' | 'outgoing' | 'new';

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('incoming');
  const { username, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNewConsult = () => {
    navigate('/consults/new');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Hospital Consult System</h1>
              <p className="text-sm text-gray-600 mt-1">Welcome, {username}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('incoming')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'incoming'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Incoming Consults
              </button>
              <button
                onClick={() => setActiveTab('outgoing')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'outgoing'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Outgoing Consults
              </button>
              <div className="flex-1"></div>
              <button
                onClick={handleNewConsult}
                className="m-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
              >
                + New Consult
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'incoming' && <ConsultList role="incoming" />}
            {activeTab === 'outgoing' && <ConsultList role="outgoing" />}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
