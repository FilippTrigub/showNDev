import { useCallback, useEffect, useState } from 'react';
import {
    SocialEnvValues,
    SocialEnvStatusMap,
    defaultSocialEnvValues,
} from '../types/social';
import {
    clearSocialEnvSecrets,
    fetchSocialEnvStatus,
    saveSocialEnvSecrets,
} from '../utils/backendApi';

const STORAGE_KEY = 'showndev-social-env';

const readFromStorage = (): SocialEnvValues => {
    if (typeof window === 'undefined') {
        return defaultSocialEnvValues;
    }

    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
        return defaultSocialEnvValues;
    }

    try {
        const parsed = JSON.parse(raw) as Partial<SocialEnvValues>;
        return { ...defaultSocialEnvValues, ...parsed };
    } catch (error) {
        console.warn('Failed to parse stored social env values:', error);
        return defaultSocialEnvValues;
    }
};

const persistToStorage = (values: SocialEnvValues) => {
    if (typeof window === 'undefined') {
        return;
    }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(values));
};

const removeFromStorage = () => {
    if (typeof window === 'undefined') {
        return;
    }
    window.localStorage.removeItem(STORAGE_KEY);
};

export const useSocialEnv = () => {
    const [values, setValues] = useState<SocialEnvValues>(defaultSocialEnvValues);
    const [status, setStatus] = useState<SocialEnvStatusMap>({});
    const [isSyncing, setIsSyncing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setValues(readFromStorage());
    }, []);

    const refreshStatus = useCallback(async () => {
        try {
            const response = await fetchSocialEnvStatus();
            setStatus(response.status || {});
            setError(null);
        } catch (err) {
            console.error('Failed to fetch social env status:', err);
            setError('Unable to load social credential status from backend.');
        }
    }, []);

    useEffect(() => {
        refreshStatus();
    }, [refreshStatus]);

    const saveValues = useCallback(async (nextValues: SocialEnvValues) => {
        setIsSyncing(true);
        try {
            const response = await saveSocialEnvSecrets(nextValues);
            setValues(nextValues);
            persistToStorage(nextValues);
            setStatus(response.status || {});
            setError(null);
        } catch (err) {
            console.error('Failed to persist social env secrets:', err);
            setError('Failed to persist social credentials to backend.');
            throw err;
        } finally {
            setIsSyncing(false);
        }
    }, []);

    const clearValues = useCallback(async () => {
        setIsSyncing(true);
        try {
            const response = await clearSocialEnvSecrets();
            setValues(defaultSocialEnvValues);
            removeFromStorage();
            setStatus(response.status || {});
            setError(null);
        } catch (err) {
            console.error('Failed to clear social env secrets:', err);
            setError('Unable to clear social credentials on backend.');
            throw err;
        } finally {
            setIsSyncing(false);
        }
    }, []);

    return {
        values,
        saveValues,
        clearValues,
        status,
        refreshStatus,
        isSyncing,
        error,
    };
};
