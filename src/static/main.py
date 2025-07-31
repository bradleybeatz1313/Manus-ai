import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.call import Call, Appointment, BusinessConfig
from src.routes.user import user_bp
from src.routes.voice_api import voice_bp
from src.routes.phone_api import phone_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(voice_bp, url_prefix='/api/voice')
app.register_blueprint(phone_bp, url_prefix='/api/phone')

with app.app_context():
    db.create_all()
    
    # Initialize default business configuration
    if not BusinessConfig.query.filter_by(key='business_name').first():
        default_configs = [
            ('business_name', 'Your Business Name', 'Name of the business'),
            ('business_hours', 'Monday-Friday 9AM-6PM, Saturday 9AM-3PM', 'Business operating hours'),
            ('business_address', '123 Main Street, City, State 12345', 'Business address'),
            ('business_phone', '(555) 123-4567', 'Business phone number'),
            ('business_email', 'info@yourbusiness.com', 'Business email address'),
            ('services', 'Consultation,Treatment,Follow-up', 'Available services (comma-separated)'),
            ('default_voice', 'alloy', 'Default TTS voice'),
            ('appointment_duration', '60', 'Default appointment duration in minutes'),
            ('twilio_account_sid', '', 'Twilio Account SID'),
            ('twilio_auth_token', '', 'Twilio Auth Token'),
            ('twilio_phone_number', '', 'Twilio Phone Number'),
            ('openai_api_key', '', 'OpenAI API Key for Realtime API')
        ]
        
        for key, value, description in default_configs:
            config = BusinessConfig(key=key, value=value, description=description)
            db.session.add(config)
        
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
