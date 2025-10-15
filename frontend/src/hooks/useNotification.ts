import { useState, useRef } from 'react';

export const useNotification = () => {
    const [message, setMessage] = useState<string>('');
    const [showMessage, setShowMessage] = useState<boolean>(false);
    const messageTimeoutRef = useRef<number | null>(null);

    const showNotification = (msg: string) => {
        if (messageTimeoutRef.current) {
            clearTimeout(messageTimeoutRef.current);
        }
        setMessage(msg);
        setShowMessage(true);
        messageTimeoutRef.current = setTimeout(() => {
            setShowMessage(false);
        }, 8002);
    };

    return {
        message,
        showMessage,
        showNotification
    };
};
