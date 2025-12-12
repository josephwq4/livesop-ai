import { Link, useLocation } from 'react-router-dom';
import { Workflow, Settings, LogOut } from 'lucide-react';

export default function Navbar() {
    const location = useLocation();

    return (
        <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center gap-3">
                        <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg shadow-md">
                            <Workflow className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            LiveSOP AI
                        </span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center gap-6">
                        <Link
                            to="/dashboard"
                            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === '/dashboard'
                                    ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                                    : 'text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400'
                                }`}
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/integrations"
                            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === '/integrations'
                                    ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                                    : 'text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400'
                                }`}
                        >
                            Integrations
                        </Link>
                    </div>

                    {/* Right Side */}
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                            TM
                        </div>
                        <Link to="/" className="text-gray-500 hover:text-red-500 transition-colors">
                            <LogOut className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}
