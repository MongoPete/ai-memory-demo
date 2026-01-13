"""
Test suite for Exercise 2: Index Health Monitoring

Run with: pytest test_index_health.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# These tests mock MongoDB responses since we can't test against real Atlas indexes


class TestIndexValidator:
    """Test index validation logic"""
    
    @pytest.mark.asyncio
    async def test_all_indexes_exist(self):
        """Should return exists=True for all indexes when they exist"""
        from database.index_validator import validate_search_indexes
        
        # Mock list_search_indexes to return all indexes
        mock_indexes = [
            {"name": "conversations_vector_search_index"},
            {"name": "conversations_fulltext_search_index"},
            {"name": "memory_nodes_vector_search_index"}
        ]
        
        with patch("database.mongodb.conversations") as mock_conv, \
             patch("database.mongodb.memory_nodes") as mock_mem:
            
            mock_conv.list_search_indexes.return_value = iter(mock_indexes[:2])
            mock_mem.list_search_indexes.return_value = iter([mock_indexes[2]])
            
            result = await validate_search_indexes()
            
            assert result["conversations_vector_search_index"]["exists"] is True
            assert result["conversations_fulltext_search_index"]["exists"] is True
            assert result["memory_nodes_vector_search_index"]["exists"] is True
    
    @pytest.mark.asyncio
    async def test_missing_indexes_detected(self):
        """Should return exists=False for missing indexes"""
        from database.index_validator import validate_search_indexes
        
        # Mock empty index lists
        with patch("database.mongodb.conversations") as mock_conv, \
             patch("database.mongodb.memory_nodes") as mock_mem:
            
            mock_conv.list_search_indexes.return_value = iter([])
            mock_mem.list_search_indexes.return_value = iter([])
            
            result = await validate_search_indexes()
            
            assert result["conversations_vector_search_index"]["exists"] is False
            assert result["conversations_fulltext_search_index"]["exists"] is False
            assert result["memory_nodes_vector_search_index"]["exists"] is False
    
    @pytest.mark.asyncio
    async def test_get_index_status_simple(self):
        """Should return simple status dict"""
        from database.index_validator import get_index_status
        
        with patch("database.index_validator.validate_search_indexes") as mock_validate:
            mock_validate.return_value = {
                "conversations_vector_search_index": {"exists": True},
                "conversations_fulltext_search_index": {"exists": False}
            }
            
            status = await get_index_status()
            
            assert status["conversations_vector_search_index"] == "exists"
            assert status["conversations_fulltext_search_index"] == "missing"
    
    def test_setup_instructions_generated(self):
        """Should generate helpful setup instructions"""
        from database.index_validator import get_setup_instructions
        
        missing = ["conversations_vector_search_index"]
        instructions = get_setup_instructions(missing)
        
        assert "conversations_vector_search_index" in instructions
        assert "MongoDB Atlas" in instructions
        assert "docs" in instructions.lower()


class TestHealthEndpoint:
    """Test health endpoint integration"""
    
    @pytest.mark.asyncio
    async def test_health_includes_index_status(self):
        """Health endpoint should include index status"""
        # This test would need to mock the FastAPI app
        # For now, we'll test the logic separately
        pass
    
    @pytest.mark.asyncio
    async def test_degraded_status_when_indexes_missing(self):
        """Should return degraded status if any index is missing"""
        # Mock scenario where one index is missing
        from database.index_validator import get_index_status
        
        with patch("database.index_validator.validate_search_indexes") as mock_validate:
            mock_validate.return_value = {
                "conversations_vector_search_index": {"exists": True},
                "conversations_fulltext_search_index": {"exists": False},
                "memory_nodes_vector_search_index": {"exists": True}
            }
            
            status = await get_index_status()
            
            # Check that at least one is missing
            missing_count = sum(1 for v in status.values() if v == "missing")
            assert missing_count > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
