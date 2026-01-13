"""
Test suite for Exercise 1: Data Validation

These tests should PASS after you implement validation in database/models.py

Run with: pytest test_validation.py -v
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import from main codebase
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database.models import Message
from models.pydantic_models import MessageInput


class TestUserIdValidation:
    """Test user_id validation"""
    
    def test_empty_user_id_rejected(self):
        """Should raise ValueError for empty user_id"""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            msg_input = MessageInput(
                user_id="",
                conversation_id="test",
                type="human",
                text="Hello",
                timestamp=None
            )
            Message(msg_input)
    
    def test_whitespace_only_user_id_rejected(self):
        """Should raise ValueError for whitespace-only user_id"""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            msg_input = MessageInput(
                user_id="   ",
                conversation_id="test",
                type="human",
                text="Hello",
                timestamp=None
            )
            Message(msg_input)


class TestConversationIdValidation:
    """Test conversation_id validation"""
    
    def test_empty_conversation_id_rejected(self):
        """Should raise ValueError for empty conversation_id"""
        with pytest.raises(ValueError, match="conversation_id cannot be empty"):
            msg_input = MessageInput(
                user_id="alice",
                conversation_id="",
                type="human",
                text="Hello",
                timestamp=None
            )
            Message(msg_input)


class TestMessageTextValidation:
    """Test message text validation"""
    
    def test_empty_text_rejected(self):
        """Should raise ValueError for empty text"""
        with pytest.raises(ValueError, match="Message text cannot be empty"):
            msg_input = MessageInput(
                user_id="alice",
                conversation_id="test",
                type="human",
                text="",
                timestamp=None
            )
            Message(msg_input)
    
    def test_whitespace_only_text_rejected(self):
        """Should raise ValueError for whitespace-only text"""
        with pytest.raises(ValueError, match="Message text cannot be empty"):
            msg_input = MessageInput(
                user_id="alice",
                conversation_id="test",
                type="human",
                text="    ",
                timestamp=None
            )
            Message(msg_input)


class TestEmbeddingValidation:
    """Test embedding dimension validation"""
    
    def test_invalid_embedding_dimensions(self, monkeypatch):
        """Should raise ValueError for wrong embedding dimensions"""
        # Mock generate_embedding to return wrong dimensions
        def mock_generate_embedding(text):
            return [0.1] * 128  # Wrong size!
        
        monkeypatch.setattr("database.models.generate_embedding", mock_generate_embedding)
        
        with pytest.raises(ValueError, match="Invalid embedding dimensions. Expected 1536, got 128"):
            msg_input = MessageInput(
                user_id="alice",
                conversation_id="test",
                type="human",
                text="Hello",
                timestamp=None
            )
            Message(msg_input)
    
    def test_empty_embedding_rejected(self, monkeypatch):
        """Should raise ValueError for empty embeddings"""
        # Mock generate_embedding to return empty list
        def mock_generate_embedding(text):
            return []
        
        monkeypatch.setattr("database.models.generate_embedding", mock_generate_embedding)
        
        with pytest.raises(ValueError, match="Invalid embedding dimensions. Expected 1536, got 0"):
            msg_input = MessageInput(
                user_id="alice",
                conversation_id="test",
                type="human",
                text="Hello",
                timestamp=None
            )
            Message(msg_input)


class TestValidInputs:
    """Test that valid inputs still work"""
    
    def test_valid_message_accepted(self, monkeypatch):
        """Should successfully create message with valid inputs"""
        # Mock generate_embedding to return correct dimensions
        def mock_generate_embedding(text):
            return [0.1] * 1536
        
        monkeypatch.setattr("database.models.generate_embedding", mock_generate_embedding)
        
        msg_input = MessageInput(
            user_id="alice",
            conversation_id="test_conv",
            type="human",
            text="This is a valid message",
            timestamp=None
        )
        
        # Should not raise any exception
        message = Message(msg_input)
        
        # Verify fields
        assert message.user_id == "alice"
        assert message.conversation_id == "test_conv"
        assert message.text == "This is a valid message"
        assert len(message.embeddings) == 1536


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
