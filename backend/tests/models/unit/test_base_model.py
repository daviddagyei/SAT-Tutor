"""
Unit tests for the BaseModel class
"""
import pytest
from datetime import datetime, timedelta, UTC
import uuid

from app.models.base import BaseModel


class ConcreteModel(BaseModel):
    """A concrete implementation of BaseModel for testing purposes"""
    def __init__(self, name="Test", **kwargs):
        super().__init__(**kwargs)
        self.name = name


class TestBaseModel:
    """Tests for the BaseModel class"""

    def test_init_default_values(self):
        """Test that BaseModel initializes with default values when none are provided"""
        model = ConcreteModel()
        
        # Check that ID is a valid UUID
        assert isinstance(model.id, str)
        # Try to parse it as UUID to validate format
        uuid_obj = uuid.UUID(model.id)
        
        # Check creation and update timestamps
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        
        # Timestamps should be very close to now
        now = datetime.now(UTC)
        assert (now - model.created_at).total_seconds() < 1
        assert (now - model.updated_at).total_seconds() < 1

    def test_init_with_provided_values(self):
        """Test that BaseModel uses provided values when initializing"""
        test_id = "test-id-12345"
        test_created = datetime.now(UTC) - timedelta(days=10)
        test_updated = datetime.now(UTC) - timedelta(days=5)
        
        model = ConcreteModel(
            id=test_id,
            created_at=test_created,
            updated_at=test_updated
        )
        
        assert model.id == test_id
        assert model.created_at == test_created
        assert model.updated_at == test_updated

    def test_update_method(self):
        """Test that the update method updates the updated_at timestamp"""
        model = ConcreteModel()
        original_updated_at = model.updated_at
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        # Call update method
        model.update()
        
        # Check that updated_at has changed but created_at has not
        assert model.updated_at > original_updated_at
        assert (model.updated_at - original_updated_at).total_seconds() > 0