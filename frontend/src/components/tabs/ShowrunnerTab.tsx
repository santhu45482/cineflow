import React, { useState } from 'react';
import { Play, CheckCircle2, XCircle, AlertTriangle, Sparkles, Clock, RefreshCw } from 'lucide-react';
import type { ProductionOverviewResponse } from '../../types/cineflow';
import { triggerProductionPipeline, resumeProductionGate } from '../../services/api';

interface ShowrunnerTabProps {
  overview: ProductionOverviewResponse;
  setOverview: React.Dispatch<React.SetStateAction<ProductionOverviewResponse>>;
  sessionId: string;
  opticsConfig: any;
}

export const ShowrunnerTab: React.FC<ShowrunnerTabProps> = ({
  overview,
  setOverview,
  sessionId,
  opticsConfig,
}) => {
  const [premise, setPremise] = useState(
    'A rogue cybernetic investigator in rain-drenched Neo-Bangalore 2088 uncovers a black-market memory trading cartel operating beneath sub-level 9.'
  );
  const [directorNotes, setDirectorNotes] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const handleStartProduction = async () => {
    setIsRunning(true);
    setStatusMessage('Showrunner initiating ADK 2.0 Graph Pipeline...');
    try {
      const res = await triggerProductionPipeline({
        session_id: sessionId,
        premise,
        genre: overview.genre,
        runtime_optics: opticsConfig,
      });
      setStatusMessage(res.message || 'Production dispatched.');
      setOverview((prev) => ({
        ...prev,
        active_gate: res.active_gate || 'GATE_1_PREPROD',
      }));
    } finally {
      setIsRunning(false);
    }
  };

  const handleGateAction = async (status: 'APPROVED' | 'REJECTED') => {
    setStatusMessage(`Submitting Director Gate decision (${status})...`);
    try {
      const currentInterruptId = overview.active_gate === 'GATE_2_ASSETS' ? 'gate_2_approval' : 'gate_1_approval';
      const res = await resumeProductionGate({
        session_id: sessionId || 'director-session-default',
        interrupt_id: currentInterruptId,
        approval_status: status,
        director_notes: directorNotes,
      });
      setStatusMessage(res.message);
      setOverview((prev) => ({
        ...prev,
        active_gate: res.active_gate || prev.active_gate,
      }));
      setDirectorNotes('');
    } catch (err) {
      console.error(err);
      setStatusMessage('Error submitting gate decision.');
    }
  };

  return (
    <div className="tab-content">
      {/* Executive Premise Input */}
      <div className="card">
        <h2 className="card-title">
          <Sparkles color="#f59e0b" size={20} />
          Executive Direction & Movie Premise
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.875rem' }}>
          Provide the foundational story logline. The Executive Showrunner (Gemini 3.7 Flash) will orchestrate screenwriting, casting seeds, shot breakdown, and score composition.
        </p>

        <div className="form-group">
          <textarea
            className="form-control"
            rows={3}
            value={premise}
            onChange={(e) => setPremise(e.target.value)}
            placeholder="Describe the cinematic premise, tone, and character dynamics..."
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button
            className="btn btn-primary"
            onClick={handleStartProduction}
            disabled={isRunning}
          >
            {isRunning ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Executing Pipeline DAG...
              </>
            ) : (
              <>
                <Play size={16} />
                Run Production Pipeline (ADK 2.0)
              </>
            )}
          </button>

          {statusMessage && (
            <span style={{ fontSize: '0.85rem', color: 'var(--cyan)' }}>
              {statusMessage}
            </span>
          )}
        </div>
      </div>

      {/* Human-in-the-Loop Gate Approval Banner */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid #f59e0b',
          background: 'linear-gradient(180deg, #161f30 0%, #111724 100%)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <AlertTriangle size={18} color="#f59e0b" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                Director Milestone Gate: <span style={{ color: '#f59e0b' }}>{overview.active_gate}</span>
              </h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Deterministic pause point. Review outputs below and sign off before high-compute rendering proceeds.
            </p>
          </div>
          <span className="badge badge-gold">PAUSED FOR HITL APPROVAL</span>
        </div>

        <div className="form-group">
          <label className="form-label">Director Revision Notes (Optional)</label>
          <input
            type="text"
            className="form-control"
            placeholder="e.g. Increase rain density in Shot 1, keep lighting high-contrast neon purple"
            value={directorNotes}
            onChange={(e) => setDirectorNotes(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            className="btn btn-success"
            onClick={() => handleGateAction('APPROVED')}
          >
            <CheckCircle2 size={16} />
            Approve & Advance Production Gate
          </button>

          <button
            className="btn btn-danger"
            onClick={() => handleGateAction('REJECTED')}
          >
            <XCircle size={16} />
            Request Department Revision
          </button>
        </div>
      </div>

      {/* Pipeline Stages Overview */}
      <div className="card">
        <h3 className="card-title">
          <Clock size={18} color="#06b6d4" />
          Autonomous Multi-Agent Pipeline DAG Lifecycle
        </h3>
        <div className="grid-3" style={{ marginTop: '1rem' }}>
          <div style={{ background: 'var(--bg-darkest)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <p style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem' }}>PHASE 1: PRE-PRODUCTION</p>
            <h4 style={{ margin: '0.25rem 0', fontSize: '0.95rem' }}>Script & Casting Bible</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Fountain screenplay formatting, beat-sheet extraction, and deterministic character seed locks.
            </p>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-green">COMPLETED</span>
            </div>
          </div>

          <div style={{ background: 'var(--bg-darkest)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <p style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem' }}>PHASE 2: ASSET GENERATION</p>
            <h4 style={{ margin: '0.25rem 0', fontSize: '0.95rem' }}>Storyboards, Audio & Score</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Parallel rendering via Imagen 3 (Gemini 3.1 Flash Image), dialogue TTS stems, and Lyria-3.5 score.
            </p>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-gold">ACTIVE / READY</span>
            </div>
          </div>

          <div style={{ background: 'var(--bg-darkest)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <p style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem' }}>PHASE 3: ASSEMBLY & QA</p>
            <h4 style={{ margin: '0.25rem 0', fontSize: '0.95rem' }}>Timeline Assembly & Cut</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              FFmpeg container stitching, multimodal QA continuity grading, and animatic package delivery.
            </p>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-purple">QUEUED</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
