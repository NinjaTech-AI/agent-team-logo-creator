"""
Unit tests for the AI Logo Creator API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app, GenerateLogoRequest, ImprovePromptRequest

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check_returns_healthy(self):
        """Test that health endpoint returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestGenerateLogoEndpoint:
    """Tests for the logo generation endpoint"""
    
    @patch('main.get_openai_client')
    def test_generate_logo_basic_request(self, mock_client):
        """Test basic logo generation with minimal parameters"""
        # Mock OpenAI response
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["logo_url"] == "https://example.com/logo.png"
        assert data["generation_id"] is not None
    
    @patch('main.get_openai_client')
    def test_generate_logo_with_description(self, mock_client):
        """Test logo generation with description field (#32)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "description": "A tech startup focused on innovation"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify description was included in the prompt
        call_args = mock_openai.images.generate.call_args
        prompt = call_args.kwargs['prompt']
        assert "A tech startup focused on innovation" in prompt
    
    @patch('main.get_openai_client')
    def test_generate_logo_with_custom_size(self, mock_client):
        """Test logo generation with custom size (#33)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "size": "1792x1024"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify size was used
        call_args = mock_openai.images.generate.call_args
        assert call_args.kwargs['size'] == "1792x1024"
    
    @patch('main.get_openai_client')
    def test_generate_logo_with_filters(self, mock_client):
        """Test logo generation with filters (#34)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "filters": ["vibrant", "gradient"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify filters were included in the prompt
        call_args = mock_openai.images.generate.call_args
        prompt = call_args.kwargs['prompt']
        assert "vibrant" in prompt.lower()
        assert "gradient" in prompt.lower()
    
    @patch('main.get_openai_client')
    def test_generate_logo_preview_mode(self, mock_client):
        """Test logo generation in preview mode (#35)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "preview_mode": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify preview mode uses low quality
        call_args = mock_openai.images.generate.call_args
        assert call_args.kwargs['quality'] == "low"
    
    @patch('main.get_openai_client')
    def test_generate_logo_with_transparency(self, mock_client):
        """Test logo generation with transparency (#36)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "transparency": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify transparency was mentioned in the prompt
        call_args = mock_openai.images.generate.call_args
        prompt = call_args.kwargs['prompt']
        assert "transparent" in prompt.lower()
    
    @patch('main.get_openai_client')
    def test_generate_logo_quality_mapping(self, mock_client):
        """Test quality parameter mapping (#33)"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        # Test standard -> medium
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "resolution": "standard"
            }
        )
        assert response.status_code == 200
        call_args = mock_openai.images.generate.call_args
        assert call_args.kwargs['quality'] == "medium"
        
        # Test high -> high
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "resolution": "high"
            }
        )
        assert response.status_code == 200
        call_args = mock_openai.images.generate.call_args
        assert call_args.kwargs['quality'] == "high"
    
    @patch('main.get_openai_client')
    def test_generate_logo_error_handling(self, mock_client):
        """Test error handling when OpenAI API fails"""
        mock_openai = Mock()
        mock_openai.images.generate.side_effect = Exception("API Error")
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test Company",
                "style": "modern"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to generate logo" in data["error"]


class TestImprovePromptEndpoint:
    """Tests for the AI prompt improver endpoint (#37)"""
    
    @patch('main.get_openai_client')
    def test_improve_prompt_basic(self, mock_client):
        """Test basic prompt improvement"""
        mock_openai = Mock()
        
        # Mock GPT-4 response
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Improved prompt text"))]
        )
        
        # Mock image generation response
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/preview.png")]
        )
        
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/improve-prompt",
            json={
                "business_name": "Test Company",
                "style": "modern"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["improved_prompt"] == "Improved prompt text"
        assert data["preview_url"] == "https://example.com/preview.png"
    
    @patch('main.get_openai_client')
    def test_improve_prompt_with_description(self, mock_client):
        """Test prompt improvement with description"""
        mock_openai = Mock()
        
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Improved prompt"))]
        )
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/preview.png")]
        )
        
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/improve-prompt",
            json={
                "business_name": "Test Company",
                "style": "modern",
                "description": "Tech startup"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify description was included in GPT-4 call
        call_args = mock_openai.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        assert "Tech startup" in user_message
    
    @patch('main.get_openai_client')
    def test_improve_prompt_error_handling(self, mock_client):
        """Test error handling in prompt improvement"""
        mock_openai = Mock()
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        mock_client.return_value = mock_openai
        
        response = client.post(
            "/api/improve-prompt",
            json={
                "business_name": "Test Company",
                "style": "modern"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to improve prompt" in data["error"]


class TestRequestValidation:
    """Tests for request validation"""
    
    def test_generate_logo_missing_business_name(self):
        """Test that business_name is required"""
        response = client.post(
            "/api/generate",
            json={"style": "modern"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_generate_logo_invalid_size(self):
        """Test handling of invalid size values"""
        # Should still work, will use default size
        response = client.post(
            "/api/generate",
            json={
                "business_name": "Test",
                "size": "invalid_size"
            }
        )
        # The endpoint should handle this gracefully


class TestStylePrompts:
    """Tests for different logo styles"""
    
    @patch('main.get_openai_client')
    def test_all_logo_styles(self, mock_client):
        """Test that all logo styles work"""
        mock_openai = Mock()
        mock_openai.images.generate.return_value = Mock(
            data=[Mock(url="https://example.com/logo.png")]
        )
        mock_client.return_value = mock_openai
        
        styles = ["minimalist", "modern", "classic", "playful", "professional", "vintage"]
        
        for style in styles:
            response = client.post(
                "/api/generate",
                json={
                    "business_name": "Test Company",
                    "style": style
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])