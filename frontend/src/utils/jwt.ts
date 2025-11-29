/**
 * JWT Utilities - Token validation and expiration handling
 */

export interface DecodedToken {
    sub: string;
    username: string;
    role: string;
    scope: string;
    iat: number;
    exp: number;
}

/**
 * Decode JWT token without verification (client-side only for expiration check)
 */
export function decodeToken(token: string): DecodedToken | null {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) {
            return null;
        }

        const payload = parts[1];
        if (!payload) {
            return null;
        }

        const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));

        return decoded as DecodedToken;
    } catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) {
        return true;
    }

    // exp is in seconds, Date.now() is in milliseconds
    const expirationTime = decoded.exp * 1000;
    const currentTime = Date.now();

    return currentTime >= expirationTime;
}

/**
 * Get remaining time in seconds until token expires
 */
export function getTokenRemainingTime(token: string): number {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) {
        return 0;
    }

    const expirationTime = decoded.exp * 1000;
    const currentTime = Date.now();
    const remainingMs = expirationTime - currentTime;

    return Math.max(0, Math.floor(remainingMs / 1000));
}

/**
 * Get token expiration date
 */
export function getTokenExpirationDate(token: string): Date | null {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) {
        return null;
    }

    return new Date(decoded.exp * 1000);
}

/**
 * Check if token will expire soon (within specified minutes)
 */
export function willTokenExpireSoon(token: string, minutesThreshold: number = 5): boolean {
    const remainingSeconds = getTokenRemainingTime(token);
    return remainingSeconds > 0 && remainingSeconds <= (minutesThreshold * 60);
}
