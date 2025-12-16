import { useState, useEffect } from 'react';
import api from '../services/api';
import { Trash2, FileText, Plus, Upload, Loader2, Book } from 'lucide-react';

export default function KnowledgeBase({ teamId }) {
    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [newText, setNewText] = useState("");
    const [isAdding, setIsAdding] = useState(false);

    useEffect(() => {
        if (teamId) loadDocs();
    }, [teamId]);

    const loadDocs = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/knowledge/${teamId}/knowledge`);
            if (res.data.success) {
                setDocs(res.data.documents);
            }
        } catch (e) {
            console.error("Failed to load KB", e);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async () => {
        if (!newText.trim()) return;
        setUploading(true);
        try {
            const formData = new FormData();
            formData.append("text", newText);
            formData.append("source_type", "manual_entry");

            await api.post(`/knowledge/${teamId}/knowledge`, formData);
            setNewText("");
            setIsAdding(false);
            loadDocs();
        } catch (e) {
            alert("Failed to upload: " + e.message);
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Delete this document? AI will no longer use it for context.")) return;
        try {
            await api.delete(`/knowledge/${teamId}/knowledge/${id}`);
            loadDocs();
        } catch (e) {
            console.error(e);
        }
    }

    return (
        <div className="animate-fade-in-up">
            <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Book className="w-6 h-6 text-blue-600" />
                    Knowledge Base
                </h2>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg font-medium"
                >
                    <Plus className="w-4 h-4" /> Add Context
                </button>
            </div>

            <p className="mb-6 text-gray-600 dark:text-gray-400 max-w-3xl">
                Upload policy documents, error code sheets, or past resolution notes here.
                LiveSOP Response Engine will automatically reference these documents (RAG) to improve decision accuracy.
            </p>

            {isAdding && (
                <div className="mb-8 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 animate-slide-in-down">
                    <h3 className="font-semibold mb-4 text-gray-700 dark:text-gray-200">Add Knowledge Context</h3>
                    <textarea
                        className="w-full p-4 border border-gray-200 dark:border-gray-700 rounded-lg mb-4 bg-gray-50 dark:bg-gray-900 dark:text-white h-32 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="Paste policy text, error codes, or SOP details here..."
                        value={newText}
                        onChange={e => setNewText(e.target.value)}
                    />
                    <div className="flex justify-end gap-3">
                        <button onClick={() => setIsAdding(false)} className="px-4 py-2 text-gray-500 hover:text-gray-700 font-medium">Cancel</button>
                        <button
                            onClick={handleAdd}
                            disabled={uploading || !newText.trim()}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50 font-medium"
                        >
                            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                            {uploading ? "Ingesting..." : "Ingest & Embed"}
                        </button>
                    </div>
                </div>
            )}

            <div className="grid gap-4">
                {docs.map(doc => (
                    <div key={doc.id} className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex justify-between items-start hover:shadow-md transition-all duration-200">
                        <div className="flex gap-4 w-full">
                            <div className="p-3 h-fit bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 shrink-0">
                                <FileText className="w-6 h-6" />
                            </div>
                            <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <h4 className="font-bold text-gray-900 dark:text-white truncate">
                                        {doc.metadata?.filename || "Manual Entry"}
                                    </h4>
                                    <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-500 px-2 py-0.5 rounded">
                                        {new Date(doc.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 leading-relaxed">
                                    {doc.content}
                                </p>
                            </div>
                        </div>
                        <button onClick={() => handleDelete(doc.id)} className="p-2 ml-4 hover:bg-red-50 text-gray-300 hover:text-red-500 rounded-lg transition-colors shrink-0">
                            <Trash2 className="w-5 h-5" />
                        </button>
                    </div>
                ))}

                {!loading && docs.length === 0 && (
                    <div className="text-center py-16 text-gray-400 bg-gray-50/50 dark:bg-gray-900/50 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700">
                        <Book className="w-12 h-12 mx-auto mb-4 opacity-10" />
                        <h3 className="text-lg font-medium text-gray-500">Knowledge Base is Empty</h3>
                        <p className="text-sm opacity-70 mt-1">Add context to help the AI understand your specific rules.</p>
                    </div>
                )}

                {loading && (
                    <div className="flex justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    </div>
                )}
            </div>
        </div>
    );
}
