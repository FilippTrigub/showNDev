export interface SocialEnvValues {
    twitterApiKey: string;
    twitterApiSecretKey: string;
    twitterAccessToken: string;
    twitterAccessTokenSecret: string;
    blueskyIdentifier: string;
    blueskyAppPassword: string;
    blueskyServiceUrl: string;
    linkedinClientId: string;
    linkedinClientSecret: string;
    linkedinRedirectUri: string;
}

export const defaultSocialEnvValues: SocialEnvValues = {
    twitterApiKey: '',
    twitterApiSecretKey: '',
    twitterAccessToken: '',
    twitterAccessTokenSecret: '',
    blueskyIdentifier: '',
    blueskyAppPassword: '',
    blueskyServiceUrl: 'https://bsky.social',
    linkedinClientId: '',
    linkedinClientSecret: '',
    linkedinRedirectUri: 'http://localhost:3000/callback',
};

export type SocialEnvFieldKey = keyof SocialEnvValues;

interface SocialEnvFieldConfig {
    envVar: string;
    label: string;
    placeholder?: string;
    helperText?: string;
    type?: 'text' | 'password' | 'url';
}

export const SOCIAL_ENV_FIELD_CONFIG: Record<SocialEnvFieldKey, SocialEnvFieldConfig> = {
    twitterApiKey: {
        envVar: 'TWITTER_API_KEY',
        label: 'Twitter/X API Key',
        placeholder: 'your_twitter_api_key',
    },
    twitterApiSecretKey: {
        envVar: 'TWITTER_API_SECRET_KEY',
        label: 'Twitter/X API Secret Key',
        placeholder: 'your_twitter_api_secret',
    },
    twitterAccessToken: {
        envVar: 'TWITTER_ACCESS_TOKEN',
        label: 'Twitter/X Access Token',
        placeholder: 'your_twitter_access_token',
    },
    twitterAccessTokenSecret: {
        envVar: 'TWITTER_ACCESS_TOKEN_SECRET',
        label: 'Twitter/X Access Token Secret',
        placeholder: 'your_twitter_access_token_secret',
    },
    blueskyIdentifier: {
        envVar: 'BLUESKY_IDENTIFIER',
        label: 'Bluesky Identifier',
        placeholder: 'yourname.bsky.social',
    },
    blueskyAppPassword: {
        envVar: 'BLUESKY_APP_PASSWORD',
        label: 'Bluesky App Password',
        placeholder: 'app-specific password',
        type: 'password',
    },
    blueskyServiceUrl: {
        envVar: 'BLUESKY_SERVICE_URL',
        label: 'Bluesky Service URL',
        placeholder: 'https://bsky.social',
        type: 'url',
        helperText: 'Use default unless pointing to a custom PDS.',
    },
    linkedinClientId: {
        envVar: 'LINKEDIN_CLIENT_ID',
        label: 'LinkedIn Client ID',
        placeholder: 'your_linkedin_client_id',
    },
    linkedinClientSecret: {
        envVar: 'LINKEDIN_CLIENT_SECRET',
        label: 'LinkedIn Client Secret',
        placeholder: 'your_linkedin_client_secret',
        type: 'password',
    },
    linkedinRedirectUri: {
        envVar: 'LINKEDIN_REDIRECT_URI',
        label: 'LinkedIn Redirect URI',
        placeholder: 'http://localhost:3000/callback',
        type: 'url',
        helperText: 'Must match the redirect URI registered with LinkedIn.',
    },
};

export const SOCIAL_ENV_SECTIONS: Array<{ title: string; description: string; fields: SocialEnvFieldKey[] }> = [
    {
        title: 'Twitter / X',
        description: 'Required for posting via the Twitter MCP adapter.',
        fields: ['twitterApiKey', 'twitterApiSecretKey', 'twitterAccessToken', 'twitterAccessTokenSecret'],
    },
    {
        title: 'Bluesky',
        description: 'Credentials for the Bluesky MCP integration.',
        fields: ['blueskyIdentifier', 'blueskyAppPassword', 'blueskyServiceUrl'],
    },
    {
        title: 'LinkedIn',
        description: 'OAuth client information for LinkedIn automation.',
        fields: ['linkedinClientId', 'linkedinClientSecret', 'linkedinRedirectUri'],
    },
];

export const buildSocialEnvSnippet = (values: SocialEnvValues): string => [
    `TWITTER_API_KEY=${values.twitterApiKey}`,
    `TWITTER_API_SECRET_KEY=${values.twitterApiSecretKey}`,
    `TWITTER_ACCESS_TOKEN=${values.twitterAccessToken}`,
    `TWITTER_ACCESS_TOKEN_SECRET=${values.twitterAccessTokenSecret}`,
    `BLUESKY_IDENTIFIER=${values.blueskyIdentifier}`,
    `BLUESKY_APP_PASSWORD=${values.blueskyAppPassword}`,
    `BLUESKY_SERVICE_URL=${values.blueskyServiceUrl}`,
    `LINKEDIN_CLIENT_ID=${values.linkedinClientId}`,
    `LINKEDIN_CLIENT_SECRET=${values.linkedinClientSecret}`,
    `LINKEDIN_REDIRECT_URI=${values.linkedinRedirectUri}`,
].join('\n');

export const SOCIAL_ENV_FIELD_API_KEYS: Record<SocialEnvFieldKey, string> = {
    twitterApiKey: 'twitter_api_key',
    twitterApiSecretKey: 'twitter_api_secret_key',
    twitterAccessToken: 'twitter_access_token',
    twitterAccessTokenSecret: 'twitter_access_token_secret',
    blueskyIdentifier: 'bluesky_identifier',
    blueskyAppPassword: 'bluesky_app_password',
    blueskyServiceUrl: 'bluesky_service_url',
    linkedinClientId: 'linkedin_client_id',
    linkedinClientSecret: 'linkedin_client_secret',
    linkedinRedirectUri: 'linkedin_redirect_uri',
};

export type SocialEnvStatusMap = Record<string, boolean>;

export const toSocialEnvApiPayload = (values: SocialEnvValues): Record<string, string> => {
    const payload: Record<string, string> = {};
    (Object.keys(SOCIAL_ENV_FIELD_API_KEYS) as SocialEnvFieldKey[]).forEach((field) => {
        const apiKey = SOCIAL_ENV_FIELD_API_KEYS[field];
        payload[apiKey] = values[field];
    });
    return payload;
};
