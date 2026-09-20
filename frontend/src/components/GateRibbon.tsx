import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  OctagonX,
  Play,
  ArrowRight,
} from 'lucide-react';
import { resumeProductionGate, cancelProductionPipeline } from '../services/api';
import type { ProductionOverviewResponse } from '../types/cineflow';

interface GateRibbonProps {
  sessionId: string;
  overview: ProductionOverviewResponse;
  setOverview: React.Dispatch<React.SetStateAction<ProductionOverviewResponse>>;
  isRunning: boolean;
  setIsRunning: (running: boolean) => void;
  onQuickRun?: () => void;
}

export const GateRibbon: React.FC<GateRibbonProps> = ({
  sessionId,
  overview,
  setOverview,
  isRunning,
  setIsRunning,
  onQuickRun,
}) => {
  const [directorNotes, setDirectorNotes] = useState('');
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const activeGate = overview.active_gate || 'IDLE';
  const isPaused = activeGate.startsWith('GATE_');

  const handleGateAction = async (status: 'APPROVED' | 'REJECTED') => {
    setSubmitting(true);
    setActionMessage(`Submitting Director Gate decision (${status})...`);
    try {
      const res = await resumeProductionGate({
        session_id: sessionId,
        interrupt_id: 'gate-001',
        approval_status: status,
        director_notes: directorNotes,
      });
      setActionMessage(res.message || `Gate ${status.toLowerCase()} successfully.`);
      setOverview((prev) => ({
        ...prev,
        active_gate: res.active_gate || (status === 'APPROVED' ? 'GATE_2_ASSETS' : 'GATE_1_PREPROD'),
      }));
      setDirectorNotes('');
    } catch (err) {
      console.error(err);
      setActionMessage('Failed to submit gate action.');
    } finally {
      setSubmitting(false);
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to abort the current production pipeline?')) {
      return;
    }
    setSubmitting(true);
    setActionMessage('Aborting production pipeline...');
    try {
      const res = await cancelProductionPipeline({
        session_id: sessionId,
        reason: directorNotes || 'Aborted by Director from Studio Console',
      });
      setIsRunning(false);
      setActionMessage(res.message || 'Pipeline aborted.');
      setOverview((prev) => ({
        ...prev,
        active_gate: 'IDLE',
      }));
    } catch (err) {
      console.error(err);
      setActionMessage('Failed to abort pipeline.');
    } finally {
      setSubmitting(false);
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  // Stepper state
  const isPhase1Done = activeGate === 'GATE_2_ASSETS' || activeGate === 'GATE_3_FINAL' || activeGate === 'COMPLETED';
  const isPhase2Done = activeGate === 'GATE_3_FINAL' || activeGate === 'COMPLETED';
  const isPhase3Done = activeGate === 'COMPLETED';

  return (
    <div
      className={`gate-ribbon ${
        isRunning ? 'gate-running' : isPaused ? 'gate-paused' : ''
      }`}
    >
      {/* Left: Stage Stepper */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div className="gate-stage-stepper">
          <div
            className={`gate-stage-step ${
              isPhase1Done ? 'completed' : activeGate === 'GATE_1_PREPROD' ? 'active' : ''
            }`}
          >
            {isPhase1Done ? <CheckCircle2 size={13} /> : <span>1</span>}
            <span>Pre-Prod (Script/Cast)</span>
          </div>

          <ArrowRight size={12} color="var(--text-dim)" />

          <div
            className={`gate-stage-step ${
              isPhase2Done ? 'completed' : activeGate === 'GATE_2_ASSETS' ? 'active' : ''
            }`}
          >
            {isPhase2Done ? <CheckCircle2 size={13} /> : <span>2</span>}
            <span>Asset Gen (Shots/Audio)</span>
          </div>

          <ArrowRight size={12} color="var(--text-dim)" />

          <div
            className={`gate-stage-step ${
              isPhase3Done ? 'completed' : activeGate === 'GATE_3_FINAL' ? 'active' : ''
            }`}
          >
            {isPhase3Done ? <CheckCircle2 size={13} /> : <span>3</span>}
            <span>Assembly & QA</span>
          </div>
        </div>

        {actionMessage && (
          <span
            style={{
              fontSize: '0.8rem',
              color: 'var(--cyan)',
              background: 'rgba(6, 182, 212, 0.1)',
              padding: '0.2rem 0.6rem',
              borderRadius: '4px',
              border: '1px solid rgba(6, 182, 212, 0.2)',
            }}
          >
            {actionMessage}
          </span>
        )}
      </div>

      {/* Right: Contextual Operator Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {isRunning ? (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--cyan)' }}>
              <RefreshCw size={15} className="animate-spin" />
              <span style={{ fontSize: '0.825rem', fontWeight: 600 }}>Executing Pipeline DAG...</span>
            </div>
            <button
              className="btn btn-danger"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={handleCancel}
              disabled={submitting}
            >
              <OctagonX size={14} />
              Abort Run
            </button>
          </>
        ) : isPaused ? (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <AlertTriangle size={15} color="#f59e0b" />
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: '#fbbf24' }}>
                Director Gate: {activeGate}
              </span>
            </div>

            <input
              type="text"
              className="form-control"
              placeholder="Director revision notes (optional)..."
              value={directorNotes}
              onChange={(e) => setDirectorNotes(e.target.value)}
              style={{ width: '260px', padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
            />

            <button
              className="btn btn-success"
              style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}
              onClick={() => handleGateAction('APPROVED')}
              disabled={submitting}
            >
              <CheckCircle2 size={14} />
              Approve & Advance
            </button>

            <button
              className="btn btn-outline"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', color: '#fbbf24', borderColor: 'rgba(245, 158, 11, 0.4)' }}
              onClick={() => handleGateAction('REJECTED')}
              disabled={submitting}
            >
              <XCircle size={14} />
              Request Revision
            </button>

            <button
              className="btn btn-outline"
              style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem', color: '#f87171' }}
              onClick={handleCancel}
              disabled={submitting}
              title="Abort production pipeline"
            >
              <OctagonX size={14} />
            </button>
          </>
        ) : (
          <>
            <span className="badge badge-green">Pipeline Ready</span>
            {onQuickRun && (
              <button
                className="btn btn-primary"
                style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}
                onClick={onQuickRun}
              >
                <Play size={13} />
                Run Scene Pipeline
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
};
