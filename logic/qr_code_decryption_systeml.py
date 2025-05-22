"""
QR Code Data Processing System - Simplified Version
Handles base64 encoding/decoding and JSON parsing
"""

import base64
import json
import logging
import sys
from dataclasses import dataclass
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Custom Exceptions
class QRProcessingError(Exception):
    """Base exception for QR processing errors"""
    pass

class InvalidDataFormatError(QRProcessingError):
    """Raised when data format is invalid or corrupted"""
    pass

@dataclass
class StudentData:
    """Dataclass representing student information"""
    full_name: str
    national_id: str
    phone_number: str = ""
    address: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with camelCase keys for frontend compatibility"""
        return {
            'fullName': self.full_name,
            'nationalId': self.national_id,
            'phoneNumber': self.phone_number,
            'address': self.address
        }

def process_qr_data(qr_data: str) -> StudentData:
    """
    Process QR data using base64 encoding/decoding
    
    Process:
    1. Base64 decode
    2. UTF-8 decode -> JSON parse
    """
    logger.info("="*60)
    logger.info("🚀 QR CODE PROCESSING")
    logger.info("="*60)
    logger.info(f"📊 Input data: {qr_data}")
    
    try:
        # Clean the input data
        cleaned_data = qr_data.strip().lstrip('\ufeff').replace('\x00', '')
        logger.info(f"🧹 Cleaned data: {cleaned_data}")
        logger.info(f"📏 Data length: {len(cleaned_data)}")
        
        # Step 1: Base64 decode
        try:
            decoded_bytes = base64.b64decode(cleaned_data)
            logger.info(f"✅ Base64 decoded successfully")
            logger.info(f"📦 Decoded bytes length: {len(decoded_bytes)}")
            logger.info(f"🔢 Decoded bytes (hex): {decoded_bytes.hex()}")
        except Exception as e:
            logger.error(f"❌ Base64 decode failed: {e}")
            raise InvalidDataFormatError(f"Invalid base64 data: {e}")
        
        # Step 2: UTF-8 decode
        try:
            json_str = decoded_bytes.decode('utf-8')
            logger.info(f"✅ UTF-8 decoded successfully")
            logger.info(f"📝 JSON string: {json_str}")
        except UnicodeDecodeError as e:
            logger.error(f"❌ UTF-8 decode failed: {e}")
            # Try with error handling
            json_str = decoded_bytes.decode('utf-8', errors='replace')
            logger.warning(f"⚠️ UTF-8 decode with errors: {json_str}")
        
        # Step 3: Parse JSON
        try:
            data = json.loads(json_str)
            logger.info(f"✅ JSON parsed successfully")
            logger.info(f"📋 Parsed data: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse failed: {e}")
            logger.error(f"🔍 Problematic JSON string: {repr(json_str)}")
            raise InvalidDataFormatError(f"Invalid JSON format: {e}")
        
        # Step 4: Extract student data
        # JSON structure: {"n":"name", "i":"id", "p":"phone", "a":"address"}
        student_data = StudentData(
            full_name=str(data.get('n', '')),      # 'n' = name
            national_id=str(data.get('i', '')),    # 'i' = id
            phone_number=str(data.get('p', '')),   # 'p' = phone
            address=str(data.get('a', ''))         # 'a' = address
        )
        
        # Validate required fields
        if not student_data.national_id:
            raise InvalidDataFormatError("Missing required field: national_id")
        
        # Display results in Arabic/English
        logger.info("="*60)
        logger.info("🎉 PROCESSING SUCCESSFUL!")
        logger.info("="*60)
        print(f"👤 الاسم الكامل / Full Name: {student_data.full_name}")
        print(f"🆔 الرقم القومي / National ID: {student_data.national_id}")
        print(f"📞 رقم الهاتف / Phone: {student_data.phone_number}")
        print(f"🏠 العنوان / Address: {student_data.address}")
        logger.info("="*60)
        
        return student_data
        
    except Exception as e:
        logger.error("="*60)
        logger.error("❌ PROCESSING FAILED")
        logger.error(f"🚨 Error type: {type(e).__name__}")
        logger.error(f"🚨 Error details: {str(e)}")
        logger.error("="*60)
        raise QRProcessingError(f"Processing failed: {str(e)}")