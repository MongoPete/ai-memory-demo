import datetime
from fastapi import HTTPException
from services.bedrock_service import generate_embedding

class Message:
    """
    Message model with comprehensive input validation.
    
    This implementation demonstrates:
    - Application-level schema validation for MongoDB
    - Defensive programming patterns
    - Clear error messages for debugging
    - Data consistency enforcement
    """
    
    def __init__(self, message_data):
        # Validate user_id
        user_id = message_data.user_id.strip()
        if not user_id:
            raise ValueError("user_id cannot be empty")
        self.user_id = user_id
        
        # Validate conversation_id
        conversation_id = message_data.conversation_id.strip()
        if not conversation_id:
            raise ValueError("conversation_id cannot be empty")
        self.conversation_id = conversation_id
        
        # Validate message text
        text = message_data.text.strip()
        if not text:
            raise ValueError("Message text cannot be empty")
        self.text = text
        
        # Set type (no validation needed - FastAPI Pydantic handles this)
        self.type = message_data.type
        
        # Parse and set timestamp
        self.timestamp = self.parse_timestamp(message_data.timestamp)
        
        # Generate embeddings
        self.embeddings = generate_embedding(self.text)
        
        # Validate embedding dimensions (critical for vector search)
        if not self.embeddings or len(self.embeddings) != 1536:
            actual_len = len(self.embeddings) if self.embeddings else 0
            raise ValueError(
                f"Invalid embedding dimensions. Expected 1536, got {actual_len}"
            )
        
    def parse_timestamp(self, timestamp):
        """Parse ISO timestamp or use current time"""
        if timestamp:
            try:
                return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")
        return datetime.datetime.now(datetime.timezone.utc)
        
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "type": self.type,
            "text": self.text,
            "timestamp": self.timestamp,
            "embeddings": self.embeddings,
        }
