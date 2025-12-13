import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Loader2, AlertCircle } from 'lucide-react';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [isSignUp, setIsSignUp] = useState(false);

    const { signIn, signUp } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (isSignUp) {
                const { error } = await signUp({ email, password });
                if (error) throw error;
                alert('Success! Check your email for the confirmation link.');
            } else {
                const { error } = await signIn({ email, password });
                if (error) throw error;
                navigate('/dashboard');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
            <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg mb-4">
                        <Lock className="h-6 w-6 text-white" />
                    </div>
                    <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">
                        {isSignUp ? 'Create an account' : 'Welcome back'}
                    </h2>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {isSignUp ? 'Sign up to get started' : 'Sign in to your account'}
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div className="relative">
                            <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 text-gray-900 dark:text-gray-200 dark:bg-gray-700 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                                placeholder="Email address"
                            />
                        </div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 text-gray-900 dark:text-gray-200 dark:bg-gray-700 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                                placeholder="Password"
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all duration-200"
                        >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isSignUp ? 'Sign Up' : 'Sign In')}
                        </button>
                    </div>

                    <div className="text-center">
                        <button
                            type="button"
                            onClick={() => setIsSignUp(!isSignUp)}
                            className="text-sm text-blue-600 hover:text-blue-500 font-medium"
                        >
                            {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
