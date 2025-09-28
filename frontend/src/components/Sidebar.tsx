import React from 'react';
import { PushHistory } from '../types/shared';

interface SidebarProps {
    postHistory: PushHistory[];
    currentPushId: string | null;
    onLoadPush: (pushId: string) => void;
    className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({
    postHistory,
    currentPushId,
    onLoadPush,
    className,
}) => {
    const containerClasses = ['flex h-full flex-col gap-4'];
    if (className) {
        containerClasses.push(className);
    }

    return (
        <nav className={containerClasses.join(' ')}>
            <div className="flex flex-col gap-1">
                <h2 className="text-base font-semibold text-slate-100">Content History</h2>
                <p className="text-sm text-slate-400">
                    Choose a recent push to review generated drafts.
                </p>
            </div>

            {postHistory.length === 0 ? (
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                    No history available yet.
                </div>
            ) : (
                <ul className="space-y-2 overflow-y-auto pr-1">
                    {postHistory.map(push => (
                        <li key={push.id}>
                            <button
                                type="button"
                                onClick={() => onLoadPush(push.id)}
                                className={`flex w-full flex-col items-start gap-1 rounded-lg border px-3 py-2 text-left transition-colors ${
                                    push.id === currentPushId
                                        ? 'border-indigo-400 bg-indigo-500/10 text-slate-100'
                                        : 'border-slate-800 bg-slate-900 text-slate-200 hover:border-slate-700 hover:bg-slate-800'
                                }`}
                            >
                                <span className="text-sm font-medium">
                                    {push.id.split('-')[0]}
                                </span>
                                <span className="text-xs text-slate-400">
                                    {push.posts.length} posts • {push.id.split('-')[1] || 'main'}
                                </span>
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </nav>
    );
};

export default Sidebar;
