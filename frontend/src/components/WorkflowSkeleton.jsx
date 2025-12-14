import React from 'react';

export default function WorkflowSkeleton() {
    return (
        <div className="space-y-4 animate-pulse">
            <h2 className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-6"></h2>
            {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
                    <div className="flex justify-between items-start mb-4">
                        <div className="w-full">
                            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-3"></div>
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                        </div>
                        <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                    </div>
                    <div className="flex gap-4 mt-2">
                        <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                </div>
            ))}
        </div>
    );
}
