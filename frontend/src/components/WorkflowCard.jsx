import { useState } from 'react';
import { Play, Clock, User, ChevronRight, Zap, Loader2 } from 'lucide-react';
import { updateNode } from '../services/api';

export default function WorkflowCard({ step, runAutomation, teamId }) {
    const defaultAuto = step.metadata?.auto_pilot || step.data?.auto_pilot || false;
    const [autoPilot, setAutoPilot] = useState(defaultAuto);
    const [updating, setUpdating] = useState(false);

    const toggleAutoPilot = async () => {
        if (!teamId) return;
        setUpdating(true);
        const newState = !autoPilot;
        try {
            // Use step.id (Visual) or step.step_id (DB row) - Graph uses 'id' usually mapped to step_id
            await updateNode(teamId, step.id, { auto_pilot: newState });
            setAutoPilot(newState);
        } catch (e) {
            console.error("Failed to toggle auto-pilot", e);
        }
        setUpdating(false);
    }

    return (
        <div className={`group relative bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border rounded-xl p-6 mb-4 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 ${autoPilot ? 'border-amber-400 dark:border-amber-500 ring-1 ring-amber-400/30' : 'border-gray-200 dark:border-gray-700'}`}>
            {/* Gradient accent */}
            <div className={`absolute top-0 left-0 w-1 h-full rounded-l-xl transition-opacity duration-300 ${autoPilot ? 'bg-amber-500 opacity-100' : 'bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-100'}`}></div>

            <div className="flex items-start justify-between">
                <div className="flex-1">
                    {/* Step title */}
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                        <ChevronRight className="w-5 h-5 text-blue-500" />
                        {step.step || step.data?.label || "Untitled Step"}
                        {autoPilot && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full border border-amber-200 flex items-center gap-1"><Zap className="w-3 h-3 fill-amber-500" /> Auto-Pilot</span>}
                    </h3>

                    {/* Description */}
                    {(step.description || step.data?.description) && (
                        <p className="text-gray-600 dark:text-gray-300 mb-3 leading-relaxed">
                            {step.description || step.data?.description}
                        </p>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            <span className="font-medium">{step.owner || step.data?.actor || "Unknown"}</span>
                        </div>

                        {step.timestamp && (
                            <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                <span>{new Date(step.timestamp).toLocaleDateString()}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 ml-4">
                    <button
                        onClick={() => runAutomation(step)}
                        className="flex items-center justify-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                    >
                        <Play className="w-4 h-4" />
                        Run
                    </button>

                    <button
                        onClick={toggleAutoPilot}
                        disabled={updating}
                        className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all border ${autoPilot ? 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'}`}
                    >
                        {updating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className={`w-3 h-3 ${autoPilot ? 'fill-amber-600' : ''}`} />}
                        {autoPilot ? 'Enabled' : 'Enable Auto'}
                    </button>
                </div>
            </div>

            {/* Hover effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
        </div>
    );
}
