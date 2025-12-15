import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Workflow, Settings, LogOut, Zap } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getTeamUsage } from '../services/api';

export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const { signOut } = useAuth();
    const [usage, setUsage] = useState(null);

    useEffect(() => {
        getTeamUsage().then(data => {
            if (data.success) setUsage(data.usage);
        }).catch(err => console.error("Failed to load usage", err));
    }, []);

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

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
                        {/* Integrations Link Removed - merged into Settings or separate page, keeping as is if user wants but Phase A spec was Dashboard + Settings */}
                        {/* Keeping Integrations link as per previous file, no instruction to remove */}
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
                        {/* Always show usage, default to trial state if loading/error */}
                        <Link to="/settings" className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold mr-2 border transition-all hover:scale-105 ${usage && (usage.automation_count / usage.automation_limit) > 0.9
                            ? 'bg-red-50 text-red-600 border-red-200 animate-pulse'
                            : 'bg-green-50 text-green-700 border-green-200'
                            }`}>
                            <Zap className="w-3 h-3" />
                            {usage ? usage.automation_count : 0} / {usage ? usage.automation_limit : 100}
                            <span className="opacity-75 uppercase text-[10px] ml-1">{usage ? usage.plan_tier : 'TRIAL'}</span>
                        </Link>

                        <Link
                            to="/settings"
                            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                            title="Settings"
                        >
                            <Settings className="w-5 h-5" />
                        </Link>

                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                            TM
                        </div>

                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
                            title="Sign Out"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
