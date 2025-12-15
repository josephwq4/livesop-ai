import { useEffect, useState } from 'react';
import { fetchWorkflows, runAutomation, runInference, fetchSOP, fetchWorkflowHistory, searchKnowledge } from '../services/api';
import WorkflowCard from '../components/WorkflowCard';
import WorkflowSkeleton from '../components/WorkflowSkeleton';
import FlowChart from '../components/FlowChart';
import ReactMarkdown from 'react-markdown';
import {
    Workflow,
    Play,
    RefreshCw,
    FileText,
    Loader2,
    Sparkles,
    Network,
    List,
    History,
    Search,
    X,
    Shield
} from 'lucide-react';

import Navbar from '../components/Navbar';

export default function Dashboard() {
    const [workflow, setWorkflow] = useState(null);
    const [sop, setSop] = useState(null);
    const [loading, setLoading] = useState(true);
    const [inferring, setInferring] = useState(false);
    const [view, setView] = useState('cards'); // 'cards', 'flowchart', 'sop'
    const [notification, setNotification] = useState(null);
    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    // Search State
    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);

    const [realTeamId, setRealTeamId] = useState(null);

    const teamId = 'team123'; // Placeholder for API calls until AuthContext provides it

    useEffect(() => {
        loadWorkflows();
        loadHistory();
    }, []);

    // Real-time Subscription
    useEffect(() => {
        if (!realTeamId) return;

        // Import supabase client dynamically or expect it from import
        // We need to import it at top, I'll add import line separately.
        // Assuming imports exist.

        import('../lib/supabase').then(({ supabase }) => {
            if (!supabase) return;

            const channel = supabase
                .channel(`signals-${realTeamId}`)
                .on(
                    'postgres_changes',
                    {
                        event: 'INSERT',
                        schema: 'public',
                        table: 'raw_signals',
                        filter: `team_id=eq.${realTeamId}`
                    },
                    (payload) => {
                        const newSignal = payload.new;
                        showNotification(`New ${newSignal.source} signal: ${newSignal.content.substring(0, 40)}...`, 'info');
                    }
                )
                .subscribe();

            return () => {
                supabase.removeChannel(channel);
            };
        });
    }, [realTeamId]);

    const loadHistory = async () => {
        try {
            const data = await fetchWorkflowHistory(teamId);
            if (data.history) setHistory(data.history);
        } catch (error) {
            console.error('Error loading history:', error);
        }
    };

    const loadWorkflows = async (workflowId = null) => {
        try {
            setLoading(true);
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timeout')), 10000)
            );
            const dataPromise = fetchWorkflows(teamId, workflowId);

            const data = await Promise.race([dataPromise, timeoutPromise]);

            // Capture Real Team ID from Backend
            if (data.team_id) {
                setRealTeamId(data.team_id);
            }

            setWorkflow(data.workflow);
            setShowHistory(false);
        } catch (error) {
            console.error('Error loading workflows:', error);
            if (error.message !== 'Request timeout') {
                showNotification('Could not load workflows.', 'info');
            }
            setWorkflow({ nodes: [], edges: [] });
        } finally {
            setLoading(false);
        }
    };

    const handleRunInference = async () => {
        try {
            setInferring(true);

            // Add 60 second timeout for inference
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Inference timeout')), 60000)
            );
            const inferencePromise = runInference(teamId);

            const data = await Promise.race([inferencePromise, timeoutPromise]);

            setWorkflow(data.workflow);
            showNotification('Workflow inference completed successfully!', 'success');
        } catch (error) {
            console.error('Error running inference:', error);
            showNotification('Inference took too long or failed. Please try again.', 'error');
        } finally {
            setInferring(false);
        }
    };

    const handleRunAutomation = async (step) => {
        try {
            const label = (step.step || step.data?.label || "").toLowerCase();
            const desc = (step.description || step.data?.description || "");

            // Default Action: Slack Notification
            let payload = {
                action: 'slack_notify',
                params: {
                    message: `[Automation] Executed step: ${step.step || step.data?.label}`
                }
            };

            // Smart Heuristic: Detect Jira Intent
            if (label.includes('jira') || label.includes('ticket') || label.includes('issue')) {
                payload = {
                    action: 'create_jira_ticket',
                    params: {
                        summary: step.step || step.data?.label,
                        description: desc || "Created via LiveSOP Automation"
                    }
                };
            }

            const result = await runAutomation(teamId, payload);

            if (result.success) {
                showNotification(result.message, 'success');
                if (result.url) {
                    // Allow user to see the link (console for now, notification supported via message)
                    console.log("Created resource:", result.url);
                }
            } else {
                showNotification(`Automation failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Error running automation:', error);
            const msg = error.response?.data?.detail || error.message || 'Error running automation';
            showNotification(`Failed: ${msg}`, 'error');
        }
    };

    const handleLoadSOP = async () => {
        try {
            setLoading(true);
            const data = await fetchSOP(teamId);
            setSop(data.sop);
            setView('sop');
        } catch (error) {
            console.error('Error loading SOP:', error);
            showNotification('Error loading SOP', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;
        setIsSearching(true);
        try {
            const data = await searchKnowledge(teamId, searchQuery);
            if (data.results) setSearchResults(data.results);
        } catch (err) {
            console.error(err);
            showNotification('Search failed', 'error');
        } finally {
            setIsSearching(false);
        }
    };

    const showNotification = (message, type = 'info') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 5000);
    };

    if (loading && !workflow && !history.length) {
        // Only show full page loader if absolutely nothing is loaded
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
                <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
            {/* Navigation Bar */}
            <Navbar />

            {/* Notification */}
            {notification && (
                <div className={`fixed top-20 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 ${notification.type === 'success' ? 'bg-green-500' :
                    notification.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    } text-white font-semibold`}>
                    {notification.message}
                </div>
            )}

            {/* Header Actions */}
            <div className="max-w-7xl mx-auto px-6 pt-8 pb-2">
                <div className="flex items-center justify-end gap-3">
                    <button
                        onClick={() => setShowSearch(true)}
                        className="flex items-center gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-4 py-2.5 rounded-lg font-semibold shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 transition-all"
                    >
                        <Search className="w-5 h-5" />
                        Search
                    </button>
                    <button
                        onClick={() => setShowHistory(true)}
                        className="flex items-center gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-4 py-2.5 rounded-lg font-semibold shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 transition-all"
                    >
                        <History className="w-5 h-5" />
                        History
                    </button>
                    <button
                        onClick={handleRunInference}
                        disabled={inferring}
                        className="flex items-center gap-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                    >
                        {inferring ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Sparkles className="w-5 h-5" />
                        )}
                        {inferring ? 'Analyzing...' : 'Analyze Signals'}
                    </button>

                    <button
                        onClick={loadWorkflows}
                        className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 px-5 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                    >
                        <RefreshCw className="w-5 h-5" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* View Toggle */}
                <div className="flex items-center gap-2 mb-6 bg-white dark:bg-gray-800 p-2 rounded-xl shadow-md w-fit">
                    <button
                        onClick={() => setView('cards')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${view === 'cards'
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                            }`}
                    >
                        <List className="w-5 h-5" />
                        Cards
                    </button>

                    <button
                        onClick={() => setView('flowchart')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${view === 'flowchart'
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                            }`}
                    >
                        <Network className="w-5 h-5" />
                        Flowchart
                    </button>

                    <button
                        onClick={handleLoadSOP}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${view === 'sop'
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                            }`}
                    >
                        <FileText className="w-5 h-5" />
                        SOP
                    </button>
                </div>

                {/* Content Area */}
                {!workflow || !workflow.nodes || workflow.nodes.length === 0 ? (
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-12 text-center border border-gray-200 dark:border-gray-700">
                        <div className="bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Workflow className="w-12 h-12 text-blue-600 dark:text-blue-400" />
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                            No Automations Configured
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                            LiveSOP is monitoring your integration signals. Once a resolution pattern is detected, it will appear here for your review.
                        </p>

                        <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-8 bg-gray-50 dark:bg-gray-900/50 py-2 px-4 rounded-full w-fit mx-auto">
                            <Shield className="w-4 h-4 ml-1" />
                            <span>You are in control. Automations require approval unless Auto-Pilot is enabled.</span>
                        </div>

                        <button
                            onClick={handleRunInference}
                            disabled={inferring}
                            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 transform hover:scale-105"
                        >
                            {inferring ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Sparkles className="w-5 h-5" />
                            )}
                            {inferring ? 'Processing...' : 'Create Workflow'}
                        </button>
                    </div>
                ) : (
                    <>
                        {view === 'cards' && (
                            <div className="space-y-4">
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                    <Play className="w-6 h-6 text-blue-600" />
                                    Workflow Steps
                                </h2>
                                {workflow.nodes.map((step) => (
                                    <WorkflowCard
                                        key={step.id}
                                        step={step}
                                        runAutomation={handleRunAutomation}
                                        teamId={realTeamId}
                                    />
                                ))}
                            </div>
                        )}

                        {view === 'flowchart' && (
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                    <Network className="w-6 h-6 text-purple-600" />
                                    Workflow Visualization
                                </h2>
                                <FlowChart workflow={workflow} />
                            </div>
                        )}

                        {view === 'sop' && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                                    <FileText className="w-6 h-6 text-green-600" />
                                    Living SOP Document
                                </h2>
                                {sop ? (
                                    <div className="prose prose-lg dark:prose-invert max-w-none">
                                        <ReactMarkdown>{sop}</ReactMarkdown>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center py-12">
                                        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </div>
            {/* History Drawer */}
            {showHistory && (
                <div className="fixed inset-0 z-50 flex justify-end">
                    {/* Backdrop */}
                    <div
                        className="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity"
                        onClick={() => setShowHistory(false)}
                    ></div>

                    {/* Drawer */}
                    <div className="relative w-96 bg-white dark:bg-gray-900 h-full shadow-2xl p-6 overflow-y-auto border-l border-gray-200 dark:border-gray-700 animate-slide-in-right">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
                                <History className="w-5 h-5" />
                                Version History
                            </h2>
                            <button onClick={() => setShowHistory(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full">
                                <X className="w-5 h-5 dark:text-white" />
                            </button>
                        </div>

                        <div className="space-y-3">
                            {history.map((h) => (
                                <div
                                    key={h.id}
                                    onClick={() => loadWorkflows(h.id)}
                                    className={`p-4 rounded-xl border cursor-pointer transition-all hover:shadow-md ${workflow?.workflow_id === h.id
                                        ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700'
                                        : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 hover:border-blue-200'
                                        }`}
                                >
                                    <div className="font-semibold text-gray-900 dark:text-white mb-1">
                                        {h.title || "Untitled Workflow"}
                                    </div>
                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                        <span>{new Date(h.created_at).toLocaleString()}</span>
                                        {h.is_active && (
                                            <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                                                Active
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Search Modal */}
            {showSearch && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowSearch(false)}></div>
                    <div className="relative bg-white dark:bg-gray-900 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden animate-slide-up">
                        <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
                            <h2 className="text-xl font-bold flex items-center gap-2 dark:text-white">
                                <Search className="w-5 h-5 text-blue-600" />
                                Smart Knowledge Base
                            </h2>
                            <button onClick={() => setShowSearch(false)}><X className="w-5 h-5 dark:text-gray-400" /></button>
                        </div>
                        <div className="p-6">
                            <form onSubmit={handleSearch} className="flex gap-2 mb-6">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search past resolutions or context..."
                                    className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                                <button
                                    type="submit"
                                    disabled={isSearching}
                                    className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50"
                                >
                                    {isSearching ? <Loader2 className="animate-spin" /> : 'Search'}
                                </button>
                            </form>

                            <div className="space-y-4 max-h-[60vh] overflow-y-auto">
                                {searchResults.map((res) => (
                                    <div key={res.id} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                                        <div className="text-sm text-gray-500 mb-2 flex justify-between">
                                            <span>Similarity: {(res.similarity * 100).toFixed(1)}%</span>
                                            <span>{new Date(res.occurred_at).toLocaleString()}</span>
                                        </div>
                                        <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                                            {res.content}
                                        </p>
                                    </div>
                                ))}
                                {searchResults.length === 0 && !isSearching && searchQuery && (
                                    <div className="text-center text-gray-400 py-8">No relevant context found.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
