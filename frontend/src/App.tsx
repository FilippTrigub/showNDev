import React, { useState, useEffect, useRef } from 'react';
import './styles/index.css';
import { getContentItems, updateContentStatus, updateContentText, testBackendConnection, rephraseContent, approveAndPost, ContentItem } from './utils/backendApi';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import PostCard from './components/PostCard';
import SocialEnvModal from './components/SocialEnvModal';
import { Post, PushHistory } from './types/shared';
import { useSocialEnv } from './hooks/useSocialEnv';

// Convert ContentItem to Post format for UI compatibility
const convertContentItemToPost = (item: ContentItem): Post => {
    // Build media array from separate image/video/audio arrays
    const media: Post['media'] = [];

    // Add images from image_content array
    if (item.image_content && Array.isArray(item.image_content)) {
        item.image_content.forEach((url: string) => {
            if (url) {
                media.push({ url, type: 'image' });
            }
        });
    }

    // Add videos from video_content array
    if (item.video_content && Array.isArray(item.video_content)) {
        item.video_content.forEach((url: string) => {
            if (url) {
                media.push({ url, type: 'video' });
            }
        });
    }

    // Add audio from audio_content array (base64 encoded)
    if (item.audio_content && Array.isArray(item.audio_content)) {
        item.audio_content.forEach((base64Audio: string, index: number) => {
            if (base64Audio) {
                // Create a data URL for the audio
                const audioDataUrl = `data:audio/mpeg;base64,${base64Audio}`;
                media.push({
                    url: audioDataUrl,
                    type: 'audio',
                    caption: `Audio ${index + 1}`
                });
            }
        });
    }

    // Fallback to legacy media field if present
    if ((!media || media.length === 0) && item.media && Array.isArray(item.media)) {
        media.push(...item.media);
    }

    return {
        id: item._id,
        platform: (item.platform as 'LinkedIn' | 'X' | 'Email' | 'TikTok') || 'LinkedIn',
        author: item.author || {
            name: 'System',
            avatar: 'https://placehold.co/100x100/667eea/ffffff?text=SYS'
        },
        content: item.content || '',
        status: item.status === 'pending' ? 'pending' :
               item.status === 'rephrased' ? 'pending' :
               item.status === 'rejected' ? 'disapproved' : 'posted',
        media,
        repository: item.repository,
        commit_sha: item.commit_sha,
        branch: item.branch
    };
};

