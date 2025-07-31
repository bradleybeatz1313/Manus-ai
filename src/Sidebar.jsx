import React from 'react';
import { Button } from '@/components/ui/button';
import { 
  LayoutDashboard, 
  Phone, 
  Calendar, 
  Users, 
  Settings, 
  MessageSquare,
  BarChart3,
  Headphones
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'calls', label: 'Call Monitoring', icon: Phone },
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'chat', label: 'Test Chat', icon: MessageSquare },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="flex items-center space-x-2">
          <Headphones className="h-8 w-8 text-blue-600" />
          <h2 className="text-xl font-bold text-gray-900">AI Voice</h2>
        </div>
        <p className="text-sm text-gray-500 mt-1">Receptionist</p>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Button>
          );
        })}
      </nav>
      
      <div className="sidebar-footer">
        <div className="status-indicator">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">AI Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

