import React from 'react';
import { Post } from '../types/shared';

interface PostCardProps {
    post: Post;
    isLoading: boolean;
    onApprove: (id: string) => void;
    onDisapprove: (id: string) => void;
    onRephrase: (id: string) => void;
    onReadAloud: (id: string) => void;
    onContentChange: (event: React.ChangeEvent<HTMLTextAreaElement>, id: string) => void;
}

const PostCard: React.FC<PostCardProps> = ({
    post,
    isLoading,
    onApprove,
    onDisapprove,
    onRephrase,
    onReadAloud,
    onContentChange
}) => {
    const getPlatformAccent = (platform: string) => {
        switch (platform) {
            case 'LinkedIn':
                return { border: 'border-sky-500/40', text: 'text-sky-200' };
            case 'X':
                return { border: 'border-slate-500/40', text: 'text-slate-200' };
            case 'Email':
                return { border: 'border-emerald-500/40', text: 'text-emerald-200' };
            case 'TikTok':
                return { border: 'border-pink-500/40', text: 'text-pink-200' };
            default:
                return { border: 'border-indigo-500/40', text: 'text-indigo-200' };
        }
    };

    const statusTone = () => {
        switch (post.status) {
            case 'approved':
                return 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/30';
            case 'disapproved':
                return 'bg-rose-500/20 text-rose-200 border border-rose-500/30';
            case 'posted':
                return 'bg-blue-500/20 text-blue-200 border border-blue-500/30';
            default:
                return 'bg-slate-700/30 text-slate-200 border border-slate-600/40';
        }
    };

    const platformAccent = getPlatformAccent(post.platform);

    const renderMedia = (post: Post) => {
        if (post.media.length === 0) {
            return (
                <div className="flex h-48 w-full items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/70">
                    <div className="text-center text-slate-500">
                        <div className="mb-2 text-3xl">📄</div>
                        <div className="text-sm font-medium">No media attached</div>
                    </div>
                </div>
            );
        }

        if (post.media.length === 1) {
            const media = post.media[0];
            return (
                <div className="relative">
                    {media.type === 'image' ? (
                        <img src={media.url} alt={media.caption || "Post Media"} className="w-full h-48 object-cover rounded-2xl" />
                    ) : (
                        <video src={media.url} className="w-full h-48 object-cover rounded-2xl" controls muted loop></video>
                    )}
                    {media.caption && (
                        <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded-lg">
                            {media.caption}
                        </div>
                    )}
                </div>
            );
        }

        // Multiple media items - show as carousel/grid
        return (
            <div className="space-y-2">
                <div className="grid grid-cols-2 gap-2">
                    {post.media.slice(0, 4).map((media, index) => (
                        <div key={index} className="relative">
                            {media.type === 'image' ? (
                                <img src={media.url} alt={media.caption || `Media ${index + 1}`} className="w-full h-24 object-cover rounded-xl" />
                            ) : (
                                <video src={media.url} className="w-full h-24 object-cover rounded-xl" muted></video>
                            )}
                            {media.caption && (
                                <div className="absolute bottom-1 left-1 bg-black/70 text-white text-xs px-1 py-0.5 rounded">
                                    {media.caption}
                                </div>
                            )}
                            {index === 3 && post.media.length > 4 && (
                                <div className="absolute inset-0 bg-black/50 rounded-xl flex items-center justify-center text-white font-bold">
                                    +{post.media.length - 4}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                <div className="text-xs text-white/70 text-center">
                    {post.media.length} media items from database
                </div>
            </div>
        );
    };

    return (
        <div className="post-card-container rounded-3xl p-8">
            {/* Platform Header */}
            <div
                className={`mb-6 rounded-2xl border ${platformAccent.border} bg-slate-900/70 p-4 text-slate-100`}
            >
                <div className="flex items-center justify-between">
                    <h3 className={`text-sm font-semibold uppercase tracking-wide ${platformAccent.text}`}>
                        {post.platform}
                    </h3>
                    <div className={`rounded-full px-3 py-1 text-xs font-semibold ${statusTone()}`}>
                        {post.status.toUpperCase()}
                    </div>
                </div>
                <div className="flex items-center mt-2">
                    <img src={post.author.avatar} alt={post.author.name} className="h-8 w-8 rounded-full mr-3" />
                    <div>
                        <div className="font-semibold text-sm">{post.author.name}</div>
                        {post.author.title && <div className="text-xs opacity-75">{post.author.title}</div>}
                    </div>
                </div>
                {/* Repository Info */}
                {post.repository && (
                    <div className="mt-2 text-xs opacity-75">
                        📦 {post.repository} • {post.branch} • {post.commit_sha?.slice(0, 7)}
                    </div>
                )}
            </div>

            {/* Media from Database */}
            <div className="mb-6">
                {renderMedia(post)}
            </div>

            {/* Content */}
            <textarea
                value={post.content}
                onChange={(e) => onContentChange(e, post.id)}
                disabled={post.status !== 'pending'}
                className="h-32 w-full resize-none rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-slate-100 placeholder-slate-500 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-300/40"
                placeholder="AI-generated content..."
            />

            {/* AI Actions */}
            <div className="mt-6 flex gap-3">
                <button
                    onClick={() => onRephrase(post.id)}
                    disabled={post.status !== 'pending' || isLoading}
                    className="modern-button flex-1 rounded-2xl bg-indigo-600 py-3 px-4 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {isLoading ? (
                        <div className="loading-spinner mx-auto"></div>
                    ) : (
                        <>✨ Rephrase</>
                    )}
                </button>
                <button
                    onClick={() => onReadAloud(post.id)}
                    disabled={post.status !== 'pending'}
                    className="modern-button rounded-2xl bg-slate-800 py-3 px-6 text-sm font-semibold text-slate-100 transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    🎧
                </button>
            </div>

            {/* Approval Actions */}
            <div className="mt-4 flex gap-3">
                <button
                    onClick={() => onApprove(post.id)}
                    disabled={post.status !== 'pending'}
                    className="modern-button flex-1 rounded-2xl bg-emerald-600 py-3 px-4 text-sm font-semibold text-white transition-colors hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    ✅ Approve
                </button>
                <button
                    onClick={() => onDisapprove(post.id)}
                    disabled={post.status !== 'pending'}
                    className="modern-button flex-1 rounded-2xl bg-rose-600 py-3 px-4 text-sm font-semibold text-white transition-colors hover:bg-rose-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    ❌ Reject
                </button>
            </div>
        </div>
    );
};

export default PostCard;
