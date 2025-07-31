"""
Voice API Routes
Handles voice-related API endpoints for the AI receptionist
"""

import os
import io
import tempfile
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.services.speech_service import SpeechService
from src.services.dialogue_service import DialogueService
from src.models.call import Call, Appointment, BusinessConfig, db
from datetime import datetime

voice_bp = Blueprint('voice', __name__)

# Initialize services
speech_service = SpeechService()
dialogue_service = DialogueService()

@voice_bp.route('/process-call', methods=['POST'])
def process_call():
    """
    Process a voice call - handles audio input and returns audio response
    """
    try:
        # Check if audio file is provided
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400