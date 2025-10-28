import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🔐 Universal OAuth SDK
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Next.js 14 App Router Example
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Link
              href="/auth/google"
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-4 px-6 rounded-lg text-center transition-colors"
            >
              Sign in with Google
            </Link>
            <Link
              href="/auth/github"
              className="bg-gray-800 hover:bg-gray-900 text-white font-semibold py-4 px-6 rounded-lg text-center transition-colors"
            >
              Sign in with GitHub
            </Link>
            <Link
              href="/auth/microsoft"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg text-center transition-colors"
            >
              Sign in with Microsoft
            </Link>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Features</h2>
            <ul className="space-y-2 text-gray-700">
              <li>✅ Next.js 14 App Router</li>
              <li>✅ Server-side OAuth flow</li>
              <li>✅ Secure token storage</li>
              <li>✅ Automatic token refresh</li>
              <li>✅ TypeScript support</li>
              <li>✅ Tailwind CSS styling</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  );
}
