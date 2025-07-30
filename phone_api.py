from flask import Blueprint, request, jsonify, Response
from flask_cors import cross_origin
import asyncio
import json
import base64
import logging
from datetime import datetime
from ..services.twilio_service import TwilioService
from ..services.realtime_voice_service import RealtimeVoiceService
from ..services.speech_service import SpeechService
from ..services.dialogue_service import DialogueService
from ..models.call import Call, db

logger = logging.getLogger(__name__)

phone_bp = Blueprint('phone', __name__)

# Global services
twilio_service = TwilioService()
active_calls = {}  # Store active call sessions

@phone_bp.route('/webhook/voice', methods=['POST'])
@cross_origin()
def handle_incoming_call():
    """Handle incoming Twilio voice calls"""
    try:
        # Get call information from Twilio
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        call_status = request.form.get('CallStatus')
        
        logger.info(f"Incoming call: {call_sid} from {from_number} to {to_number}")
        
        # Create call record
        call = Call(
            session_id=call_sid,
            caller_phone=from_number,
            business_phone=to_number,
            status='active',
            start_time=datetime.utcnow()
        )
        db.session.add(call)
        db.session.commit()
        
        # Generate stream URL for WebSocket connection
        stream_url = f"wss://{request.host}/phone/stream/{call_sid}"
        
        # Return TwiML response to connect to media stream
        twiml_response = twilio_service.handle_incoming_call(stream_url)
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        # Return error TwiML
        error_response = twilio_service.create_voice_response(
            message="I'm sorry, but I'm experiencing technical difficulties. Please try calling back later."
        )
        return Response(error_response, mimetype='text/xml')

