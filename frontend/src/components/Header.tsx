import React from 'react';

interface HeaderProps {
    tone: number;
    onToneChange: (tone: number) => void;
    onToggleHistory: () => void;
    onOpenSocialSettings: () => void;
    socialEnvConfigured: boolean;
    historyOpen: boolean;
}

const Header: React.FC<HeaderProps> = ({
    tone,
    onToneChange,
    onToggleHistory,
    onOpenSocialSettings,
    socialEnvConfigured,
    historyOpen,
}) => {
    return (
        <header className="border-b border-slate-800 bg-slate-950">
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            className="lg:hidden rounded-lg border border-slate-800 px-3 py-2 text-sm font-medium text-slate-200 hover:border-slate-700 hover:bg-slate-900"
                            onClick={onToggleHistory}
                        >
                            {historyOpen ? 'Hide History' : 'Show History'}
                        </button>
                        <div>
                            <h1 className="text-2xl font-semibold text-slate-100">AI Content Manager</h1>
                            <p className="text-sm text-slate-400">
                                Review and post AI-generated updates across social channels.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <div className="flex w-full flex-col">
                        <label className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            Content Tone
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={tone}
                            onChange={(event) => onToneChange(Number(event.target.value))}
                            className="mt-2 h-2 w-full rounded-full bg-slate-800 accent-indigo-400"
                        />
                        <div className="mt-1 flex justify-between text-xs text-slate-500">
                            <span>Formal</span>
                            <span>Casual</span>
                        </div>
                    </div>

                    <button
                        type="button"
                        className="flex items-center gap-2 rounded-lg border border-indigo-500/70 px-4 py-2 text-sm font-medium text-indigo-200 hover:bg-indigo-500/10"
                        onClick={onOpenSocialSettings}
                    >
                        <span role="img" aria-label="settings">🔐</span>
                        Social Credentials
                        <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                            socialEnvConfigured ? 'bg-emerald-500/20 text-emerald-200' : 'bg-amber-500/20 text-amber-200'
                        }`}>
                            {socialEnvConfigured ? 'Ready' : 'Set up'}
                        </span>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
