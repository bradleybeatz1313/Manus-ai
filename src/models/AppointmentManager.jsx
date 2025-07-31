import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Calendar, 
  Clock, 
  User, 
  Phone, 
  Mail, 
  Search,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const AppointmentManager = () => {
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  useEffect(() => {
    // Mock appointment data
    const mockAppointments = [
      {
        id: 1,
        customerName: 'John Smith',
        customerPhone: '(555) 123-4567',
        customerEmail: 'john@email.com',
        serviceType: 'Consultation',
        appointmentDate: '2025-02-03',
        appointmentTime: '14:00',
        duration: 60,
        status: 'scheduled',
        notes: 'First-time customer, interested in our premium package.',
        specialRequests: 'Prefers afternoon appointments',
        createdAt: '2025-01-30 14:30:00'
      },
      {
        id: 2,
        customerName: 'Sarah Johnson',
        customerPhone: '(555) 987-6543',
        customerEmail: 'sarah@email.com',
        serviceType: 'Follow-up',
        appointmentDate: '2025-02-04',
        appointmentTime: '10:30',
        duration: 30,
        status: 'confirmed',
        notes: 'Follow-up appointment for previous consultation.',
        specialRequests: null,
        createdAt: '2025-01-29 16:15:00'
      },
      {
        id: 3,
        customerName: 'Mike Wilson',
        customerPhone: '(555) 456-7890',
        customerEmail: 'mike@email.com',
        serviceType: 'Treatment',
        appointmentDate: '2025-02-05',
        appointmentTime: '15:30',
        duration: 90,
        status: 'scheduled',
        notes: 'Requires extended session.',
        specialRequests: 'Wheelchair accessible',
        createdAt: '2025-01-30 13:45:00'
      },
      {
        id: 4,
        customerName: 'Emily Davis',
        customerPhone: '(555) 321-0987',
        customerEmail: 'emily@email.com',
        serviceType: 'Consultation',
        appointmentDate: '2025-01-31',
        appointmentTime: '11:00',
        duration: 60,
        status: 'cancelled',
        notes: 'Customer cancelled due to scheduling conflict.',
        specialRequests: null,
        createdAt: '2025-01-28 09:20:00'
      },
      {
        id: 5,
        customerName: 'Robert Brown',
        customerPhone: '(555) 555-1234',
        customerEmail: 'robert@email.com',
        serviceType: 'Treatment',
        appointmentDate: '2025-01-30',
        appointmentTime: '16:00',
        duration: 60,
        status: 'completed',
        notes: 'Successful treatment session.',
        specialRequests: null,
        createdAt: '2025-01-29 14:10:00'
      }
    ];

    setAppointments(mockAppointments);
    setFilteredAppointments(mockAppointments);
  }, []);

  useEffect(() => {
    let filtered = appointments;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(appointment => 
        appointment.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        appointment.customerPhone.includes(searchTerm) ||
        appointment.customerEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
        appointment.serviceType.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(appointment => appointment.status === statusFilter);
    }

    setFilteredAppointments(filtered);
  }, [appointments, searchTerm, statusFilter]);

  const getStatusBadge = (status) => {
    const statusConfig = {
      scheduled: { color: 'bg-blue-100 text-blue-800', icon: Clock },
      confirmed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle },
      completed: { color: 'bg-gray-100 text-gray-800', icon: CheckCircle }
    };

    const config = statusConfig[status] || statusConfig.scheduled;
    const Icon = config.icon;

    return (
      <Badge className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const updateAppointmentStatus = (appointmentId, newStatus) => {
    setAppointments(prev => 
      prev.map(appointment => 
        appointment.id === appointmentId 
          ? { ...appointment, status: newStatus }
          : appointment
      )
    );
  };

  const handleEditAppointment = (appointment) => {
    setSelectedAppointment(appointment);
    setIsEditDialogOpen(true);
  };

  const saveAppointmentChanges = () => {
    if (selectedAppointment) {
      setAppointments(prev => 
        prev.map(appointment => 
          appointment.id === selectedAppointment.id 
            ? selectedAppointment
            : appointment
        )
      );
      setIsEditDialogOpen(false);
      setSelectedAppointment(null);
    }
  };

  const getUpcomingAppointments = () => {
    const today = new Date();
    return appointments.filter(appointment => {
      const appointmentDate = new Date(appointment.appointmentDate);
      return appointmentDate >= today && appointment.status !== 'cancelled';
    }).length;
  };

  const getTodayAppointments = () => {
    const today = new Date().toISOString().split('T')[0];
    return appointments.filter(appointment => 
      appointment.appointmentDate === today && appointment.status !== 'cancelled'
    ).length;
  };

  return (
    <div className="appointment-manager-container p-6">
      <div className="header mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Appointment Management</h1>
        <p className="text-gray-600 mt-2">Manage and track all customer appointments</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today's Appointments</p>
                <p className="text-2xl font-bold">{getTodayAppointments()}</p>
              </div>
              <Calendar className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Upcoming Appointments</p>
                <p className="text-2xl font-bold">{getUpcomingAppointments()}</p>
              </div>
              <Clock className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Appointments</p>
                <p className="text-2xl font-bold">{appointments.length}</p>
              </div>
              <User className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
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
                  placeholder="Search appointments..."
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
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="confirmed">Confirmed</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>

            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Appointment
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Appointments List */}
      <Card>
        <CardHeader>
          <CardTitle>Appointments ({filteredAppointments.length})</CardTitle>
          <CardDescription>Manage all customer appointments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredAppointments.map((appointment) => (
              <div key={appointment.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-lg">{appointment.customerName}</h3>
                      {getStatusBadge(appointment.status)}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center space-x-2">
                        <Phone className="h-4 w-4" />
                        <span>{appointment.customerPhone}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4" />
                        <span>{appointment.customerEmail}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(appointment.appointmentDate)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4" />
                        <span>{formatTime(appointment.appointmentTime)} ({appointment.duration} min)</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4" />
                        <span>{appointment.serviceType}</span>
                      </div>
                    </div>
                    
                    {appointment.notes && (
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Notes:</strong> {appointment.notes}
                      </p>
                    )}
                    
                    {appointment.specialRequests && (
                      <p className="text-sm text-gray-700">
                        <strong>Special Requests:</strong> {appointment.specialRequests}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {appointment.status === 'scheduled' && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                      >
                        Confirm
                      </Button>
                    )}
                    
                    {(appointment.status === 'scheduled' || appointment.status === 'confirmed') && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => updateAppointmentStatus(appointment.id, 'completed')}
                      >
                        Complete
                      </Button>
                    )}
                    
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleEditAppointment(appointment)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    
                    {appointment.status !== 'cancelled' && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => updateAppointmentStatus(appointment.id, 'cancelled')}
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {filteredAppointments.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No appointments found matching your criteria.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Appointment Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Appointment</DialogTitle>
            <DialogDescription>
              Update appointment details
            </DialogDescription>
          </DialogHeader>
          
          {selectedAppointment && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="customerName">Customer Name</Label>
                <Input
                  id="customerName"
                  value={selectedAppointment.customerName}
                  onChange={(e) => setSelectedAppointment({
                    ...selectedAppointment,
                    customerName: e.target.value
                  })}
                />
              </div>
              
              <div>
                <Label htmlFor="appointmentDate">Date</Label>
                <Input
                  id="appointmentDate"
                  type="date"
                  value={selectedAppointment.appointmentDate}
                  onChange={(e) => setSelectedAppointment({
                    ...selectedAppointment,
                    appointmentDate: e.target.value
                  })}
                />
              </div>
              
              <div>
                <Label htmlFor="appointmentTime">Time</Label>
                <Input
                  id="appointmentTime"
                  type="time"
                  value={selectedAppointment.appointmentTime}
                  onChange={(e) => setSelectedAppointment({
                    ...selectedAppointment,
                    appointmentTime: e.target.value
                  })}
                />
              </div>
              
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={selectedAppointment.notes || ''}
                  onChange={(e) => setSelectedAppointment({
                    ...selectedAppointment,
                    notes: e.target.value
                  })}
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={saveAppointmentChanges}>
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AppointmentManager;