const App: React.FC = () => {
    const [posts, setPosts] = useState<Post[]>([]);
    const [postHistory, setPostHistory] = useState<PushHistory[]>([]);
    const [currentPushId, setCurrentPushId] = useState<string | null>(null);
    const [tone, setTone] = useState<number>(50);
    const [notification, setNotification] = useState<string>('');
    const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<{ [key: string]: boolean }>({});
    const [backendConnected, setBackendConnected] = useState<boolean>(false);
    const [isSocialModalOpen, setIsSocialModalOpen] = useState<boolean>(false);

    const {
        values: socialEnvValues,
        saveValues: saveSocialEnvValues,
        clearValues: clearSocialEnvValues,
        status: socialEnvStatus,
        isSyncing: socialEnvSyncing,
        error: socialEnvError,
    } = useSocialEnv();

    const messageTimeoutRef = useRef<number | null>(null);

    // Initialize app - load content from backend
    useEffect(() => {
        const loadContentFromBackend = async () => {
            try {
                const isBackendAvailable = await testBackendConnection();
                setBackendConnected(isBackendAvailable);
                
                if (isBackendAvailable) {
                    const contentItems = await getContentItems();
                    
                    if (contentItems && contentItems.length > 0) {
                        // Convert backend content to posts
                        const backendPosts = contentItems.map(convertContentItemToPost);
                        
                        // Group posts by repository/branch for history
                        const groupedPosts = backendPosts.reduce((acc, post) => {
                            const key = `${post.repository || 'unknown'}-${post.branch || 'main'}`;
                            if (!acc[key]) {
                                acc[key] = [];
                            }
                            acc[key].push(post);
                            return acc;
                        }, {} as Record<string, Post[]>);

                        // Create push history from grouped posts
                        const newPushes: PushHistory[] = Object.entries(groupedPosts).map(([key, posts]) => ({
                            id: key,
                            posts
                        }));

                        setPostHistory(newPushes);
                        console.log('Successfully loaded content from backend:', contentItems.length, 'items');
                    } else {
                        console.log('No content available from backend');
                        setPostHistory([]);
                    }
                } else {
                    console.log('Backend not available, using mock data');
                    showNotification("Backend unavailable - using mock data");
                    // Could load mock data here if needed
                }
            } catch (error) {
                console.error('Error loading content from backend:', error);
                setBackendConnected(false);
                showNotification("Error connecting to backend - using mock data");
            }
        };

        loadContentFromBackend();
    }, []);

    // Load latest push
    useEffect(() => {
        if (postHistory.length > 0 && currentPushId === null) {
            const latestPush = postHistory[postHistory.length - 1];
            loadPush(latestPush.id);
        }
    }, [postHistory, currentPushId]);

    // Convert tone from 0-100 range to 0-1 range for backend
    const normalizedTone = tone / 100;

    // Helper function to refresh content from backend
    const refreshContentFromBackend = async () => {
        try {
            console.log('Refreshing content from backend...');
            const contentItems = await getContentItems();
            
            // Convert backend content to posts
            const backendPosts = contentItems.map(convertContentItemToPost);
            
            // Group posts by repository/branch for history
            const groupedPosts = backendPosts.reduce((acc, post) => {
                const key = `${post.repository || 'unknown'}-${post.branch || 'main'}`;
                if (!acc[key]) {
                    acc[key] = [];
                }
                acc[key].push(post);
                return acc;
            }, {} as Record<string, Post[]>);

            // Create push history from grouped posts
            const newPushes: PushHistory[] = Object.entries(groupedPosts).map(([key, posts]) => ({
                id: key,
                posts
            }));

            setPostHistory(newPushes);
            
            // Update current posts if we're viewing a specific push
            if (currentPushId) {
                const currentPush = newPushes.find(p => p.id === currentPushId);
                if (currentPush) {
                    setPosts(currentPush.posts);
                }
            }
            
            console.log('Content refreshed successfully');
        } catch (error) {
            console.error('Error refreshing content:', error);
        }
    };

    const showNotification = (msg: string) => {
        if (messageTimeoutRef.current) {
            clearTimeout(messageTimeoutRef.current);
        }
        setNotification(msg);
        messageTimeoutRef.current = window.setTimeout(() => {
            setNotification('');
        }, 8002);
    };

    const handleSaveSocialEnv = async (nextValues: typeof socialEnvValues) => {
        await saveSocialEnvValues(nextValues);
    };

    const handleClearSocialEnv = async () => {
        await clearSocialEnvValues();
    };

    const loadPush = (pushId: string) => {
        const push = postHistory.find(p => p.id === pushId);
        if (push) {
            setPosts(push.posts);
            setCurrentPushId(pushId);
        }
    };

    const updatePostStatus = async (postId: string, newStatus: Post['status']) => {
        try {
            // Update backend
            const backendStatus = newStatus === 'disapproved' ? 'rejected' : 
                                 newStatus === 'posted' ? 'published' : newStatus;
            await updateContentStatus(postId, backendStatus as any);
            
            // Update local state
            setPosts(prevPosts => 
                prevPosts.map(post => 
                    post.id === postId ? { ...post, status: newStatus } : post
                )
            );
            
            // Update post history
            setPostHistory(prevHistory => 
                prevHistory.map(pushHistory => ({
                    ...pushHistory,
                    posts: pushHistory.posts.map(post => 
                        post.id === postId ? { ...post, status: newStatus } : post
                    )
                }))
            );
            
            showNotification(`Post ${newStatus}`);
        } catch (error) {
            console.error('Error updating post status:', error);
            showNotification('Error updating post status');
        }
    };

    const rephrasePost = async (postId: string) => {
        setIsLoading(prev => ({ ...prev, [postId]: true }));
        try {
            if (backendConnected) {
                console.log('Rephrasing post with ID:', postId);
                
                // Use backend rephraseContent API
                const rephraseResult = await rephraseContent(postId, normalizedTone);
                console.log('Rephrase result:', rephraseResult);
                
                // Use our refresh helper to reload all content
                await refreshContentFromBackend();
                
                showNotification('Post rephrased successfully!');
            } else {
                // Fallback to direct MCP call if backend is unavailable
                const { rephraseWithMCP } = await import('./utils/mcpApi');
                const currentPost = posts.find(p => p.id === postId);
                if (currentPost) {
                    const newContent = await rephraseWithMCP(currentPost.content, normalizedTone);
                    
                    // Update local state
                    setPosts(prevPosts => 
                        prevPosts.map(post => 
                            post.id === postId ? { ...post, content: newContent } : post
                        )
                    );
                    
                    // Update post history
                    setPostHistory(prevHistory => 
                        prevHistory.map(pushHistory => ({
                            ...pushHistory,
                            posts: pushHistory.posts.map(post => 
                                post.id === postId ? { ...post, content: newContent } : post
                            )
                        }))
                    );
                    
                    showNotification('Post rephrased successfully (via MCP fallback)');
                }
            }
        } catch (error) {
            console.error('Error rephrasing post:', error);
            showNotification('Error rephrasing post');
        } finally {
            setIsLoading(prev => ({ ...prev, [postId]: false }));
        }
    };

    const handleApprove = async (postId: string) => {
        try {
            // Use approveAndPost API instead of just status update
            await approveAndPost(postId);

            // Update local state to "posted" status
            setPosts(prevPosts =>
                prevPosts.map(post =>
                    post.id === postId ? { ...post, status: 'posted' } : post
                )
            );

            // Update post history
            setPostHistory(prevHistory =>
                prevHistory.map(pushHistory => ({
                    ...pushHistory,
                    posts: pushHistory.posts.map(post =>
                        post.id === postId ? { ...post, status: 'posted' } : post
                    )
                }))
            );

            showNotification('Approved & Posted! ✅');
        } catch (error) {
            console.error('Error approving and posting:', error);
            showNotification('Error approving and posting');
        }
    };


    const getCurrentPush = () => {
        return postHistory.find(p => p.id === currentPushId);
    };

    const currentPosts = getCurrentPush()?.posts || posts;
    const socialEnvConfigured = Object.values(socialEnvStatus || {}).some(value => value);

    useEffect(() => {
        if (socialEnvError) {
            showNotification(socialEnvError);
        }
    }, [socialEnvError]);

    return (
        <div className="min-h-screen bg-slate-950">
            <Header
                tone={tone}
                onToneChange={setTone}
                onToggleHistory={() => setIsHistoryOpen(prev => !prev)}
                onOpenSocialSettings={() => setIsSocialModalOpen(true)}
                socialEnvConfigured={socialEnvConfigured}
                historyOpen={isHistoryOpen}
            />

            {notification && (
                <div className="fixed top-4 right-4 rounded-lg border border-emerald-400/40 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-200 shadow-lg">
                    {notification}
                </div>
            )}

            <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8 lg:flex-row">
                <main className="flex-1 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-slate-100">Drafts</h2>
                        <span className="text-xs uppercase tracking-wide text-slate-500">
                            Connected: {backendConnected ? 'Backend' : 'Mock'}
                        </span>
                    </div>

                    {currentPosts.length > 0 ? (
                        currentPosts.map((post) => (
                            <PostCard
                                key={post.id}
                                post={post}
                                isLoading={isLoading[post.id] || false}
                                onContentChange={async (event: React.ChangeEvent<HTMLTextAreaElement>, id: string) => {
                                    const newContent = event.target.value;
                                    try {
                                        await updateContentText(id, newContent);
                                        setPosts(prevPosts =>
                                            prevPosts.map(p =>
                                                p.id === id ? { ...p, content: newContent } : p
                                            )
                                        );
                                    } catch (error) {
                                        console.error('Error updating content:', error);
                                    }
                                }}
                                onRephrase={(id: string) => rephrasePost(id)}
                                onApprove={(id: string) => handleApprove(id)}
                                onDisapprove={(id: string) => updatePostStatus(id, 'disapproved')}
                                onReadAloud={() => {}} // Audio handled directly in PostCard
                            />
                        ))
                    ) : (
                        <div className="rounded-lg border border-slate-800 bg-slate-900 p-8 text-center text-slate-400">
                            No content available. Check your backend connection.
                        </div>
                    )}
                </main>

                <aside
                    className={`${isHistoryOpen ? 'flex' : 'hidden'} lg:flex lg:w-80`}
                >
                    <Sidebar
                        postHistory={postHistory}
                        currentPushId={currentPushId}
                        onLoadPush={(id) => {
                            loadPush(id);
                            if (typeof window !== 'undefined' && window.innerWidth < 1024) {
                                setIsHistoryOpen(false);
                            }
                        }}
                        className="w-full rounded-xl border border-slate-800 bg-slate-900/60 p-4"
                    />
                </aside>
            </div>

            <SocialEnvModal
                isOpen={isSocialModalOpen}
                values={socialEnvValues}
                onClose={() => setIsSocialModalOpen(false)}
                onSave={handleSaveSocialEnv}
                onClear={handleClearSocialEnv}
                onNotify={showNotification}
                status={socialEnvStatus}
                isSyncing={socialEnvSyncing}
            />
        </div>
    );
};

export default App;
