import { Handle, Position } from 'reactflow';

export default function SOPNode({ data, isConnectable }) {
    // Determine visuals
    const isAutoRun = data.auto_run_enabled;
    const gradient = isAutoRun
        ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
        : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

    return (
        <div className="shadow-lg rounded-xl overflow-hidden min-w-[200px]" style={{ background: gradient }}>
            <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="!bg-white" />

            <div className="p-4 text-white">
                <div className="font-bold text-sm mb-1">{data.label}</div>
                <div className="text-xs text-white/80 flex items-center justify-between">
                    <span>{data.owner || "AI Agent"}</span>
                    {isAutoRun && <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-bold">AUTO</span>}
                </div>
            </div>

            <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="!bg-white" />
        </div>
    );
}
