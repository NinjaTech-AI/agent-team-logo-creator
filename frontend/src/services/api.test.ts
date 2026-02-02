// @ts-nocheck - Test file excluded from production build
/**
 * Unit tests for API service
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { generateLogo, improvePrompt, checkHealth } from './api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('generateLogo', () => {
    it('should successfully generate a logo', async () => {
      const mockResponse = {
        success: true,
        logo_url: 'https://example.com/logo.png',
        generation_id: '123',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await generateLogo({
        business_name: 'Test Company',
        style: 'modern',
      });

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/generate',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('should handle API errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'API Error' }),
      });

      await expect(
        generateLogo({
          business_name: 'Test Company',
          style: 'modern',
        })
      ).rejects.toThrow('API Error');
    });

    it('should send all parameters correctly', async () => {
      const mockResponse = {
        success: true,
        logo_url: 'https://example.com/logo.png',
        generation_id: '123',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await generateLogo({
        business_name: 'Test Company',
        style: 'modern',
        description: 'A tech startup',
        size: '1792x1024',
        resolution: 'high',
        filters: ['vibrant', 'gradient'],
        transparency: true,
        preview_mode: false,
      });

      const callArgs = (global.fetch as any).mock.calls[0];
      const body = JSON.parse(callArgs[1].body);

      expect(body.business_name).toBe('Test Company');
      expect(body.description).toBe('A tech startup');
      expect(body.size).toBe('1792x1024');
      expect(body.resolution).toBe('high');
      expect(body.filters).toEqual(['vibrant', 'gradient']);
      expect(body.transparency).toBe(true);
    });
  });

  describe('improvePrompt', () => {
    it('should successfully improve a prompt', async () => {
      const mockResponse = {
        success: true,
        improved_prompt: 'Enhanced prompt text',
        preview_url: 'https://example.com/preview.png',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await improvePrompt({
        business_name: 'Test Company',
        style: 'modern',
        description: 'Tech startup',
      });

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/improve-prompt',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should handle improvement errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Improvement failed' }),
      });

      await expect(
        improvePrompt({
          business_name: 'Test Company',
          style: 'modern',
        })
      ).rejects.toThrow('Improvement failed');
    });
  });

  describe('checkHealth', () => {
    it('should return true when API is healthy', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
      });

      const result = await checkHealth();

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith('/api/health');
    });

    it('should return false when API is unhealthy', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      const result = await checkHealth();

      expect(result).toBe(false);
    });
  });
});