@phone_bp.route('/webhook/status', methods=['POST'])
@cross_origin()
def handle_call_status():
    """Handle call status updates from Twilio"""
    try:
        call_sid = request.form.get('CallSid')
        call_status = request.form.get('CallStatus')
        call_duration = request.form.get('CallDuration')
        
        logger.info(f"Call status update: {call_sid} - {call_status}")
        
        # Update call record
        call = Call.query.filter_by(session_id=call_sid).first()
        if call:
            call.status = call_status.lower()
            if call_status in ['completed', 'busy', 'failed', 'no-answer']:
                call.end_time = datetime.utcnow()
                if call_duration:
                    call.duration = int(call_duration)
            db.session.commit()
        
        # Clean up active call session
        if call_sid in active_calls and call_status in ['completed', 'busy', 'failed', 'no-answer']:
            del active_calls[call_sid]
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error handling call status: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/stream/<call_sid>')
async def handle_media_stream(call_sid):
    """Handle WebSocket media stream from Twilio"""
    from flask import request
    
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        
        try:
            # Initialize services for this call
            realtime_service = RealtimeVoiceService()
            speech_service = SpeechService()
            dialogue_service = DialogueService()
            
            # Store call session
            active_calls[call_sid] = {
                'realtime_service': realtime_service,
                'speech_service': speech_service,
                'dialogue_service': dialogue_service,
                'ws': ws
            }
            
            # Connect to OpenAI Realtime API
            await realtime_service.connect_to_openai()
            
            # Set up event handlers
            realtime_service.set_audio_response_handler(
                lambda audio: send_audio_to_twilio(ws, audio)
            )
            
            # Handle incoming messages from Twilio
            while True:
                message = ws.receive()
                if message is None:
                    break
                
                try:
                    data = json.loads(message)
                    await handle_twilio_message(call_sid, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from Twilio: {message}")
                except Exception as e:
                    logger.error(f"Error processing Twilio message: {e}")
        
        except Exception as e:
            logger.error(f"Error in media stream for {call_sid}: {e}")
        
        finally:
            # Clean up
            if call_sid in active_calls:
                await active_calls[call_sid]['realtime_service'].disconnect()
                del active_calls[call_sid]
    
    return jsonify({'error': 'WebSocket connection required'}), 400

async def handle_twilio_message(call_sid, data):
    """Process messages from Twilio media stream"""
    event = data.get('event')
    
    if event == 'connected':
        logger.info(f"Media stream connected for call {call_sid}")
    
    elif event == 'start':
        logger.info(f"Media stream started for call {call_sid}")
        stream_sid = data.get('start', {}).get('streamSid')
        
        # Update call record with stream info
        call = Call.query.filter_by(session_id=call_sid).first()
        if call:
            call.stream_sid = stream_sid
            db.session.commit()
    
    elif event == 'media':
        # Process incoming audio
        if call_sid in active_calls:
            payload = data.get('media', {}).get('payload')
            if payload:
                # Send audio to OpenAI Realtime API
                realtime_service = active_calls[call_sid]['realtime_service']
                await realtime_service.send_audio(payload)
    
    elif event == 'stop':
        logger.info(f"Media stream stopped for call {call_sid}")
        if call_sid in active_calls:
            await active_calls[call_sid]['realtime_service'].disconnect()

async def send_audio_to_twilio(ws, audio_data):
    """Send audio response back to Twilio"""
    try:
        media_message = {
            'event': 'media',
            'streamSid': ws.stream_sid if hasattr(ws, 'stream_sid') else None,
            'media': {
                'payload': audio_data
            }
        }
        ws.send(json.dumps(media_message))
    except Exception as e:
        logger.error(f"Error sending audio to Twilio: {e}")

@phone_bp.route('/calls', methods=['GET'])
@cross_origin()
def get_calls():
    """Get call history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')
        
        query = Call.query
        
        if status:
            query = query.filter(Call.status == status)
        
        calls = query.order_by(Call.start_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'calls': [call.to_dict() for call in calls.items],
            'total': calls.total,
            'pages': calls.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/calls/<call_sid>', methods=['GET'])
@cross_origin()
def get_call_details(call_sid):
    """Get details of a specific call"""
    try:
        call = Call.query.filter_by(session_id=call_sid).first()
        if not call:
            return jsonify({'error': 'Call not found'}), 404
        
        # Get additional details from Twilio
        twilio_details = twilio_service.get_call_details(call_sid)
        
        call_data = call.to_dict()
        if twilio_details:
            call_data.update(twilio_details)
        
        return jsonify(call_data)
        
    except Exception as e:
        logger.error(f"Error fetching call details: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/calls/outbound', methods=['POST'])
@cross_origin()
def make_outbound_call():
    """Make an outbound call"""
    try:
        data = request.get_json()
        to_number = data.get('to_number')
        message = data.get('message')
        
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Make the call
        result = twilio_service.make_outbound_call(
            to_number=to_number,
            message=message or "Hello, this is a call from your AI voice assistant."
        )
        
        if result['success']:
            # Create call record
            call = Call(
                session_id=result['call_sid'],
                caller_phone=twilio_service.phone_number,
                business_phone=to_number,
                status='initiated',
                start_time=datetime.utcnow(),
                direction='outbound'
            )
            db.session.add(call)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error making outbound call: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/numbers', methods=['GET'])
@cross_origin()
def get_phone_numbers():
    """Get list of Twilio phone numbers"""
    try:
        numbers = twilio_service.list_phone_numbers()
        return jsonify({'numbers': numbers})
        
    except Exception as e:
        logger.error(f"Error fetching phone numbers: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/numbers/purchase', methods=['POST'])
@cross_origin()
def purchase_phone_number():
    """Purchase a new phone number"""
    try:
        data = request.get_json()
        area_code = data.get('area_code')
        country_code = data.get('country_code', 'US')
        
        result = twilio_service.purchase_phone_number(
            area_code=area_code,
            country_code=country_code
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error purchasing phone number: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/numbers/<number_sid>/configure', methods=['POST'])
@cross_origin()
def configure_phone_number(number_sid):
    """Configure webhook for a phone number"""
    try:
        data = request.get_json()
        voice_url = data.get('voice_url')
        
        if not voice_url:
            # Use default webhook URL
            voice_url = f"https://{request.host}/phone/webhook/voice"
        
        result = twilio_service.configure_webhook(
            phone_number_sid=number_sid,
            voice_url=voice_url
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error configuring phone number: {e}")
        return jsonify({'error': str(e)}), 500

@phone_bp.route('/test/voice', methods=['POST'])
@cross_origin()
def test_voice_response():
    """Test voice response without making a call"""
    try:
        data = request.get_json()
        text = data.get('text', 'Hello, this is a test of the AI voice system.')
        
        # Use speech service to generate audio
        speech_service = SpeechService()
        audio_result = speech_service.text_to_speech(text)
        
        if audio_result['success']:
            return jsonify({
                'success': True,
                'audio_url': audio_result['audio_url'],
                'text': text
            })
        else:
            return jsonify({
                'success': False,
                'error': audio_result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error testing voice response: {e}")
        return jsonify({'error': str(e)}), 500

