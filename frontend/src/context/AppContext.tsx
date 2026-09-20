import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Session, Profile } from '../api/types';

interface SavedSession {
  sessionId: string;
  profileId: string;
  createdAt: string;
  status: string;
}

interface AppContextType {
  currentSession: Session | null;
  setCurrentSession: (session: Session | null) => void;
  profiles: Profile[];
  setProfiles: (profiles: Profile[]) => void;
  savedSessions: SavedSession[];
  saveSession: (session: SavedSession) => void;
  updateSavedSessionStatus: (sessionId: string, status: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const STORAGE_KEY = 'pramaan_sessions';

function loadSessions(): SavedSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function persistSessions(sessions: SavedSession[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [savedSessions, setSavedSessions] = useState<SavedSession[]>(loadSessions);

  const saveSession = useCallback((session: SavedSession) => {
    setSavedSessions((prev) => {
      const exists = prev.find((s) => s.sessionId === session.sessionId);
      const updated = exists
        ? prev.map((s) => (s.sessionId === session.sessionId ? session : s))
        : [session, ...prev];
      persistSessions(updated);
      return updated;
    });
  }, []);

  const updateSavedSessionStatus = useCallback((sessionId: string, status: string) => {
    setSavedSessions((prev) => {
      const updated = prev.map((s) =>
        s.sessionId === sessionId ? { ...s, status } : s
      );
      persistSessions(updated);
      return updated;
    });
  }, []);

  return (
    <AppContext.Provider
      value={{
        currentSession,
        setCurrentSession,
        profiles,
        setProfiles,
        savedSessions,
        saveSession,
        updateSavedSessionStatus,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextType {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
