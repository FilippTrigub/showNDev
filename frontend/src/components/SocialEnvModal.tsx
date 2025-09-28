import React, { useEffect, useMemo, useState } from 'react';
import {
    SocialEnvValues,
    SOCIAL_ENV_SECTIONS,
    SOCIAL_ENV_FIELD_CONFIG,
    defaultSocialEnvValues,
    buildSocialEnvSnippet,
    SOCIAL_ENV_FIELD_API_KEYS,
} from '../types/social';

interface SocialEnvModalProps {
    isOpen: boolean;
    values: SocialEnvValues;
    onClose: () => void;
    onSave: (values: SocialEnvValues) => void | Promise<void>;
    onClear: () => void | Promise<void>;
    onNotify: (message: string) => void;
    status: Record<string, boolean>;
    isSyncing: boolean;
}

const SocialEnvModal: React.FC<SocialEnvModalProps> = ({
    isOpen,
    values,
    onClose,
    onSave,
    onClear,
    onNotify,
    status,
    isSyncing,
}) => {
    const [formValues, setFormValues] = useState<SocialEnvValues>(values);
    const [isSaving, setIsSaving] = useState(false);
    const [isClearing, setIsClearing] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setFormValues(values);
        }
    }, [isOpen, values]);

    const envSnippet = useMemo(() => buildSocialEnvSnippet(formValues), [formValues]);

    const handleInputChange = (key: keyof SocialEnvValues) => (event: React.ChangeEvent<HTMLInputElement>) => {
        const { value } = event.target;
        setFormValues(prev => ({ ...prev, [key]: value }));
    };

    const handleCopy = async () => {
        try {
            if (navigator?.clipboard?.writeText) {
                await navigator.clipboard.writeText(envSnippet);
                onNotify('.env snippet copied to clipboard.');
            } else {
                onNotify('Clipboard unavailable. Copy the snippet manually.');
            }
        } catch (error) {
            console.error('Failed to copy env snippet:', error);
            onNotify('Unable to copy automatically. Copy the snippet manually.');
        }
    };

    const handleSave = async () => {
        try {
            setIsSaving(true);
            await onSave(formValues);
            onNotify('Social credentials synced with backend.');
        } catch (error) {
            console.error('Failed to save social env values:', error);
            onNotify('Could not save credentials. Try again.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleClear = async () => {
        try {
            setIsClearing(true);
            await onClear();
            setFormValues(defaultSocialEnvValues);
            onNotify('Cleared social credentials from backend.');
        } catch (error) {
            console.error('Failed to clear social env values:', error);
            onNotify('Could not clear credentials. Try again.');
        } finally {
            setIsClearing(false);
        }
    };

    return (
        <div
            className={`fixed inset-0 z-50 transition-opacity ${isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'}`}
            aria-hidden={!isOpen}
        >
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
                role="presentation"
            />
            <div className="relative flex min-h-full items-center justify-center p-4">
                <div className="w-full max-w-3xl rounded-3xl bg-white/95 p-8 shadow-2xl">
                    <div className="flex items-start justify-between gap-4">
                        <div>
                            <h2 className="text-2xl font-semibold text-gray-900">Configure Social Media Credentials</h2>
                            <p className="mt-2 text-sm text-gray-600">
                                These values map directly to the backend environment variables and are cached locally for quick edits.
                                Use “Copy .env snippet” to update <code>.env</code> for the FastAPI backend when you want them persisted outside this session.
                            </p>
                        </div>
                        <button
                            type="button"
                            className="rounded-full bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300"
                            onClick={onClose}
                        >
                            Close
                        </button>
                    </div>

                    <div className="mt-6 space-y-6">
                        {SOCIAL_ENV_SECTIONS.map(section => (
                            <section key={section.title} className="rounded-2xl bg-white/70 p-5 shadow-sm">
                                <div className="mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                                    <p className="text-sm text-gray-600">{section.description}</p>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                    {section.fields.map(fieldKey => {
                                        const config = SOCIAL_ENV_FIELD_CONFIG[fieldKey];
                                        const backendStatusKey = SOCIAL_ENV_FIELD_API_KEYS[fieldKey];
                                        const isConfigured = status[backendStatusKey];
                                        return (
                                            <label key={fieldKey} className="flex flex-col gap-2">
                                                <span className="text-sm font-medium text-gray-700">
                                                    {config.label}
                                                    <span className="ml-2 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">
                                                        {config.envVar}
                                                    </span>
                                                    <span className={`ml-2 text-xs ${isConfigured ? 'text-emerald-500' : 'text-slate-400'}`}>
                                                        {isConfigured ? 'Configured' : 'Not set'}
                                                    </span>
                                                </span>
                                                <input
                                                    type={config.type === 'password' ? 'password' : config.type === 'url' ? 'url' : 'text'}
                                                    value={formValues[fieldKey]}
                                                    onChange={handleInputChange(fieldKey)}
                                                    placeholder={config.placeholder}
                                                    className="w-full rounded-xl border border-gray-200 bg-white/80 px-4 py-2 text-sm shadow-inner focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                                                />
                                                {config.helperText && (
                                                    <span className="text-xs text-gray-500">{config.helperText}</span>
                                                )}
                                            </label>
                                        );
                                    })}
                                </div>
                            </section>
                        ))}
                    </div>

                    <div className="mt-8 flex flex-wrap gap-3">
                        <button
                            type="button"
                            className="modern-button rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 px-5 py-3 text-sm font-semibold text-white shadow-md hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
                            onClick={handleSave}
                            disabled={isSaving || isSyncing}
                        >
                            {isSaving ? 'Saving…' : 'Save Credentials'}
                        </button>
                        <button
                            type="button"
                            className="rounded-xl border border-indigo-200 px-5 py-3 text-sm font-semibold text-indigo-600 hover:bg-indigo-50"
                            onClick={handleCopy}
                            >
                            Copy .env snippet
                        </button>
                        <button
                            type="button"
                            className="rounded-xl border border-gray-200 px-5 py-3 text-sm font-semibold text-gray-600 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
                            onClick={handleClear}
                            disabled={isClearing || isSyncing}
                        >
                            {isClearing ? 'Clearing…' : 'Clear stored values'}
                        </button>
                    </div>

                    <div className="mt-6 rounded-2xl bg-gray-900/90 p-4 text-sm text-gray-100">
                        <p className="font-semibold text-indigo-300">Preview</p>
                        <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs">{envSnippet}</pre>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SocialEnvModal;
