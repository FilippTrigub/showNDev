import React, { useEffect } from 'react';

interface ImageModalProps {
    imageUrl: string | null;
    caption?: string;
    onClose: () => void;
}

const ImageModal: React.FC<ImageModalProps> = ({ imageUrl, caption, onClose }) => {
    // Handle ESC key to close modal
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        if (imageUrl) {
            document.addEventListener('keydown', handleEsc);
            // Prevent background scrolling when modal is open
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEsc);
            document.body.style.overflow = 'unset';
        };
    }, [imageUrl, onClose]);

    if (!imageUrl) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="relative max-h-[90vh] max-w-[90vw] rounded-2xl bg-slate-900 p-4 shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Close button */}
                <button
                    onClick={onClose}
                    className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-slate-800/80 text-white transition-colors hover:bg-slate-700"
                    aria-label="Close modal"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-6 w-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                        />
                    </svg>
                </button>

                {/* Image */}
                <img
                    src={imageUrl}
                    alt={caption || "Full size image"}
                    className="max-h-[80vh] max-w-full rounded-xl object-contain"
                />

                {/* Caption */}
                {caption && (
                    <div className="mt-4 text-center text-sm text-slate-300">
                        {caption}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ImageModal;
