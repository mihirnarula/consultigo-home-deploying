const config = {
    API_URL: process.env.NODE_ENV === 'production'
        ? 'https://your-production-api.railway.app/api/v1'
        : 'http://localhost:8000/api/v1',
    API_TIMEOUT: 30000,
    ENVIRONMENT: process.env.NODE_ENV || 'development',
    VERSION: '1.0.0',
    ENABLE_LOGS: process.env.NODE_ENV !== 'production',
};

// API endpoints
const endpoints = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        REFRESH: '/auth/refresh',
        LOGOUT: '/auth/logout',
    },
    USERS: {
        PROFILE: '/users/profile',
        UPDATE: '/users/update',
    },
    PROBLEMS: {
        LIST: '/problems',
        DETAIL: (id) => `/problems/${id}`,
        SUBMIT: (id) => `/problems/${id}/submit`,
    },
    SUBMISSIONS: {
        LIST: '/submissions',
        DETAIL: (id) => `/submissions/${id}`,
    },
};

// Error handling
const handleApiError = async (response) => {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'An unexpected error occurred');
    }
    return response.json();
};

// API request helper
const apiRequest = async (endpoint, options = {}) => {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        timeout: config.API_TIMEOUT,
    };

    const requestOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.API_TIMEOUT);

        const response = await fetch(`${config.API_URL}${endpoint}`, {
            ...requestOptions,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);
        return handleApiError(response);
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        throw error;
    }
};

// Logging utility
const logger = {
    log: (...args) => config.ENABLE_LOGS && console.log(...args),
    error: (...args) => config.ENABLE_LOGS && console.error(...args),
    warn: (...args) => config.ENABLE_LOGS && console.warn(...args),
    info: (...args) => config.ENABLE_LOGS && console.info(...args),
};

// Export configuration
window.appConfig = {
    ...config,
    endpoints,
    apiRequest,
    logger,
}; 