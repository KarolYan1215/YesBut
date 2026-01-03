/**
 * 404 Not Found Page Component
 *
 * Displayed when a user navigates to a route that doesn't exist.
 *
 * @module app/not-found
 */

/**
 * Not found page component
 *
 * Displays a user-friendly 404 error page with:
 * - Clear "Page Not Found" message
 * - Helpful suggestions for navigation
 * - Link to return to home page
 * - Search functionality (optional)
 *
 * @returns The 404 page JSX element
 */
import Link from 'next/link';

export default function NotFound(): JSX.Element {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p className="text-gray-600 mb-4">Page Not Found</p>
      <Link href="/" className="text-blue-500 hover:underline">
        Return Home
      </Link>
    </div>
  );
}
