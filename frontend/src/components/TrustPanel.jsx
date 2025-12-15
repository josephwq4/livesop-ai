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
                {/* Header */}
                <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-start bg-gray-50/50 dark:bg-gray-800/50">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${escalation.confidence > 0.8
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                    : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                                }`}>
                                {escalation.confidence > 0.8 ? 'High Confidence' : 'Review Needed'}
                            </span>
                            <span className="text-xs text-gray-500">{new Date(escalation.time).toLocaleString()}</span>
                        </div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white leading-tight">
                            Escalation Detected
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 p-6 space-y-8">

                    {/* Why this matched */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Why it matched
                        </h3>
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl border border-blue-100 dark:border-blue-800 text-sm text-blue-900 dark:text-blue-100 leading-relaxed">
                            {escalation.rationale || "The content matched the configured intent patterns for 'High Priority Bug' and was posted in a tracked support channel."}
                        </div>
                    </div>

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
