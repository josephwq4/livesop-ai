import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Shield, Zap, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';

export default function Settings() {
    const { user, signOut } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
            <div className="max-w-4xl mx-auto">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                </button>

                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Settings</h1>

                {/* Profile Section */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400">
                            <User className="w-8 h-8" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Your Profile</h2>
                            <p className="text-gray-500">{user?.email}</p>
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full mt-1 inline-block">Active Subscription (Free)</span>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                </div>

                {/* Integrations Status */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div className="flex items-center gap-2 mb-6">
                        <Shield className="w-5 h-5 text-purple-600" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Integrations Status</h2>
                    </div>

                    <div className="space-y-4">
                        <IntegrationStatus name="Slack" status="connected" />
                        <IntegrationStatus name="Jira" status="connected" />
                        <IntegrationStatus name="Gmail" status="connected" />

                        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm rounded-lg flex gap-2">
                            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                            <p>Integrations are currently managed via System Environment Variables. To connect custom accounts, please contact support or upgrade to Enterprise.</p>
                        </div>
                    </div>
                </div>

                {/* Automation Config */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-center gap-2 mb-6">
                        <Zap className="w-5 h-5 text-amber-500" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Auto-Pilot Configuration</h2>
                    </div>

                    <div className="flex items-center justify-between p-4 border border-gray-100 dark:border-gray-700 rounded-lg">
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white">Node-Level Auto-Pilot</h3>
                            <p className="text-sm text-gray-500">Allow specific nodes to execute automatically when triggered.</p>
                        </div>
                        <div className="flex items-center gap-2 text-green-600 font-bold">
                            <CheckCircle className="w-5 h-5" /> Enabled
                        </div>
                    </div>

                    <p className="text-sm text-gray-500 mt-4">
                        Configure individual nodes in the Workflow Dashboard by toggling "Enable Auto".
                    </p>
                </div>
            </div>
        </div>
    );
}

function IntegrationStatus({ name, status }) {
    const isConnected = status === 'connected';
    return (
        <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-900/50">
            <span className="font-medium text-gray-700 dark:text-gray-300">{name}</span>
            <span className={`text-sm font-semibold flex items-center gap-1.5 ${isConnected ? 'text-green-600' : 'text-gray-400'}`}>
                {isConnected ? <CheckCircle className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
                {isConnected ? 'Connected' : 'Not Connected'}
            </span>
        </div>
    )
}
