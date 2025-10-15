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
            className={`fixed inset-0 z-50 flex items-center justify-center p-4 transition-opacity ${isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'}`}
            aria-hidden={!isOpen}
        >
            <div
                className="absolute inset-0 bg-black/40"
                onClick={onClose}
                role="presentation"
            />
            <div className="relative w-full max-w-3xl max-h-[90vh] overflow-hidden rounded-lg bg-white shadow-xl">
                {/* Header */}
                <div className="border-b border-gray-200 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold text-gray-900">Social Media Credentials</h2>
                        <button
                            type="button"
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                            onClick={onClose}
                            aria-label="Close"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">
                        Configure API credentials for social media platforms. Changes sync with backend.
                    </p>
                </div>

                {/* Scrollable Content */}
                <div className="overflow-y-auto max-h-[calc(90vh-180px)] px-6 py-4">
                    <div className="space-y-6">
                        {SOCIAL_ENV_SECTIONS.map(section => (
                            <section key={section.title} className="border-b border-gray-100 pb-6 last:border-0">
                                <div className="mb-4">
                                    <h3 className="text-base font-medium text-gray-900">{section.title}</h3>
                                    <p className="mt-1 text-sm text-gray-500">{section.description}</p>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                    {section.fields.map(fieldKey => {
                                        const config = SOCIAL_ENV_FIELD_CONFIG[fieldKey];
                                        const backendStatusKey = SOCIAL_ENV_FIELD_API_KEYS[fieldKey];
                                        const isConfigured = status[backendStatusKey];
                                        return (
                                            <label key={fieldKey} className="flex flex-col gap-2">
                                                <span className="flex items-center gap-2 text-sm font-medium text-gray-700">
                                                    {config.label}
                                                    <span className="text-xs text-gray-400">{config.envVar}</span>
                                                    <span className={`ml-auto text-xs font-normal ${isConfigured ? 'text-green-600' : 'text-gray-400'}`}>
                                                        {isConfigured ? '✓' : '○'}
                                                    </span>
                                                </span>
                                                <input
                                                    type={config.type === 'password' ? 'password' : config.type === 'url' ? 'url' : 'text'}
                                                    value={formValues[fieldKey]}
                                                    onChange={handleInputChange(fieldKey)}
                                                    placeholder={config.placeholder}
                                                    className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                                                />
                                                {config.helperText && (
                                                    <span className="text-xs text-gray-400">{config.helperText}</span>
                                                )}
                                            </label>
                                        );
                                    })}
                                </div>
                            </section>
                        ))}

                        {/* Preview Section */}
                        <section className="pt-2">
                            <h3 className="text-base font-medium text-gray-900 mb-3">.env Preview</h3>
                            <div className="rounded border border-gray-200 bg-gray-50 p-3">
                                <pre className="overflow-x-auto text-xs text-gray-700 font-mono">{envSnippet}</pre>
                            </div>
                        </section>
                    </div>
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
                    <div className="flex items-center justify-between gap-3">
                        <button
                            type="button"
                            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                            onClick={handleClear}
                            disabled={isClearing || isSyncing}
                        >
                            {isClearing ? 'Clearing…' : 'Clear All'}
                        </button>
                        <div className="flex gap-3">
                            <button
                                type="button"
                                className="px-4 py-2 text-sm font-medium text-indigo-600 border border-indigo-600 rounded hover:bg-indigo-50 transition-colors"
                                onClick={handleCopy}
                            >
                                Copy .env
                            </button>
                            <button
                                type="button"
                                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                onClick={handleSave}
                                disabled={isSaving || isSyncing}
                            >
                                {isSaving ? 'Saving…' : 'Save'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SocialEnvModal;
