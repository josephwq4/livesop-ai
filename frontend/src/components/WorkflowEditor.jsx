import { useState, useRef } from 'react';
import FlowChart from './FlowChart';
import { updateWorkflowNodes } from '../services/api';
import { Edit, Save, X, Plus, Trash2, Settings, Zap } from 'lucide-react';

export default function WorkflowEditor({ workflow, teamId, onRefresh }) {
    const [isEditing, setIsEditing] = useState(false);
    const [selectedNode, setSelectedNode] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const flowChartRef = useRef(null);

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const nodes = flowChartRef.current.getNodes();
            // Prepare payload
            const payload = nodes.map(n => ({
                id: n.id,
                label: n.data.label,
                metadata: {
                    ...n.data,
                    position: n.position
                },
                auto_run_enabled: n.data.auto_run_enabled,
                description: n.data.description
            }));

            await updateWorkflowNodes(teamId, workflow.workflow_id, payload);
            setIsEditing(false);
            if (onRefresh) onRefresh();
        } catch (e) {
            console.error(e);
            alert("Failed to save workflow");
        } finally {
            setIsSaving(false);
        }
    };

    const handleNodeUpdate = (key, value) => {
        if (!selectedNode) return;
        flowChartRef.current.updateNodeData(selectedNode.id, { [key]: value });
        // Update local selected node state too so input reflects change
        setSelectedNode(prev => ({ ...prev, data: { ...prev.data, [key]: value } }));
    };

    const handleDeleteNode = () => {
        if (!selectedNode) return;
        if (confirm("Delete this step?")) {
            flowChartRef.current.removeNode(selectedNode.id);
            setSelectedNode(null);
        }
    }

    return (
        <div className="relative h-[700px] flex flex-col bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Toolbar */}
            <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-2">
                    <h3 className="font-bold text-gray-700 dark:text-gray-200">Workflow Designer</h3>
                    {!isEditing && (
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded text-gray-500">Read Only</span>
                    )}
                    {isEditing && (
                        <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded font-bold animate-pulse">Editing Mode</span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {!isEditing ? (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-500 transition-colors text-sm font-semibold"
                        >
                            <Edit className="w-4 h-4" /> Edit Workflow
                        </button>
                    ) : (
                        <>
                            <button
                                onClick={() => flowChartRef.current.addNode()}
                                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg text-gray-600"
                                title="Add Step"
                            >
                                <Plus className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => { setIsEditing(false); setSelectedNode(null); }}
                                className="px-4 py-2 text-gray-500 hover:text-gray-700 font-medium text-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={isSaving}
                                className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold shadow-md transition-all text-sm"
                            >
                                {isSaving ? "Saving..." : <><Save className="w-4 h-4" /> Save Changes</>}
                            </button>
                        </>
                    )}
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Canvas */}
                <div className="flex-1 relative">
                    <FlowChart
                        ref={flowChartRef}
                        workflow={workflow}
                        isEditing={isEditing}
                        onNodeSelect={(node) => isEditing && setSelectedNode(node)}
                    />
                </div>

                {/* Sidebar Properties */}
                {isEditing && selectedNode && (
                    <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto animate-slide-in-right z-10 shadow-xl">
                        <div className="flex items-center justify-between mb-6">
                            <h4 className="font-bold text-lg dark:text-white flex items-center gap-2">
                                <Settings className="w-5 h-5" /> Step Settings
                            </h4>
                            <button onClick={() => setSelectedNode(null)}><X className="w-5 h-5 text-gray-400" /></button>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Step Label</label>
                                <input
                                    type="text"
                                    className="w-full p-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 dark:text-white text-sm font-medium"
                                    value={selectedNode.data.label || ""}
                                    placeholder="e.g. Check Logs"
                                    onChange={(e) => handleNodeUpdate('label', e.target.value)}
                                />
                                <div className="text-xs text-gray-400 mt-1">Short name for the flowchart card.</div>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Instructions (Prompt)</label>
                                <textarea
                                    rows="4"
                                    className="w-full p-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 dark:text-white text-sm"
                                    value={selectedNode.data.description || ""}
                                    onChange={(e) => handleNodeUpdate('description', e.target.value)}
                                    placeholder="Detailed instructions for the AI..."
                                />
                            </div>

                            <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                        <Zap className={`w-4 h-4 ${selectedNode.data.auto_run_enabled ? 'text-amber-500' : 'text-gray-400'}`} />
                                        Auto-Pilot
                                    </label>
                                    <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                                        <input
                                            type="checkbox"
                                            id="toggle"
                                            className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer"
                                            checked={selectedNode.data.auto_run_enabled || false}
                                            onChange={(e) => handleNodeUpdate('auto_run_enabled', e.target.checked)}
                                            style={{ right: selectedNode.data.auto_run_enabled ? '0' : 'auto', left: selectedNode.data.auto_run_enabled ? 'auto' : '0', borderColor: selectedNode.data.auto_run_enabled ? '#f59e0b' : '#d1d5db' }}
                                        />
                                        <label htmlFor="toggle" className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer ${selectedNode.data.auto_run_enabled ? 'bg-amber-500' : 'bg-gray-300'}`}></label>
                                    </div>
                                </div>
                                <p className="text-xs text-gray-500 leading-tight">
                                    If enabled, AI will execute this step automatically if confidence > 90%.
                                </p>
                            </div>

                            <div className="pt-6 border-t border-gray-100 dark:border-gray-700">
                                <button
                                    onClick={handleDeleteNode}
                                    className="w-full py-3 flex items-center justify-center gap-2 text-red-600 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/40 rounded-lg font-semibold transition-colors text-sm"
                                >
                                    <Trash2 className="w-4 h-4" /> Delete Step
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
