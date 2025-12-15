import { Link } from 'react-router-dom';
import { Bot, ArrowRight, Zap, Shield, GitGraph, Play } from 'lucide-react';

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
                    Turn Support Chaos into <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
                        Reliable Operations
                    </span>
                </h1>
                <p className="text-xl text-gray-500 dark:text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed">
                    LiveSOP observes your support channels to document processes automatically.
                    Turn tribal knowledge into executable Standard Operating Procedures.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
                    <Link to="/signup" className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center gap-2">
                        Start Free Trial <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link to="/login" className="w-full sm:w-auto px-8 py-4 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-xl font-bold text-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all">
                        View Demo
                    </Link>
                </div>

                {/* Demo Video Placeholder */}
                <div className="relative max-w-5xl mx-auto mb-32 rounded-2xl overflow-hidden shadow-2xl border border-gray-200 dark:border-gray-800 bg-gray-900 aspect-video flex items-center justify-center group cursor-pointer">
                    {/* In a real app, this would be an iframe or video tag */}
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900 to-transparent opacity-60"></div>
                    <div className="relative z-10 text-center">
                        <div className="w-20 h-20 bg-white/10 backdrop-blur-md rounded-full flex items-center justify-center mx-auto mb-4 border border-white/20 group-hover:scale-110 transition-transform">
                            <Play className="w-8 h-8 text-white ml-1" />
                        </div>
                        <p className="text-gray-300 font-medium">Watch the 2-minute Product Tour</p>
                    </div>
                </div>

                {/* How It Works */}
                <div className="mb-24">
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-16">How It Works</h2>
                    <div className="grid md:grid-cols-3 gap-12 text-left relative">
                        {/* Connecting Line (Desktop) */}
                        <div className="hidden md:block absolute top-8 left-0 w-full h-0.5 bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 dark:from-blue-900 dark:to-pink-900 z-0"></div>

                        <Step
                            num="01"
                            title="Detect"
                            desc="We connect to Slack and Jira to identify recurring support patterns."
                        />
                        <Step
                            num="02"
                            title="Document"
                            desc="The system generates a 'Living SOP' flow that documents the resolution path."
                        />
                        <Step
                            num="03"
                            title="Execute"
                            desc="Run the approved SOP manually or set it to Auto-Pilot for instant resolution."
                        />
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8 text-left">
                    <Feature
                        icon={<GitGraph className="w-6 h-6 text-blue-500" />}
                        title="Living SOPs"
                        desc="Documentation that updates itself as your team works."
                    />
                    <Feature
                        icon={<Zap className="w-6 h-6 text-amber-500" />}
                        title="Safe Automation"
                        desc="You control exactly which steps run automatically."
                    />
                    <Feature
                        icon={<Shield className="w-6 h-6 text-emerald-500" />}
                        title="Enterprise Grade"
                        desc="SOC2-ready architecture with team isolation."
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

function Step({ num, title, desc }) {
    return (
        <div className="relative z-10">
            <div className="w-16 h-16 bg-white dark:bg-gray-900 border-4 border-blue-50 dark:border-gray-800 rounded-2xl flex items-center justify-center text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 shadow-xl mb-6">
                {num}
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{title}</h3>
            <p className="text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
        </div>
    );
}
