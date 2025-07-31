"""
Call Model
Database model for storing call information and logs
"""

from src.models.user import db
from datetime import datetime
import json

class Call(db.Model):
    """Model for storing call information"""
    __tablename__ = 'calls'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    caller_phone = db.Column(db.String(20), nullable=True)
    caller_name = db.Column(db.String(100), nullable=True)
    caller_email = db.Column(db.String(100), nullable=True)
    
    # Call details
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    call_status = db.Column(db.String(20), default='active')  # active, completed, failed
    
    # Conversation details
    primary_intent = db.Column(db.String(50), nullable=True)
    conversation_summary = db.Column(db.Text, nullable=True)
    conversation_history = db.Column(db.Text, nullable=True)  # JSON string
    
    # Business outcomes
    appointment_booked = db.Column(db.Boolean, default=False)
    lead_qualified = db.Column(db.Boolean, default=False)
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Call {self.id}: {self.session_id}>'
    
    def to_dict(self):
        """Convert call object to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'caller_phone': self.caller_phone,
            'caller_name': self.caller_name,
            'caller_email': self.caller_email,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'call_status': self.call_status,
            'primary_intent': self.primary_intent,
            'conversation_summary': self.conversation_summary,
            'conversation_history': json.loads(self.conversation_history) if self.conversation_history else [],
            'appointment_booked': self.appointment_booked,
            'lead_qualified': self.lead_qualified,
            'follow_up_required': self.follow_up_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_conversation_history(self, history_list):
        """Set conversation history from list"""
        self.conversation_history = json.dumps(history_list)
    
    def get_conversation_history(self):
        """Get conversation history as list"""
        if self.conversation_history:
            return json.loads(self.conversation_history)
        return []
    
    def calculate_duration(self):
        """Calculate and set call duration"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
    
    def end_call(self):
        """Mark call as ended"""
        self.end_time = datetime.utcnow()
        self.call_status = 'completed'
        self.calculate_duration()

class Appointment(db.Model):
    """Model for storing appointment information"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.Integer, db.ForeignKey('calls.id'), nullable=True)
    
    # Customer information
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    
    # Appointment details
    service_type = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    
    # Status and notes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, cancelled, completed
    notes = db.Column(db.Text, nullable=True)
    special_requests = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    call = db.relationship('Call', backref=db.backref('appointments', lazy=True))
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.customer_name} on {self.appointment_date}>'
    
    def to_dict(self):
        """Convert appointment object to dictionary"""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'service_type': self.service_type,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'notes': self.notes,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BusinessConfig(db.Model):
    """Model for storing business configuration"""
    __tablename__ = 'business_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusinessConfig {self.key}: {self.value[:50]}...>'
    
    def to_dict(self):
        """Convert config object to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_config(key, default=None):
        """Get configuration value by key"""
        config = BusinessConfig.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_config(key, value, description=None):
        """Set configuration value"""
        config = BusinessConfig.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = BusinessConfig(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config

