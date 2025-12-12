import { useState } from 'react';
import { Upload, Slack, FileText, Mail, Database, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { uploadCSV, fetchSlackEvents, fetchJiraIssues, fetchGmailThreads } from '../services/api';

import Navbar from '../components/Navbar';

export default function Integrations() {
    const [loading, setLoading] = useState({});
    const [results, setResults] = useState({});
    const [csvFile, setCsvFile] = useState(null);
    const teamId = 'team123';

    // ... (logic functions unchanged) ...

    const handleSlackConnect = async () => {
        setLoading({ ...loading, slack: true });
        try {
            const token = prompt('Enter your Slack Bot Token:');
            if (!token) return;

            const channels = prompt('Enter channel names (comma-separated):', 'general');
            const result = await fetchSlackEvents(token, channels);

            setResults({ ...results, slack: result });
            alert(`✅ Connected! Found ${result.count} events`);
        } catch (error) {
            alert('❌ Error connecting to Slack');
            console.error(error);
        } finally {
            setLoading({ ...loading, slack: false });
        }
    };

    const handleJiraConnect = async () => {
        setLoading({ ...loading, jira: true });
        try {
            const apiKey = prompt('Enter your Jira API Key:');
            if (!apiKey) return;

            const project = prompt('Enter Jira Project Key:', 'PROJ');
            const result = await fetchJiraIssues(apiKey, project);

            setResults({ ...results, jira: result });
            alert(`✅ Connected! Found ${result.count} issues`);
        } catch (error) {
            alert('❌ Error connecting to Jira');
            console.error(error);
        } finally {
            setLoading({ ...loading, jira: false });
        }
    };

    const handleGmailConnect = async () => {
        setLoading({ ...loading, gmail: true });
        try {
            const credentials = prompt('Enter your Gmail OAuth credentials (JSON):');
            if (!credentials) return;

            const label = prompt('Enter Gmail label:', 'INBOX');
            const result = await fetchGmailThreads(credentials, label);

            setResults({ ...results, gmail: result });
            alert(`✅ Connected! Found ${result.count} threads`);
        } catch (error) {
            alert('❌ Error connecting to Gmail');
            console.error(error);
        } finally {
            setLoading({ ...loading, gmail: false });
        }
    };

    const handleCSVUpload = async () => {
        if (!csvFile) {
            alert('Please select a CSV file first');
            return;
        }

        setLoading({ ...loading, csv: true });
        try {
            const result = await uploadCSV(teamId, csvFile);
            setResults({ ...results, csv: result });
            alert(`✅ Uploaded! Imported ${result.count} events`);
            setCsvFile(null);
        } catch (error) {
            alert('❌ Error uploading CSV');
            console.error(error);
        } finally {
            setLoading({ ...loading, csv: false });
        }
    };

    const integrations = [
        {
            id: 'slack',
            name: 'Slack',
            icon: Slack,
            color: 'from-purple-500 to-pink-500',
            description: 'Import messages and conversations from Slack channels',
            action: handleSlackConnect,
        },
        {
            id: 'jira',
            name: 'Jira',
            icon: Database,
            color: 'from-blue-500 to-cyan-500',
            description: 'Sync issues, tickets, and project data from Jira',
            action: handleJiraConnect,
        },
        {
            id: 'gmail',
            name: 'Gmail',
            icon: Mail,
            color: 'from-red-500 to-orange-500',
            description: 'Import email threads and communications',
            action: handleGmailConnect,
        },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
            {/* Navigation Bar */}
            <Navbar />

            {/* Header */}
            <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Integrations
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Connect your tools to start inferring workflows
                    </p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Integration Cards */}
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    {integrations.map((integration) => {
                        const Icon = integration.icon;
                        const isConnected = results[integration.id];
                        const isLoading = loading[integration.id];

                        return (
                            <div
                                key={integration.id}
                                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                            >
                                <div className={`bg-gradient-to-br ${integration.color} w-16 h-16 rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                                    <Icon className="w-8 h-8 text-white" />
                                </div>

                                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                                    {integration.name}
                                </h3>

                                <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
                                    {integration.description}
                                </p>

                                {isConnected && (
                                    <div className="mb-4 flex items-center gap-2 text-green-600 dark:text-green-400 text-sm font-semibold">
                                        <CheckCircle className="w-4 h-4" />
                                        Connected - {isConnected.count} items
                                    </div>
                                )}

                                <button
                                    onClick={integration.action}
                                    disabled={isLoading}
                                    className={`w-full flex items-center justify-center gap-2 bg-gradient-to-r ${integration.color} hover:opacity-90 text-white px-4 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 transform hover:scale-105`}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Connecting...
                                        </>
                                    ) : (
                                        <>
                                            <Icon className="w-5 h-5" />
                                            {isConnected ? 'Reconnect' : 'Connect'}
                                        </>
                                    )}
                                </button>
                            </div>
                        );
                    })}
                </div>

                {/* CSV Upload Section */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-gradient-to-br from-green-500 to-emerald-500 w-12 h-12 rounded-xl flex items-center justify-center shadow-lg">
                            <Upload className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                                CSV Import
                            </h3>
                            <p className="text-gray-600 dark:text-gray-400 text-sm">
                                Upload a CSV file with your team activity data
                            </p>
                        </div>
                    </div>

                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors duration-200">
                        <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />

                        <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => setCsvFile(e.target.files[0])}
                            className="hidden"
                            id="csv-upload"
                        />

                        <label
                            htmlFor="csv-upload"
                            className="inline-block bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 px-6 py-3 rounded-lg font-semibold cursor-pointer transition-all duration-200 transform hover:scale-105"
                        >
                            Choose CSV File
                        </label>

                        {csvFile && (
                            <div className="mt-4">
                                <p className="text-gray-700 dark:text-gray-300 font-semibold mb-3">
                                    Selected: {csvFile.name}
                                </p>
                                <button
                                    onClick={handleCSVUpload}
                                    disabled={loading.csv}
                                    className="inline-flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 transform hover:scale-105"
                                >
                                    {loading.csv ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Uploading...
                                        </>
                                    ) : (
                                        <>
                                            <Upload className="w-5 h-5" />
                                            Upload CSV
                                        </>
                                    )}
                                </button>
                            </div>
                        )}

                        {results.csv && (
                            <div className="mt-4 flex items-center justify-center gap-2 text-green-600 dark:text-green-400 font-semibold">
                                <CheckCircle className="w-5 h-5" />
                                Imported {results.csv.count} events successfully!
                            </div>
                        )}
                    </div>

                    <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                            CSV Format Requirements:
                        </h4>
                        <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                            <li>• Required columns: <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">text</code>, <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">actor</code></li>
                            <li>• Optional columns: <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">timestamp</code>, <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">description</code></li>
                            <li>• Example: text,actor,timestamp</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
