/**
 * Global Loading Component
 *
 * Displayed automatically by Next.js when navigating between routes
 * while the new page is being loaded.
 *
 * @module app/loading
 */

/**
 * Global loading state component
 *
 * Renders a full-page loading indicator with:
 * - Centered spinner animation
 * - YesBut logo
 * - Optional loading message
 *
 * This component is automatically shown by Next.js App Router
 * during route transitions.
 *
 * @returns The loading state JSX element
 */
export default function Loading(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
    </div>
  );
}
