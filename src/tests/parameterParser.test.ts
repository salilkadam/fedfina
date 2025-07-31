import { ParameterParser } from '../utils/parameterParser';
import { ConversationParameters } from '../types/parameters';

// Mock window.location
const mockLocation = (search: string) => {
    Object.defineProperty(window, 'location', {
        value: {
            search,
            href: `http://localhost:3000${search}`
        },
        writable: true
    });
};

describe('ParameterParser', () => {
    beforeEach(() => {
        // Reset window.location before each test
        mockLocation('');
    });

    describe('parseParameters', () => {
        it('should parse valid parameters', () => {
            mockLocation('?emailId=user@example.com&accountId=acc123');

            const result = ParameterParser.parseParameters();

            expect(result).toEqual({
                emailId: 'user@example.com',
                accountId: 'acc123',
                sessionId: undefined,
                metadata: undefined
            });
        });

        it('should parse parameters with session ID', () => {
            mockLocation('?emailId=user@example.com&accountId=acc123&sessionId=550e8400-e29b-41d4-a716-446655440000');

            const result = ParameterParser.parseParameters();

            expect(result).toEqual({
                emailId: 'user@example.com',
                accountId: 'acc123',
                sessionId: '550e8400-e29b-41d4-a716-446655440000',
                metadata: undefined
            });
        });

        it('should parse metadata parameter', () => {
            const metadata = { source: 'android', version: '1.0' };
            const encodedMetadata = encodeURIComponent(JSON.stringify(metadata));
            mockLocation(`?emailId=user@example.com&accountId=acc123&metadata=${encodedMetadata}`);

            const result = ParameterParser.parseParameters();

            expect(result).toEqual({
                emailId: 'user@example.com',
                accountId: 'acc123',
                sessionId: undefined,
                metadata
            });
        });
    });

    describe('validateParameters', () => {
        it('should validate correct parameters', () => {
            const params: ConversationParameters = {
                emailId: 'user@example.com',
                accountId: 'acc123'
            };

            const result = ParameterParser.validateParameters(params);
            expect(result).toEqual(params);
        });

        it('should throw error for invalid email', () => {
            const params: ConversationParameters = {
                emailId: 'invalid-email',
                accountId: 'acc123'
            };

            expect(() => ParameterParser.validateParameters(params)).toThrow('emailId must be a valid email format');
        });

        it('should throw error for invalid account ID', () => {
            const params: ConversationParameters = {
                emailId: 'user@example.com',
                accountId: 'ab' // Too short
            };

            expect(() => ParameterParser.validateParameters(params)).toThrow('accountId must be alphanumeric, 3-50 characters');
        });

        it('should throw error for invalid session ID', () => {
            const params: ConversationParameters = {
                emailId: 'user@example.com',
                accountId: 'acc123',
                sessionId: 'invalid-uuid'
            };

            expect(() => ParameterParser.validateParameters(params)).toThrow('sessionId must be a valid UUID format');
        });
    });

    describe('toSearchString', () => {
        it('should convert parameters to search string', () => {
            const params: ConversationParameters = {
                emailId: 'user@example.com',
                accountId: 'acc123',
                sessionId: '550e8400-e29b-41d4-a716-446655440000',
                metadata: { source: 'android' }
            };

            const result = ParameterParser.toSearchString(params);

            expect(result).toContain('emailId=user%40example.com');
            expect(result).toContain('accountId=acc123');
            expect(result).toContain('sessionId=550e8400-e29b-41d4-a716-446655440000');
            expect(result).toContain('metadata=');
        });
    });

    describe('hasRequiredParameters', () => {
        it('should return true when required parameters are present', () => {
            mockLocation('?emailId=user@example.com&accountId=acc123');

            const result = ParameterParser.hasRequiredParameters();

            expect(result).toBe(true);
        });

        it('should return false when required parameters are missing', () => {
            mockLocation('?emailId=user@example.com'); // Missing accountId

            const result = ParameterParser.hasRequiredParameters();

            expect(result).toBe(false);
        });

        it('should return false when parameters are invalid', () => {
            mockLocation('?emailId=invalid-email&accountId=acc123');

            const result = ParameterParser.hasRequiredParameters();

            expect(result).toBe(false);
        });
    });
}); 