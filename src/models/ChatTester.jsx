import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Bot, 
  User, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX,
  RotateCcw,
  MessageSquare
} from 'lucide-react';

const ChatTester = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: 'Hello! I\'m your AI voice receptionist. How can I help you today?',
        timestamp: new Date(),
        intent: 'greeting'
      }
    ]);
    
    // Generate session ID
    setSessionId(`test_${Date.now()}`);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Mock API call to backend
      const response = await mockApiCall(inputMessage, sessionId);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        timestamp: new Date(),
        intent: response.intent,
        confidence: response.confidence || 0.9
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'I apologize, but I\'m having trouble processing your request right now. Please try again.',
        timestamp: new Date(),
        intent: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const mockApiCall = async (message, sessionId) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    // Mock responses based on message content
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('appointment') || lowerMessage.includes('book') || lowerMessage.includes('schedule')) {
      return {
        response: "I'd be happy to help you schedule an appointment. What type of service are you looking for, and when would you prefer to come in?",
        intent: 'appointment_booking',
        confidence: 0.95
      };
    }
    
    if (lowerMessage.includes('hours') || lowerMessage.includes('open') || lowerMessage.includes('close')) {
      return {
        response: "Our business hours are Monday through Friday, 9 AM to 6 PM, and Saturday 9 AM to 3 PM. We're closed on Sundays. Is there anything else I can help you with?",
        intent: 'business_hours',
        confidence: 0.92
      };
    }
    
    if (lowerMessage.includes('service') || lowerMessage.includes('what do you do') || lowerMessage.includes('offer')) {
      return {
        response: "We offer a variety of services including Consultation, Treatment, and Follow-up appointments. Would you like more information about any specific service?",
        intent: 'services',
        confidence: 0.88
      };
    }
    
    if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('fee')) {
      return {
        response: "Our pricing varies depending on the specific service you're interested in. Could you tell me which service you'd like to know about so I can provide accurate pricing information?",
        intent: 'pricing',
        confidence: 0.85
      };
    }
    
    if (lowerMessage.includes('location') || lowerMessage.includes('address') || lowerMessage.includes('where')) {
      return {
        response: "We're located at 123 Main Street, City, State 12345. Would you like me to provide directions or send you our location details?",
        intent: 'location',
        confidence: 0.90
      };
    }
    
    if (lowerMessage.includes('contact') || lowerMessage.includes('phone') || lowerMessage.includes('email')) {
      return {
        response: "You can reach us at (555) 123-4567 or email us at info@yourbusiness.com. Is there anything specific you'd like to know or discuss?",
        intent: 'contact',
        confidence: 0.87
      };
    }
    
    if (lowerMessage.includes('bye') || lowerMessage.includes('goodbye') || lowerMessage.includes('thanks')) {
      return {
        response: "Thank you for contacting us! Have a wonderful day, and we look forward to serving you soon.",
        intent: 'goodbye',
        confidence: 0.93
      };
    }

    // Default response
    return {
      response: "I understand you're asking about that. Could you please provide a bit more detail so I can better assist you?",
      intent: 'unknown',
      confidence: 0.60
    };
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetConversation = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: 'Hello! I\'m your AI voice receptionist. How can I help you today?',
        timestamp: new Date(),
        intent: 'greeting'
      }
    ]);
    setSessionId(`test_${Date.now()}`);
  };

  const getIntentBadge = (intent) => {
    const intentColors = {
      greeting: 'bg-blue-100 text-blue-800',
      appointment_booking: 'bg-green-100 text-green-800',
      business_hours: 'bg-purple-100 text-purple-800',
      services: 'bg-yellow-100 text-yellow-800',
      pricing: 'bg-orange-100 text-orange-800',
      location: 'bg-pink-100 text-pink-800',
      contact: 'bg-gray-100 text-gray-800',
      goodbye: 'bg-indigo-100 text-indigo-800',
      unknown: 'bg-red-100 text-red-800',
      error: 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={`text-xs ${intentColors[intent] || 'bg-gray-100 text-gray-800'}`}>
        {intent?.replace('_', ' ')}
      </Badge>
    );
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // In a real implementation, this would start/stop voice recording
    if (!isRecording) {
      // Simulate recording for demo
      setTimeout(() => {
        setIsRecording(false);
        setInputMessage("I'd like to book an appointment for next week");
      }, 3000);
    }
  };

  const toggleSpeech = () => {
    setIsSpeaking(!isSpeaking);
    // In a real implementation, this would enable/disable text-to-speech
  };

  return (
    <div className="chat-tester-container p-6">
      <div className="header mb-6">
        <h1 className="text-3xl font-bold text-gray-900">AI Chat Tester</h1>
        <p className="text-gray-600 mt-2">Test your AI voice receptionist with real-time chat</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Chat with AI Receptionist</CardTitle>
                  <CardDescription>Session ID: {sessionId}</CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleSpeech}
                    className={isSpeaking ? 'bg-blue-100' : ''}
                  >
                    {isSpeaking ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                  </Button>
                  <Button variant="outline" size="sm" onClick={resetConversation}>
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.type === 'bot' && <Bot className="h-4 w-4 mt-1 flex-shrink-0" />}
                        {message.type === 'user' && <User className="h-4 w-4 mt-1 flex-shrink-0" />}
                        <div className="flex-1">
                          <p className="text-sm">{message.content}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs opacity-70">
                              {formatTime(message.timestamp)}
                            </span>
                            {message.intent && message.type === 'bot' && (
                              <div className="ml-2">
                                {getIntentBadge(message.intent)}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                      <div className="flex items-center space-x-2">
                        <Bot className="h-4 w-4" />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
              
              {/* Input */}
              <div className="flex-shrink-0">
                <div className="flex space-x-2">
                  <div className="flex-1 relative">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message..."
                      disabled={isLoading}
                      className="pr-12"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      className={`absolute right-1 top-1 h-8 w-8 p-0 ${isRecording ? 'bg-red-100 text-red-600' : ''}`}
                      onClick={toggleRecording}
                    >
                      {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    </Button>
                  </div>
                  <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                {isRecording && (
                  <p className="text-sm text-red-600 mt-1 flex items-center">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2"></div>
                    Recording... (demo mode)
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Test Suggestions */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Test Suggestions</CardTitle>
              <CardDescription>Try these sample queries</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  "I'd like to book an appointment",
                  "What are your business hours?",
                  "What services do you offer?",
                  "How much does a consultation cost?",
                  "Where are you located?",
                  "What's your phone number?",
                  "I need to cancel my appointment",
                  "Thank you, goodbye"
                ].map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="w-full text-left justify-start h-auto p-2 text-xs"
                    onClick={() => setInputMessage(suggestion)}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Session Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Messages:</span>
                  <span>{messages.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>User Messages:</span>
                  <span>{messages.filter(m => m.type === 'user').length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Bot Responses:</span>
                  <span>{messages.filter(m => m.type === 'bot').length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Session Duration:</span>
                  <span>Active</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ChatTester;

