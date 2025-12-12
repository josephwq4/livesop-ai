import { Play, Clock, User, ChevronRight } from 'lucide-react';

export default function WorkflowCard({ step, runAutomation }) {
    return (
        <div className="group relative bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-6 mb-4 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            {/* Gradient accent */}
            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500 rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

            <div className="flex items-start justify-between">
                <div className="flex-1">
                    {/* Step title */}
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                        <ChevronRight className="w-5 h-5 text-blue-500" />
                        {step.step}
                    </h3>

                    {/* Description */}
                    {step.description && (
                        <p className="text-gray-600 dark:text-gray-300 mb-3 leading-relaxed">
                            {step.description}
                        </p>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            <span className="font-medium">{step.owner}</span>
                        </div>

                        {step.timestamp && (
                            <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                <span>{new Date(step.timestamp).toLocaleDateString()}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Action button */}
                <button
                    onClick={() => runAutomation(step.id)}
                    className="ml-4 flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                >
                    <Play className="w-4 h-4" />
                    Run
                </button>
            </div>

            {/* Hover effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
        </div>
    );
}
