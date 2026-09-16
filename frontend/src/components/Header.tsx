import React from 'react';
import { Clapperboard, ShieldCheck, Activity, Cpu } from 'lucide-react';

interface HeaderProps {
  sessionId: string;
  setSessionId: (id: string) => void;
  backendHealth: { online: boolean; message: string };
  gcpProject: string;
  activeGate: string;
}

export const Header: React.FC<HeaderProps> = ({
  sessionId,
  setSessionId,
  backendHealth,
  gcpProject,
  activeGate,
}) => {
  return (
    <header className="top-header">
      <div className="header-brand">
        <Clapperboard size={28} color="#f59e0b" />
        <div>
          <h1>CineFlow Studio</h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', letterSpacing: '0.5px' }}>
            AUTONOMOUS MULTI-AGENT CINEMA ENGINE • GCP: {gcpProject}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* HITL Gate Status */}
        <div className="badge badge-gold" style={{ padding: '0.4rem 0.8rem' }}>
          <Cpu size={14} />
          <span>ACTIVE GATE: {activeGate}</span>
        </div>

        {/* Google Model Armor Guard */}
        <div className="badge badge-purple" style={{ padding: '0.4rem 0.8rem' }}>
          <ShieldCheck size={14} />
          <span>Model Armor: Enforced</span>
        </div>

        {/* Backend Status */}
        <div
          className={`badge ${backendHealth.online ? 'badge-green' : 'badge-gold'}`}
          style={{ padding: '0.4rem 0.8rem' }}
        >
          <Activity size={14} />
          <span>{backendHealth.message}</span>
        </div>

        {/* Session ID Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>SESSION:</span>
          <input
            type="text"
            className="form-control"
            style={{ width: '160px', padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
          />
        </div>
      </div>
    </header>
  );
};
