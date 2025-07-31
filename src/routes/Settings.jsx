import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Save, 
  Building, 
  Phone, 
  Mail, 
  Clock, 
  MapPin,
  Mic,
  Calendar,
  Users,
  Settings as SettingsIcon,
  Key,
  Database
} from 'lucide-react';

const Settings = () => {
  const [businessConfig, setBusinessConfig] = useState({
    name: 'Your Business Name',
    phone: '(555) 123-4567',
    email: 'info@yourbusiness.com',
    address: '123 Main Street, City, State 12345',
    hours: 'Monday-Friday 9AM-6PM, Saturday 9AM-3PM',
    services: 'Consultation,Treatment,Follow-up',
    defaultVoice: 'alloy',
    appointmentDuration: '60'
  });

  const [voiceSettings, setVoiceSettings] = useState({
    voice: 'alloy',
    speed: '1.0',
    enableTTS: true,
    enableSTT: true,
    language: 'en-US'
  });

  const [integrationSettings, setIntegrationSettings] = useState({
    googleCalendarApiKey: '',
    googleCalendarId: '',
    hubspotApiKey: '',
    salesforceToken: '',
    salesforceUrl: '',
    zohoToken: ''
  });

  const [systemSettings, setSystemSettings] = useState({
    maxCallDuration: '600',
    sessionTimeout: '1800',
    enableLogging: true,
    enableAnalytics: true,
    autoBackup: true
  });

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Load settings from backend
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // Mock loading settings
      console.log('Loading settings...');
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    try {
      // Mock saving settings
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Settings saved:', {
        businessConfig,
        voiceSettings,
        integrationSettings,
        systemSettings
      });
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const testVoice = () => {
    // Mock voice test
    alert(`Testing voice: ${voiceSettings.voice} at speed ${voiceSettings.speed}`);
  };

  const testIntegration = (type) => {
    // Mock integration test
    alert(`Testing ${type} integration...`);
  };

  return (
    <div className="settings-container p-6">
      <div className="header mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Configure your AI voice receptionist system</p>
      </div>

      <Tabs defaultValue="business" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="business">Business</TabsTrigger>
          <TabsTrigger value="voice">Voice & AI</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        {/* Business Settings */}
        <TabsContent value="business">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Building className="h-5 w-5" />
                <span>Business Information</span>
              </CardTitle>
              <CardDescription>
                Configure your business details that the AI will use in conversations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="businessName">Business Name</Label>
                  <Input
                    id="businessName"
                    value={businessConfig.name}
                    onChange={(e) => setBusinessConfig({
                      ...businessConfig,
                      name: e.target.value
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="businessPhone">Phone Number</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="businessPhone"
                      value={businessConfig.phone}
                      onChange={(e) => setBusinessConfig({
                        ...businessConfig,
                        phone: e.target.value
                      })}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="businessEmail">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="businessEmail"
                      type="email"
                      value={businessConfig.email}
                      onChange={(e) => setBusinessConfig({
                        ...businessConfig,
                        email: e.target.value
                      })}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="businessHours">Business Hours</Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="businessHours"
                      value={businessConfig.hours}
                      onChange={(e) => setBusinessConfig({
                        ...businessConfig,
                        hours: e.target.value
                      })}
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <Label htmlFor="businessAddress">Business Address</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="businessAddress"
                    value={businessConfig.address}
                    onChange={(e) => setBusinessConfig({
                      ...businessConfig,
                      address: e.target.value
                    })}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="services">Services Offered (comma-separated)</Label>
                <Textarea
                  id="services"
                  value={businessConfig.services}
                  onChange={(e) => setBusinessConfig({
                    ...businessConfig,
                    services: e.target.value
                  })}
                  placeholder="Consultation, Treatment, Follow-up"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Voice & AI Settings */}
        <TabsContent value="voice">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mic className="h-5 w-5" />
                <span>Voice & AI Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure voice synthesis and AI behavior settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="voiceType">Voice Type</Label>
                  <Select 
                    value={voiceSettings.voice} 
                    onValueChange={(value) => setVoiceSettings({
                      ...voiceSettings,
                      voice: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="alloy">Alloy (Neutral)</SelectItem>
                      <SelectItem value="echo">Echo (Male)</SelectItem>
                      <SelectItem value="fable">Fable (British)</SelectItem>
                      <SelectItem value="onyx">Onyx (Deep)</SelectItem>
                      <SelectItem value="nova">Nova (Female)</SelectItem>
                      <SelectItem value="shimmer">Shimmer (Soft)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="speechSpeed">Speech Speed</Label>
                  <Select 
                    value={voiceSettings.speed} 
                    onValueChange={(value) => setVoiceSettings({
                      ...voiceSettings,
                      speed: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0.5">0.5x (Slow)</SelectItem>
                      <SelectItem value="0.75">0.75x</SelectItem>
                      <SelectItem value="1.0">1.0x (Normal)</SelectItem>
                      <SelectItem value="1.25">1.25x</SelectItem>
                      <SelectItem value="1.5">1.5x (Fast)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="language">Language</Label>
                  <Select 
                    value={voiceSettings.language} 
                    onValueChange={(value) => setVoiceSettings({
                      ...voiceSettings,
                      language: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en-US">English (US)</SelectItem>
                      <SelectItem value="en-GB">English (UK)</SelectItem>
                      <SelectItem value="es-ES">Spanish</SelectItem>
                      <SelectItem value="fr-FR">French</SelectItem>
                      <SelectItem value="de-DE">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex items-center justify-between">
                  <Button onClick={testVoice} variant="outline">
                    Test Voice
                  </Button>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Text-to-Speech</Label>
                    <p className="text-sm text-gray-500">Enable AI voice responses</p>
                  </div>
                  <Switch
                    checked={voiceSettings.enableTTS}
                    onCheckedChange={(checked) => setVoiceSettings({
                      ...voiceSettings,
                      enableTTS: checked
                    })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Speech-to-Text</Label>
                    <p className="text-sm text-gray-500">Enable voice input processing</p>
                  </div>
                  <Switch
                    checked={voiceSettings.enableSTT}
                    onCheckedChange={(checked) => setVoiceSettings({
                      ...voiceSettings,
                      enableSTT: checked
                    })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations Settings */}
        <TabsContent value="integrations">
          <div className="space-y-6">
            {/* Calendar Integration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>Calendar Integration</span>
                </CardTitle>
                <CardDescription>
                  Connect with external calendar systems for appointment scheduling
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="googleCalendarApiKey">Google Calendar API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="googleCalendarApiKey"
                      type="password"
                      value={integrationSettings.googleCalendarApiKey}
                      onChange={(e) => setIntegrationSettings({
                        ...integrationSettings,
                        googleCalendarApiKey: e.target.value
                      })}
                      placeholder="Enter your Google Calendar API key"
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testIntegration('Google Calendar')}
                    >
                      Test
                    </Button>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="googleCalendarId">Google Calendar ID</Label>
                  <Input
                    id="googleCalendarId"
                    value={integrationSettings.googleCalendarId}
                    onChange={(e) => setIntegrationSettings({
                      ...integrationSettings,
                      googleCalendarId: e.target.value
                    })}
                    placeholder="your-calendar@gmail.com"
                  />
                </div>
              </CardContent>
            </Card>

            {/* CRM Integration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>CRM Integration</span>
                </CardTitle>
                <CardDescription>
                  Connect with CRM systems for lead management
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="hubspotApiKey">HubSpot API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="hubspotApiKey"
                      type="password"
                      value={integrationSettings.hubspotApiKey}
                      onChange={(e) => setIntegrationSettings({
                        ...integrationSettings,
                        hubspotApiKey: e.target.value
                      })}
                      placeholder="Enter your HubSpot API key"
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testIntegration('HubSpot')}
                    >
                      Test
                    </Button>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="salesforceToken">Salesforce Access Token</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="salesforceToken"
                      type="password"
                      value={integrationSettings.salesforceToken}
                      onChange={(e) => setIntegrationSettings({
                        ...integrationSettings,
                        salesforceToken: e.target.value
                      })}
                      placeholder="Enter your Salesforce access token"
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testIntegration('Salesforce')}
                    >
                      Test
                    </Button>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="salesforceUrl">Salesforce Instance URL</Label>
                  <Input
                    id="salesforceUrl"
                    value={integrationSettings.salesforceUrl}
                    onChange={(e) => setIntegrationSettings({
                      ...integrationSettings,
                      salesforceUrl: e.target.value
                    })}
                    placeholder="https://your-instance.salesforce.com"
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* System Settings */}
        <TabsContent value="system">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <SettingsIcon className="h-5 w-5" />
                <span>System Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure system behavior and performance settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="maxCallDuration">Max Call Duration (seconds)</Label>
                  <Input
                    id="maxCallDuration"
                    type="number"
                    value={systemSettings.maxCallDuration}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      maxCallDuration: e.target.value
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="sessionTimeout">Session Timeout (seconds)</Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    value={systemSettings.sessionTimeout}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      sessionTimeout: e.target.value
                    })}
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Enable Call Logging</Label>
                    <p className="text-sm text-gray-500">Log all conversations for analysis</p>
                  </div>
                  <Switch
                    checked={systemSettings.enableLogging}
                    onCheckedChange={(checked) => setSystemSettings({
                      ...systemSettings,
                      enableLogging: checked
                    })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Enable Analytics</Label>
                    <p className="text-sm text-gray-500">Collect performance metrics</p>
                  </div>
                  <Switch
                    checked={systemSettings.enableAnalytics}
                    onCheckedChange={(checked) => setSystemSettings({
                      ...systemSettings,
                      enableAnalytics: checked
                    })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Auto Backup</Label>
                    <p className="text-sm text-gray-500">Automatically backup data daily</p>
                  </div>
                  <Switch
                    checked={systemSettings.autoBackup}
                    onCheckedChange={(checked) => setSystemSettings({
                      ...systemSettings,
                      autoBackup: checked
                    })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <div className="flex justify-end mt-6">
        <Button onClick={saveSettings} disabled={isSaving} size="lg">
          <Save className="h-4 w-4 mr-2" />
          {isSaving ? 'Saving...' : 'Save All Settings'}
        </Button>
      </div>
    </div>
  );
};

export default Settings;

