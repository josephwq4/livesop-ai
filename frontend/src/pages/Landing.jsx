import { Link } from 'react-router-dom';
import { Bot, ArrowRight, Zap, Shield, GitGraph } from 'lucide-react';

export default function Landing() {
    return (
        <div className="min-h-screen bg-white dark:bg-gray-900">
            {/* Nav */}
            <nav className="border-b border-gray-100 dark:border-gray-800">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-blue-600 rounded-lg">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                            LiveSOP AI
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link to="/login" className="text-gray-600 dark:text-gray-300 font-medium hover:text-blue-600 transition-colors">
                            Login
                        </Link>
                        <Link to="/signup" className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-semibold transition-all">
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <div className="max-w-7xl mx-auto px-6 py-24 text-center">
                <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-8 tracking-tight">
                    Turn Chaos into <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
                        Intelligent Workflows
                    </span>
                </h1>
                <p className="text-xl text-gray-500 dark:text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed">
                    LiveSOP observes your team's Slack, Jira, and Email activity to automatically generate living Standard Operating Procedures.
                    No manual documentation required.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
                    <Link to="/signup" className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center gap-2">
                        Start Automating <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link to="/login" className="w-full sm:w-auto px-8 py-4 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-xl font-bold text-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all">
                        Live Demo
                    </Link>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8 text-left">
                    <Feature
                        icon={<GitGraph className="w-6 h-6 text-blue-500" />}
                        title="Auto-Inference"
                        desc="GPT-4 analyzes unstructured chat logs to build structured workflow graphs instantly."
                    />
                    <Feature
                        icon={<Zap className="w-6 h-6 text-amber-500" />}
                        title="Agentic Automation"
                        desc="Click 'Run' on any step to execute real actions in Jira, Slack, or Gmail."
                    />
                    <Feature
                        icon={<Shield className="w-6 h-6 text-emerald-500" />}
                        title="Enterprise Secure"
                        desc="Team isolation, encrypted storage, and role-based access control built-in."
                    />
                </div>
            </div>

            <footer className="border-t border-gray-100 dark:border-gray-800 py-12 text-center text-gray-500">
                &copy; {new Date().getFullYear()} LiveSOP AI. All rights reserved.
            </footer>
        </div>
    );
}

function Feature({ icon, title, desc }) {
    return (
        <div className="p-8 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:border-blue-200 dark:hover:border-blue-800 transition-colors">
            <div className="w-12 h-12 bg-white dark:bg-gray-900 rounded-xl flex items-center justify-center mb-6 shadow-sm">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{title}</h3>
            <p className="text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
        </div>
    );
}
