import { useState } from 'react';
import { LogIn, Sparkles, Workflow, Zap, Shield } from 'lucide-react';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        // Simulate login - in production, call actual auth API
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 flex items-center justify-center p-6">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-300/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
            </div>

            <div className="relative w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
                {/* Left side - Branding */}
                <div className="text-white space-y-6 hidden md:block">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="bg-white/20 backdrop-blur-lg p-4 rounded-2xl shadow-2xl">
                            <Workflow className="w-12 h-12" />
                        </div>
                        <div>
                            <h1 className="text-5xl font-bold">LiveSOP AI</h1>
                            <p className="text-blue-100 text-lg">Workflow Intelligence Platform</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-start gap-4 bg-white/10 backdrop-blur-lg p-4 rounded-xl">
                            <div className="bg-blue-500/30 p-3 rounded-lg">
                                <Sparkles className="w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="font-bold text-lg mb-1">AI-Powered Inference</h3>
                                <p className="text-blue-100">Automatically discover workflows from team activities</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 bg-white/10 backdrop-blur-lg p-4 rounded-xl">
                            <div className="bg-purple-500/30 p-3 rounded-lg">
                                <Zap className="w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="font-bold text-lg mb-1">One-Click Automation</h3>
                                <p className="text-blue-100">Execute complex workflows with a single click</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 bg-white/10 backdrop-blur-lg p-4 rounded-xl">
                            <div className="bg-pink-500/30 p-3 rounded-lg">
                                <Shield className="w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="font-bold text-lg mb-1">Living SOPs</h3>
                                <p className="text-blue-100">Dynamic documentation that evolves with your team</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right side - Login form */}
                <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl p-8 md:p-12">
                    <div className="mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                            Welcome Back
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400">
                            Sign in to access your workflow dashboard
                        </p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 outline-none"
                                placeholder="you@company.com"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 outline-none"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span className="text-sm text-gray-600 dark:text-gray-400">Remember me</span>
                            </label>
                            <a href="#" className="text-sm font-semibold text-blue-600 hover:text-blue-700">
                                Forgot password?
                            </a>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-4 rounded-lg font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02]"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    <LogIn className="w-5 h-5" />
                                    Sign In
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-gray-600 dark:text-gray-400">
                            Don't have an account?{' '}
                            <a href="#" className="font-semibold text-blue-600 hover:text-blue-700">
                                Start free trial
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
