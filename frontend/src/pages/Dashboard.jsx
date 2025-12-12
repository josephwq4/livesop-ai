import { useEffect, useState } from 'react';
import { fetchWorkflows, runAutomation, runInference, fetchSOP } from '../services/api';
import WorkflowCard from '../components/WorkflowCard';
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
    List
} from 'lucide-react';

import Navbar from '../components/Navbar';

export default function Dashboard() {
    const [workflow, setWorkflow] = useState(null);
    const [sop, setSop] = useState(null);
    const [loading, setLoading] = useState(true);
    const [inferring, setInferring] = useState(false);
    const [view, setView] = useState('cards'); // 'cards', 'flowchart', 'sop'
    const [notification, setNotification] = useState(null);

    const teamId = 'team123'; // In production, get from auth context

    useEffect(() => {
        loadWorkflows();
    }, []);

    const loadWorkflows = async () => {
        try {
            setLoading(true);
            // Add timeout to prevent hanging
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timeout')), 10000)
            );
            const dataPromise = fetchWorkflows(teamId);

            const data = await Promise.race([dataPromise, timeoutPromise]);
            setWorkflow(data.workflow);
        } catch (error) {
            console.error('Error loading workflows:', error);
            // Don't show error on initial load if just empty
            if (error.message !== 'Request timeout') {
                showNotification('Could not load workflows. Click "Run Inference" to generate.', 'info');
            }
            // Set empty workflow so page doesn't hang
            setWorkflow({ nodes: [], edges: [] });
        } finally {
            setLoading(false);
        }
    };

    const handleRunInference = async () => {
        try {
            setInferring(true);

            // Add 15 second timeout for inference
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Inference timeout')), 15000)
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

    const handleRunAutomation = async (workflowId) => {
        try {
            const result = await runAutomation(teamId, workflowId);
            if (result.success) {
                showNotification(`Automation executed successfully!`, 'success');
            } else {
                showNotification('Automation failed', 'error');
            }
        } catch (error) {
            console.error('Error running automation:', error);
            showNotification('Error running automation', 'error');
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

    const showNotification = (message, type = 'info') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 5000);
    };

    if (loading && !workflow) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-300 text-lg">Loading workflows...</p>
                </div>
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
                        onClick={handleRunInference}
                        disabled={inferring}
                        className="flex items-center gap-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                    >
                        {inferring ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Sparkles className="w-5 h-5" />
                        )}
                        {inferring ? 'Inferring...' : 'Run Inference'}
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
                            No Workflows Yet
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                            Connect your integrations or import data, then run inference to generate AI-powered workflows.
                        </p>
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
                            {inferring ? 'Generating...' : 'Generate Workflow'}
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
        </div>
    );
}
