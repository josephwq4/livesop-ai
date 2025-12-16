import { useRef, useEffect } from 'react';
import { X, Shield, ExternalLink, Zap, CheckCircle, AlertTriangle } from 'lucide-react';

export default function TrustPanel({ escalation, onClose, onAction, autoPilot }) {
    const panelRef = useRef(null);

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (panelRef.current && !panelRef.current.contains(event.target)) {
                onClose();
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [onClose]);

    if (!escalation) return null;

    return (
        <div className="fixed inset-0 z-[60] flex justify-end">
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity" />

            <div
                ref={panelRef}
                className="relative w-full max-w-md bg-white dark:bg-gray-900 h-full shadow-2xl overflow-y-auto border-l border-gray-200 dark:border-gray-700 animate-slide-in-right flex flex-col"
            >
                {/* Header - Premium Design */}
                <div className="relative p-6 border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 pb-8">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>

                    <div className="flex flex-col gap-1 mb-6">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                            AI Confidence Score
                        </span>
                        <div className="flex items-baseline gap-3">
                            <h1 className={`text-5xl font-black tracking-tight ${escalation.confidence > 0.8
                                    ? 'text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-emerald-600'
                                    : 'text-amber-500'
                                }`}>
                                {Math.round(escalation.confidence * 100)}%
                            </h1>
                            <div className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide border ${escalation.confidence > 0.8
                                    ? 'bg-green-50 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
                                    : 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-400'
                                }`}>
                                {escalation.confidence > 0.8 ? 'High Certainty' : 'Review Needed'}
                            </div>
                        </div>
                    </div>

                    {/* Reasoning Box */}
                    <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
                        <div className="flex items-center gap-2 mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider">
                            <Shield className="w-3 h-3" />
                            AI Reasoning
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed font-medium">
                            {escalation.rationale}
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 p-6 space-y-8 overflow-y-auto">
                    {/* Source Context */}

                    {/* Source Context */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                            Source Context
                        </h3>
                        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-sm">
                            <div className="flex items-center gap-3 mb-3 pb-3 border-b border-gray-100 dark:border-gray-700">
                                <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs">
                                    {(escalation.customer || "U").charAt(0).toUpperCase()}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">{escalation.customer}</p>
                                    <p className="text-xs text-gray-500 truncate">in #{escalation.channel}</p>
                                </div>
                                {escalation.link && (
                                    <a
                                        href={escalation.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400 p-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg"
                                        title="View in Slack"
                                    >
                                        <ExternalLink className="w-4 h-4" />
                                    </a>
                                )}
                            </div>
                            <blockquote className="text-gray-700 dark:text-gray-300 text-sm italic border-l-2 border-gray-300 pl-3">
                                "{escalation.content}"
                            </blockquote>
                        </div>
                    </div>

                    {/* Action Taken */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                            Outcome
                        </h3>
                        <div className="flex items-start gap-3">
                            <div className={`mt-1 w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${escalation.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'
                                }`}>
                                {escalation.status === 'completed' ? <CheckCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                            </div>
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white text-sm">
                                    Action: {escalation.action}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    {autoPilot
                                        ? "Executed automatically because confidence > 90% (Auto-Pilot Active)."
                                        : "Pending approval (Auto-Pilot Disabled)."
                                    }
                                </p>
                            </div>
                        </div>
                    </div>

                </div>

                {/* Footer Controls */}
                <div className="p-6 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-orange-500" />
                            Auto-Pilot for this pattern
                        </span>
                        <div
                            className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors ${autoPilot ? 'bg-green-500' : 'bg-gray-300'}`}
                            onClick={() => onAction('toggle_autopilot')}
                        >
                            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform ${autoPilot ? 'translate-x-6' : 'translate-x-0'}`} />
                        </div>
                    </div>
                    <p className="text-xs text-gray-500 mb-4">
                        When enabled, future escalations matching this specific pattern with high confidence will run without approval.
                    </p>

                    <button
                        className="w-full bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-white font-semibold py-2.5 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors shadow-sm"
                        onClick={onClose}
                    >
                        Close Panel
                    </button>
                </div>
            </div>
        </div>
    );
}
