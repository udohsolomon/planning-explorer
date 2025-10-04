/**
 * ErrorDisplay Component Tests
 * Planning Explorer - Error state UI tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorDisplay } from '../ErrorDisplay';
import type { AnimationError } from '@/types/animation.types';

describe('ErrorDisplay', () => {
  const mockOnRetry = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render error message and title', () => {
      const error: AnimationError = {
        type: 'connection',
        message: 'Unable to reach planning database',
        userMessage: 'Connection Error',
        retryable: true,
      };

      render(<ErrorDisplay error={error} stage={2} />);

      expect(screen.getByText('Connection Error')).toBeInTheDocument();
      expect(screen.getByText('Unable to reach planning database')).toBeInTheDocument();
    });

    it('should render with role="alert" for accessibility', () => {
      const error: AnimationError = {
        type: 'server',
        message: 'Server error occurred',
        userMessage: 'Server Error',
        retryable: true,
      };

      const { container } = render(<ErrorDisplay error={error} stage={2} />);

      const alert = container.querySelector('[role="alert"]');
      expect(alert).toBeInTheDocument();
    });

    it('should render action buttons when provided', () => {
      const error: AnimationError = {
        type: 'connection',
        message: 'Connection failed',
        userMessage: 'Connection Error',
        retryable: true,
        actions: [
          { id: 'retry', label: 'Try Again', variant: 'primary', onClick: vi.fn() },
          { id: 'cancel', label: 'Go Back', variant: 'secondary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} onRetry={mockOnRetry} />);

      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Go Back')).toBeInTheDocument();
    });
  });

  describe('Error Types', () => {
    it('should render connection error with appropriate color', () => {
      const error: AnimationError = {
        type: 'connection',
        message: 'Connection failed',
        userMessage: 'Connection Error',
        retryable: true,
      };

      const { container } = render(<ErrorDisplay error={error} stage={2} />);

      // Check for red color class (connection errors are red)
      const iconContainer = container.querySelector('.text-\\[\\#EF4444\\]');
      expect(iconContainer).toBeInTheDocument();
    });

    it('should render rate limit error with upgrade CTA', () => {
      const error: AnimationError = {
        type: 'rate_limit',
        message: "You've used your free searches for today",
        userMessage: 'Rate Limit Reached',
        retryable: false,
      };

      render(<ErrorDisplay error={error} stage={2} />);

      expect(screen.getByText(/Professional Plan/i)).toBeInTheDocument();
      expect(screen.getByText(/Unlimited AI-enhanced searches/i)).toBeInTheDocument();
    });

    it('should render parsing error with orange color', () => {
      const error: AnimationError = {
        type: 'parsing',
        message: 'Could not parse query',
        userMessage: 'Query Not Understood',
        retryable: true,
      };

      const { container } = render(<ErrorDisplay error={error} stage={1} />);

      // Parsing errors are orange
      const iconContainer = container.querySelector('.text-\\[\\#F59E0B\\]');
      expect(iconContainer).toBeInTheDocument();
    });

    it('should render no_results with blue color', () => {
      const error: AnimationError = {
        type: 'no_results',
        message: 'No matching applications found',
        userMessage: 'No Results Found',
        retryable: true,
      };

      const { container } = render(<ErrorDisplay error={error} stage={5} />);

      // No results errors are blue
      const iconContainer = container.querySelector('.text-\\[\\#3B82F6\\]');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Action Handling', () => {
    it('should call onRetry when retry button is clicked', () => {
      const error: AnimationError = {
        type: 'timeout',
        message: 'Request timed out',
        userMessage: 'Timeout Error',
        retryable: true,
        actions: [
          { id: 'retry', label: 'Try Again', variant: 'primary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} onRetry={mockOnRetry} />);

      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);

      expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when cancel button is clicked', () => {
      const error: AnimationError = {
        type: 'server',
        message: 'Server error',
        userMessage: 'Server Error',
        retryable: true,
        actions: [
          { id: 'cancel', label: 'Go Back', variant: 'secondary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByText('Go Back');
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should navigate to /pricing when upgrade button is clicked', () => {
      const error: AnimationError = {
        type: 'rate_limit',
        message: 'Rate limit reached',
        userMessage: 'Rate Limit Reached',
        retryable: false,
        actions: [
          { id: 'upgrade', label: 'Upgrade Now', variant: 'primary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} />);

      const upgradeButton = screen.getByText('Upgrade Now');
      fireEvent.click(upgradeButton);

      expect(window.location.href).toBe('/pricing');
    });

    it('should open email client when report button is clicked', () => {
      const mockWindowOpen = vi.spyOn(window, 'open').mockImplementation();

      const error: AnimationError = {
        type: 'unknown',
        message: 'Unknown error',
        userMessage: 'Unexpected Error',
        retryable: true,
        actions: [
          { id: 'report', label: 'Report Issue', variant: 'secondary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} />);

      const reportButton = screen.getByText('Report Issue');
      fireEvent.click(reportButton);

      expect(mockWindowOpen).toHaveBeenCalledWith(
        'mailto:support@planningexplorer.com',
        '_blank'
      );

      mockWindowOpen.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have aria-live="assertive" for screen readers', () => {
      const error: AnimationError = {
        type: 'connection',
        message: 'Connection failed',
        userMessage: 'Connection Error',
        retryable: true,
      };

      const { container } = render(<ErrorDisplay error={error} stage={2} />);

      const alert = container.querySelector('[aria-live="assertive"]');
      expect(alert).toBeInTheDocument();
    });

    it('should have accessible button labels', () => {
      const error: AnimationError = {
        type: 'connection',
        message: 'Connection failed',
        userMessage: 'Connection Error',
        retryable: true,
        actions: [
          { id: 'retry', label: 'Try Again', variant: 'primary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} onRetry={mockOnRetry} />);

      const button = screen.getByText('Try Again');
      expect(button).toBeInstanceOf(HTMLButtonElement);
      expect(button).toHaveTextContent('Try Again');
    });

    it('should support keyboard focus on action buttons', () => {
      const error: AnimationError = {
        type: 'timeout',
        message: 'Timeout',
        userMessage: 'Timeout Error',
        retryable: true,
        actions: [
          { id: 'retry', label: 'Try Again', variant: 'primary', onClick: vi.fn() },
        ],
      };

      render(<ErrorDisplay error={error} stage={2} onRetry={mockOnRetry} />);

      const button = screen.getByText('Try Again');
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });

  describe('Rate Limit Upgrade CTA', () => {
    it('should display all upgrade features', () => {
      const error: AnimationError = {
        type: 'rate_limit',
        message: 'Rate limit',
        userMessage: 'Rate Limit Reached',
        retryable: false,
      };

      render(<ErrorDisplay error={error} stage={2} />);

      expect(screen.getByText(/Unlimited AI-enhanced searches/i)).toBeInTheDocument();
      expect(screen.getByText(/Advanced opportunity scoring/i)).toBeInTheDocument();
      expect(screen.getByText(/Email alerts and saved searches/i)).toBeInTheDocument();
    });

    it('should only show upgrade CTA for rate_limit errors', () => {
      const { rerender } = render(
        <ErrorDisplay
          error={{
            type: 'connection',
            message: 'Connection failed',
            userMessage: 'Connection Error',
            retryable: true,
          }}
          stage={2}
        />
      );

      expect(screen.queryByText(/Professional Plan/i)).not.toBeInTheDocument();

      rerender(
        <ErrorDisplay
          error={{
            type: 'rate_limit',
            message: 'Rate limit',
            userMessage: 'Rate Limit Reached',
            retryable: false,
          }}
          stage={2}
        />
      );

      expect(screen.getByText(/Professional Plan/i)).toBeInTheDocument();
    });
  });

  describe('Error Icon Display', () => {
    it('should render appropriate icon for each error type', () => {
      const errorTypes: Array<AnimationError['type']> = [
        'connection',
        'parsing',
        'timeout',
        'server',
        'rate_limit',
        'no_results',
        'unknown',
      ];

      errorTypes.forEach((type) => {
        const { unmount } = render(
          <ErrorDisplay
            error={{
              type,
              message: `${type} error`,
              userMessage: `${type} Error`,
              retryable: true,
            }}
            stage={2}
          />
        );

        // Icon should be rendered (check for svg element)
        const svg = document.querySelector('svg');
        expect(svg).toBeInTheDocument();

        unmount();
      });
    });
  });
});
