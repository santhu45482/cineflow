import React from 'react';
import {
  Clapperboard,
  SlidersHorizontal,
  Activity,
  Layers,
  Cpu,
} from 'lucide-react';

interface HeaderProps {
  sessionId: string;
  setSessionId: (id: string) => void;
  backendHealth: { online: boolean; message: string };
  gcpProject: string;
  activeMode: 'director' | 'operations';
  setActiveMode: (mode: 'director' | 'operations') => void;
  onOpenOpticsDrawer: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  sessionId,
  setSessionId,
  backendHealth,
  gcpProject,
  activeMode,
  setActiveMode,
  onOpenOpticsDrawer,
}) => {
  return (
    <header className="top-header">
      {/* Brand & GCP Badge */}
      <div className="header-brand">
        <Clapperboard size={26} color="#f59e0b" />
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h1>CineFlow Studio</h1>
            <span
              style={{
                fontSize: '0.68rem',
                color: 'var(--cyan)',
                background: 'rgba(6, 182, 212, 0.12)',
                padding: '0.15rem 0.45rem',
                borderRadius: '4px',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                fontWeight: 600,
                letterSpacing: '0.5px',
              }}
            >
              GCP: {gcpProject}
            </span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)', letterSpacing: '0.3px' }}>
            Autonomous Multi-Agent Cinema Engine • Vertex AI
          </p>
        </div>
      </div>

      {/* Center: Mode Switcher (Director Deck vs Cloud Ops) */}
      <div className="mode-switcher">
        <button
          className={`mode-btn ${activeMode === 'director' ? 'active' : ''}`}
          onClick={() => setActiveMode('director')}
        >
          <Layers size={14} />
          <span>Director Deck</span>
        </button>

        <button
          className={`mode-btn ${activeMode === 'operations' ? 'active' : ''}`}
          onClick={() => setActiveMode('operations')}
        >
          <Activity size={14} />
          <span>Cloud Ops & SRE</span>
        </button>
      </div>

      {/* Right Controls: Health, Session, Optics Drawer Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Backend Status Pip */}
        <div
          className={`badge ${backendHealth.online ? 'badge-green' : 'badge-gold'}`}
          title={backendHealth.message}
          style={{ padding: '0.35rem 0.7rem', fontSize: '0.75rem' }}
        >
          <Cpu size={13} />
          <span>{backendHealth.online ? 'ADK 2.0 Connected' : 'Offline Mode'}</span>
        </div>

        {/* Session ID */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600 }}>SESSION:</span>
          <input
            type="text"
            className="form-control"
            style={{ width: '150px', padding: '0.3rem 0.5rem', fontSize: '0.78rem' }}
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
          />
        </div>

        {/* Optics & Settings Drawer Button */}
        <button
          className="btn btn-outline"
          onClick={onOpenOpticsDrawer}
          style={{
            padding: '0.4rem 0.8rem',
            fontSize: '0.8rem',
            gap: '0.4rem',
            borderColor: 'var(--border)',
          }}
          title="Open Optics & Studio Governance Settings"
        >
          <SlidersHorizontal size={14} color="#f59e0b" />
          <span>Optics & Config</span>
        </button>
      </div>
    </header>
  );
};
