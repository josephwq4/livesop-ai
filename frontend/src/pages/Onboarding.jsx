import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Slack,
    Database,
    CheckCircle,
    ArrowRight,
    Loader2,
    Shield,
    GitGraph,
    Zap,
    Play
} from 'lucide-react';
import { fetchSlackEvents, fetchJiraIssues } from '../services/api';

export default function Onboarding() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // State for data
    const [slackConnected, setSlackConnected] = useState(false);
    const [jiraConnected, setJiraConnected] = useState(false);
    const [selectedChannel, setSelectedChannel] = useState('');
    const [selectedProject, setSelectedProject] = useState('');
    const [autoPilot, setAutoPilot] = useState(false);

    const handleSlackConnect = async () => {
        setLoading(true);
        // Simulate connection delay or actually call API if token available
        setTimeout(() => {
            setSlackConnected(true);
            setLoading(false);
            setStep(2);
        }, 1500);
    };

    const handleJiraConnect = async () => {
        setLoading(true);
        setTimeout(() => {
            setJiraConnected(true);
            setLoading(false);
            setStep(3);
        }, 1500);
    };

    const handleFinish = () => {
        // Save preferences (In a real app, post to channel_configs)
        setLoading(true);
        setTimeout(() => {
            navigate('/dashboard');
        }, 1000);
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-6">
            <div className="w-full max-w-4xl bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row min-h-[600px]">

                {/* Left Sidebar (Progress) */}
                <div className="w-full md:w-1/3 bg-gray-50 dark:bg-gray-900 p-8 border-r border-gray-100 dark:border-gray-700">
                    <div className="mb-10">
                        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center mb-4">
                            <GitGraph className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Setup Pilot</h1>
                        <p className="text-gray-500 dark:text-gray-400 text-sm mt-2">
                            Configure your first automated escalation workflow.
                        </p>
                    </div>

                    <div className="space-y-6 relative">
                        {/* Connecting Line */}
                        <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-gray-200 dark:bg-gray-700 z-0"></div>

                        <ProgressStep
                            num={1}
                            active={step === 1}
                            completed={step > 1}
                            title="Connect Slack"
                            desc="Ingest support threads"
                        />
                        <ProgressStep
                            num={2}
                            active={step === 2}
                            completed={step > 2}
                            title="Connect Jira"
                            desc="Link issue tracker"
                        />
                        <ProgressStep
                            num={3}
                            active={step === 3}
                            completed={step > 3}
                            title="Configure Workflow"
                            desc="Tier-3 Escalation"
                        />
                        <ProgressStep
                            num={4}
                            active={step === 4}
                            completed={step > 4}
                            title="Validation"
                            desc="Review & Launch"
                        />
                    </div>
                </div>

                {/* Right Content */}
                <div className="w-full md:w-2/3 p-8 md:p-12 flex flex-col">
                    <div className="flex-1 flex flex-col justify-center">

                        {/* STEP 1: SLACK */}
                        {step === 1 && (
                            <div className="animate-fade-in-up">
                                <div className="bg-blue-50 dark:bg-blue-900/20 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-blue-600 dark:text-blue-400">
                                    <Slack className="w-8 h-8" />
                                </div>
                                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Connect Support Channels</h2>
                                <p className="text-gray-600 dark:text-gray-300 text-lg mb-8">
                                    LiveSOP needs to observe your public support channels to learn how your team resolves issues.
                                </p>
                                <button
                                    onClick={handleSlackConnect}
                                    disabled={loading}
                                    className="bg-[#4A154B] hover:bg-[#3f1140] text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-3 transition-transform hover:scale-105"
                                >
                                    {loading ? <Loader2 className="animate-spin" /> : <Slack className="w-5 h-5" />}
                                    Connect Workspace
                                </button>
                            </div>
                        )}

                        {/* STEP 2: JIRA */}
                        {step === 2 && (
                            <div className="animate-fade-in-up">
                                <div className="bg-blue-50 dark:bg-blue-900/20 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-blue-600 dark:text-blue-400">
                                    <Database className="w-8 h-8" />
                                </div>
                                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Connect Issue Tracker</h2>
                                <p className="text-gray-600 dark:text-gray-300 text-lg mb-8">
                                    We'll analyze your Jira tickets to map solutions back to recurring questions.
                                </p>
                                <button
                                    onClick={handleJiraConnect}
                                    disabled={loading}
                                    className="bg-[#0052CC] hover:bg-[#0047b3] text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-3 transition-transform hover:scale-105"
                                >
                                    {loading ? <Loader2 className="animate-spin" /> : <Database className="w-5 h-5" />}
                                    Connect Jira Cloud
                                </button>
                                <div className="mt-4 text-center">
                                    <button onClick={() => setStep(3)} className="text-gray-400 hover:text-gray-600 text-sm">Skip for now</button>
                                </div>
                            </div>
                        )}

                        {/* STEP 3: CONFIGURE */}
                        {step === 3 && (
                            <div className="animate-fade-in-up">
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Setup Escalation Workflow</h2>

                                <div className="space-y-4 mb-8">
                                    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-blue-500 cursor-pointer transition-colors bg-white dark:bg-gray-800">
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Watch Channel</label>
                                        <select
                                            className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700"
                                            value={selectedChannel}
                                            onChange={(e) => setSelectedChannel(e.target.value)}
                                        >
                                            <option value="">Select a channel...</option>
                                            <option value="C123">#support-tier3 (Recommended)</option>
                                            <option value="C456">#engineering</option>
                                            <option value="C789">#general</option>
                                        </select>
                                    </div>

                                    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-blue-500 cursor-pointer transition-colors bg-white dark:bg-gray-800">
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Target Jira Project</label>
                                        <select
                                            className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700"
                                            value={selectedProject}
                                            onChange={(e) => setSelectedProject(e.target.value)}
                                        >
                                            <option value="">Select a project...</option>
                                            <option value="PROJ">PROJ (Core App)</option>
                                            <option value="SUP">SUP (Support)</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    onClick={() => setStep(4)}
                                    disabled={!selectedChannel}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Continue <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>
                        )}

                        {/* STEP 4: VALIDATION */}
                        {step === 4 && (
                            <div className="animate-fade-in-up">
                                <div className="text-center mb-8">
                                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Ready to Launch 🚀</h2>
                                    <p className="text-gray-500">Review your automated escalation configuration.</p>
                                </div>

                                <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 mb-8 border border-gray-200 dark:border-gray-700">
                                    <div className="flex items-start gap-4 mb-4">
                                        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 shrink-0">
                                            <Play className="w-5 h-5 ml-1" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900 dark:text-white">Trigger</h3>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">When message in <strong>#support-tier3</strong> matches "Bug Report" pattern...</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-4">
                                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 shrink-0">
                                            <Database className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900 dark:text-white">Action</h3>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">Draft Jira Ticket in <strong>{selectedProject || 'PROJ'}</strong> (Requires Approval)</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 mb-8 p-4 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-800 rounded-lg">
                                    <input
                                        type="checkbox"
                                        id="autopilot"
                                        className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        checked={autoPilot}
                                        onChange={(e) => setAutoPilot(e.target.checked)}
                                    />
                                    <label htmlFor="autopilot" className="text-sm text-gray-700 dark:text-gray-300 select-none cursor-pointer">
                                        <strong>Enable Auto-Pilot</strong> (High confidence matches executed automatically)
                                    </label>
                                </div>

                                <button
                                    onClick={handleFinish}
                                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all"
                                >
                                    Activate Workflow
                                </button>
                            </div>
                        )}

                    </div>
                </div>
            </div>
        </div>
    );
}

// Helper Component
function ProgressStep({ num, active, completed, title, desc }) {
    return (
        <div className={`relative z-10 flex items-center gap-4 group ${active ? 'opacity-100' : 'opacity-60'}`}>
            <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300
                ${completed
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : active
                        ? 'bg-white border-blue-600 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-300'}
            `}>
                {completed ? <CheckCircle className="w-5 h-5" /> : num}
            </div>
            <div>
                <h3 className={`font-semibold ${active ? 'text-blue-600' : 'text-gray-700 dark:text-gray-300'}`}>{title}</h3>
                <p className="text-xs text-gray-500">{desc}</p>
            </div>
        </div>
    );
}
