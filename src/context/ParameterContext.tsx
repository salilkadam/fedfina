import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ConversationParameters } from '../types/parameters';
import { ParameterParser } from '../utils/parameterParser';

interface ParameterContextType {
    parameters: ConversationParameters | null;
    isLoading: boolean;
    error: string | null;
    updateParameters: (newParams: Partial<ConversationParameters>) => void;
    refreshParameters: () => void;
}

const ParameterContext = createContext<ParameterContextType | undefined>(undefined);

interface ParameterProviderProps {
    children: ReactNode;
}

export const ParameterProvider: React.FC<ParameterProviderProps> = ({ children }) => {
    const [parameters, setParameters] = useState<ConversationParameters | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const parseAndSetParameters = () => {
        try {
            setIsLoading(true);
            setError(null);

            const parsedParams = ParameterParser.parseParameters();
            setParameters(parsedParams);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to parse parameters';
            setError(errorMessage);
            console.error('Parameter parsing error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        parseAndSetParameters();
    }, []);

    const updateParameters = (newParams: Partial<ConversationParameters>) => {
        if (parameters) {
            const updatedParams = { ...parameters, ...newParams };
            try {
                const validatedParams = ParameterParser.validateParameters(updatedParams);
                setParameters(validatedParams);
                setError(null);
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Invalid parameters';
                setError(errorMessage);
            }
        }
    };

    const refreshParameters = () => {
        parseAndSetParameters();
    };

    const value: ParameterContextType = {
        parameters,
        isLoading,
        error,
        updateParameters,
        refreshParameters,
    };

    return (
        <ParameterContext.Provider value={value}>
            {children}
        </ParameterContext.Provider>
    );
};

export const useParameters = (): ParameterContextType => {
    const context = useContext(ParameterContext);
    if (context === undefined) {
        throw new Error('useParameters must be used within a ParameterProvider');
    }
    return context;
}; 