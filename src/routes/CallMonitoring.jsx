import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Phone, 
  Search, 
  Filter,
  Download,
  Play,
  Pause,
  Volume2,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye
} from 'lucide-react';

const CallMonitoring = () => {
  const [calls, setCalls] = useState([]);
  const [filteredCalls, setFilteredCalls] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [intentFilter, setIntentFilter] = useState('all');

  useEffect(() => {
    // Mock call data
    const mockCalls = [
      {
        id: 1,
        sessionId: 'sess_001',
        caller: 'John Smith',
        phone: '(555) 123-4567',
        email: 'john@email.com',
        intent: 'appointment_booking',
        status: 'completed',
        duration: 180,
        startTime: '2025-01-30 14:30:00',
        endTime: '2025-01-30 14:33:00',
        appointmentBooked: true,
        leadQualified: true,
        summary: 'Customer booked a consultation appointment for next Tuesday at 2 PM.'
      },
      {
        id: 2,
        sessionId: 'sess_002',
        caller: 'Sarah Johnson',
        phone: '(555) 987-6543',
        email: 'sarah@email.com',
        intent: 'business_hours',
        status: 'completed',
        duration: 45,
        startTime: '2025-01-30 14:15:00',
        endTime: '2025-01-30 14:15:45',
        appointmentBooked: false,
        leadQualified: false,
        summary: 'Customer inquired about business hours and location.'
      },
      {
        id: 3,
        sessionId: 'sess_003',
        caller: 'Mike Wilson',
        phone: '(555) 456-7890',
        email: null,
        intent: 'services',
        status: 'completed',
        duration: 120,
        startTime: '2025-01-30 13:45:00',
        endTime: '2025-01-30 13:47:00',
        appointmentBooked: false,
        leadQualified: true,
        summary: 'Customer asked about available services and pricing.'
      },
      {
        id: 4,
        sessionId: 'sess_004',
        caller: 'Emily Davis',
        phone: '(555) 321-0987',
        email: 'emily@email.com',
        intent: 'appointment_cancel',
        status: 'completed',
        duration: 90,
        startTime: '2025-01-30 13:30:00',
        endTime: '2025-01-30 13:31:30',
        appointmentBooked: false,
        leadQualified: false,
        summary: 'Customer cancelled their existing appointment.'
      },
      {
        id: 5,
        sessionId: 'sess_005',
        caller: 'Unknown Caller',
        phone: '(555) 111-2222',
        email: null,
        intent: 'unknown',
        status: 'failed',
        duration: 15,
        startTime: '2025-01-30 13:00:00',
        endTime: '2025-01-30 13:00:15',
        appointmentBooked: false,
        leadQualified: false,
        summary: 'Call ended abruptly, possible technical issue.'
      }
    ];

    setCalls(mockCalls);
    setFilteredCalls(mockCalls);
  }, []);

  useEffect(() => {
    let filtered = calls;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(call => 
        call.caller.toLowerCase().includes(searchTerm.toLowerCase()) ||
        call.phone.includes(searchTerm) ||
        (call.email && call.email.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(call => call.status === statusFilter);
    }

    // Filter by intent
    if (intentFilter !== 'all') {
      filtered = filtered.filter(call => call.intent === intentFilter);
    }

    setFilteredCalls(filtered);
  }, [calls, searchTerm, statusFilter, intentFilter]);

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

  const getIntentBadge = (intent) => {
    const intentColors = {
      appointment_booking: 'bg-green-100 text-green-800',
      appointment_cancel: 'bg-red-100 text-red-800',
      business_hours: 'bg-blue-100 text-blue-800',
      services: 'bg-purple-100 text-purple-800',
      pricing: 'bg-yellow-100 text-yellow-800',
      contact: 'bg-gray-100 text-gray-800',
      unknown: 'bg-gray-100 text-gray-800'
    };

    return (
      <Badge className={intentColors[intent] || 'bg-gray-100 text-gray-800'}>
        {intent.replace('_', ' ')}
      </Badge>
    );
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString();
  };

  const exportCalls = () => {
    // Mock export functionality
    console.log('Exporting calls data...');
    alert('Call data exported successfully!');
  };

  return (
    <div className="call-monitoring-container p-6">
      <div className="header mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Call Monitoring</h1>
        <p className="text-gray-600 mt-2">Monitor and analyze all AI receptionist calls</p>
      </div>

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by name, phone, or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>

            <Select value={intentFilter} onValueChange={setIntentFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by intent" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Intents</SelectItem>
                <SelectItem value="appointment_booking">Appointment Booking</SelectItem>
                <SelectItem value="appointment_cancel">Appointment Cancel</SelectItem>
                <SelectItem value="business_hours">Business Hours</SelectItem>
                <SelectItem value="services">Services</SelectItem>
                <SelectItem value="pricing">Pricing</SelectItem>
                <SelectItem value="contact">Contact</SelectItem>
                <SelectItem value="unknown">Unknown</SelectItem>
              </SelectContent>
            </Select>

            <Button onClick={exportCalls} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Calls List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Calls ({filteredCalls.length})</CardTitle>
          <CardDescription>Detailed view of all AI receptionist interactions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredCalls.map((call) => (
              <div key={call.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    {getStatusIcon(call.status)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-lg">{call.caller}</h3>
                        {call.appointmentBooked && (
                          <Badge className="bg-green-100 text-green-800">Appointment Booked</Badge>
                        )}
                        {call.leadQualified && (
                          <Badge className="bg-blue-100 text-blue-800">Lead Qualified</Badge>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600 mb-2">
                        <div>📞 {call.phone}</div>
                        {call.email && <div>✉️ {call.email}</div>}
                        <div>🕒 {formatDateTime(call.startTime)}</div>
                        <div>⏱️ Duration: {formatDuration(call.duration)}</div>
                      </div>
                      
                      <p className="text-sm text-gray-700 mb-2">{call.summary}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {getIntentBadge(call.intent)}
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {filteredCalls.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Phone className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No calls found matching your criteria.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CallMonitoring;

