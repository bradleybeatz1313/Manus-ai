import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Phone, 
  Calendar, 
  Users, 
  Settings, 
  MessageSquare, 
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalCalls: 0,
    appointmentsBooked: 0,
    leadsGenerated: 0,
    averageCallDuration: 0
  });

  const [recentCalls, setRecentCalls] = useState([]);
  const [callData, setCallData] = useState([]);

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data for demonstration
      setStats({
        totalCalls: 127,
        appointmentsBooked: 34,
        leadsGenerated: 89,
        averageCallDuration: 185
      });

      setRecentCalls([
        {
          id: 1,
          caller: 'John Smith',
          phone: '(555) 123-4567',
          intent: 'appointment_booking',
          status: 'completed',
          duration: 180,
          timestamp: '2025-01-30 14:30:00'
        },
        {
          id: 2,
          caller: 'Sarah Johnson',
          phone: '(555) 987-6543',
          intent: 'business_hours',
          status: 'completed',
          duration: 45,
          timestamp: '2025-01-30 14:15:00'
        },
        {
          id: 3,
          caller: 'Mike Wilson',
          phone: '(555) 456-7890',
          intent: 'services',
          status: 'completed',
          duration: 120,
          timestamp: '2025-01-30 13:45:00'
        }
      ]);

      setCallData([
        { date: '2025-01-24', calls: 12, appointments: 3 },
        { date: '2025-01-25', calls: 19, appointments: 5 },
        { date: '2025-01-26', calls: 15, appointments: 4 },
        { date: '2025-01-27', calls: 22, appointments: 7 },
        { date: '2025-01-28', calls: 18, appointments: 6 },
        { date: '2025-01-29', calls: 25, appointments: 8 },
        { date: '2025-01-30', calls: 16, appointments: 1 }
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const getIntentBadge = (intent) => {
    const intentColors = {
      appointment_booking: 'bg-green-100 text-green-800',
      business_hours: 'bg-blue-100 text-blue-800',
      services: 'bg-purple-100 text-purple-800',
      pricing: 'bg-yellow-100 text-yellow-800',
      contact: 'bg-gray-100 text-gray-800'
    };

    return (
      <Badge className={intentColors[intent] || 'bg-gray-100 text-gray-800'}>
        {intent.replace('_', ' ')}
      </Badge>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'active':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="text-3xl font-bold text-gray-900">AI Voice Receptionist Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor your AI receptionist performance and manage your business</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <Card className="stat-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCalls}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last week
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Appointments Booked</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.appointmentsBooked}</div>
            <p className="text-xs text-muted-foreground">
              +8% from last week
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Leads Generated</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.leadsGenerated}</div>
            <p className="text-xs text-muted-foreground">
              +15% from last week
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Call Duration</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatDuration(stats.averageCallDuration)}</div>
            <p className="text-xs text-muted-foreground">
              -5% from last week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="chart-section">
          <Card>
            <CardHeader>
              <CardTitle>Call Analytics</CardTitle>
              <CardDescription>Daily call volume and appointment bookings</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={callData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="calls" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Total Calls"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="appointments" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Appointments"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <div className="recent-calls-section">
          <Card>
            <CardHeader>
              <CardTitle>Recent Calls</CardTitle>
              <CardDescription>Latest interactions with your AI receptionist</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentCalls.map((call) => (
                  <div key={call.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(call.status)}
                      <div>
                        <p className="font-medium">{call.caller}</p>
                        <p className="text-sm text-gray-500">{call.phone}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {getIntentBadge(call.intent)}
                      <div className="text-right">
                        <p className="text-sm font-medium">{formatDuration(call.duration)}</p>
                        <p className="text-xs text-gray-500">{new Date(call.timestamp).toLocaleTimeString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

