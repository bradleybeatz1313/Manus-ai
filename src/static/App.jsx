import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import CallMonitoring from './components/CallMonitoring';
import AppointmentManager from './components/AppointmentManager';
import ChatTester from './components/ChatTester';
import Settings from './components/Settings';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'calls':
        return <CallMonitoring />;
      case 'appointments':
        return <AppointmentManager />;
      case 'chat':
        return <ChatTester />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <div className="app-sidebar">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
      <div className="app-content">
        {renderContent()}
      </div>
    </div>
  );
}

export default App;
