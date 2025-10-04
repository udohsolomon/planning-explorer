/**
 * Focus Trap Hook
 * Planning Explorer - Manages focus containment in modal dialogs
 */

import { useEffect, useRef } from 'react';

interface UseFocusTrapProps {
  /**
   * Whether the focus trap is active
   */
  isActive: boolean;

  /**
   * Auto-focus the first focusable element on activation
   * Default: true
   */
  autoFocus?: boolean;

  /**
   * Return focus to the element that triggered the modal on deactivation
   * Default: true
   */
  returnFocus?: boolean;
}

/**
 * Focus trap hook for modal accessibility
 *
 * Traps keyboard focus within a container element to prevent
 * focus from escaping the modal. Essential for WCAG compliance.
 *
 * @example
 * const trapRef = useFocusTrap({ isActive: isOpen });
 *
 * return (
 *   <div ref={trapRef} role="dialog">
 *     <button>Action 1</button>
 *     <button>Action 2</button>
 *   </div>
 * );
 */
export function useFocusTrap({
  isActive,
  autoFocus = true,
  returnFocus = true,
}: UseFocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isActive) return;

    // Store the currently focused element
    previouslyFocusedElement.current = document.activeElement as HTMLElement;

    const container = containerRef.current;
    if (!container) return;

    // Get all focusable elements within the container
    const getFocusableElements = (): HTMLElement[] => {
      if (!container) return [];

      const focusableSelectors = [
        'a[href]',
        'area[href]',
        'input:not([disabled]):not([type="hidden"])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        'button:not([disabled])',
        '[tabindex]:not([tabindex="-1"])',
      ].join(', ');

      return Array.from(
        container.querySelectorAll<HTMLElement>(focusableSelectors)
      ).filter((el) => {
        // Filter out elements that are not visible
        return el.offsetParent !== null;
      });
    };

    // Auto-focus the first focusable element
    if (autoFocus) {
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        // Focus first element after a small delay to ensure rendering
        setTimeout(() => {
          focusableElements[0]?.focus();
        }, 50);
      }
    }

    // Handle Tab key to trap focus
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      const focusableElements = getFocusableElements();
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement as HTMLElement;

      // Shift + Tab (backwards)
      if (event.shiftKey) {
        if (activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      }
      // Tab (forwards)
      else {
        if (activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    // Add event listener
    container.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      container.removeEventListener('keydown', handleKeyDown);

      // Return focus to previously focused element
      if (returnFocus && previouslyFocusedElement.current) {
        previouslyFocusedElement.current.focus();
      }
    };
  }, [isActive, autoFocus, returnFocus]);

  return containerRef;
}
