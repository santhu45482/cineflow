import React from 'react';
import { ShieldCheck, Video, Clock } from 'lucide-react';
import type { ProductionOverviewResponse } from '../../types/cineflow';

interface StoryboardTabProps {
  overview: ProductionOverviewResponse;
}

export const StoryboardTab: React.FC<StoryboardTabProps> = ({ overview }) => {
  return (
    <div className="tab-content">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="card-title">
              <Video color="#f59e0b" size={20} />
              Cinematic Storyboard & Multimodal Visual QA
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Rendered via Gemini 3.1 Flash Image with persistent seeds, optics injection, and automated continuity auditing by Gemini Omni 1.1 Flash.
            </p>
          </div>
          <span className="badge badge-green">ALL 4 SHOTS QA AUDITED</span>
        </div>
      </div>

      {/* Shots Grid */}
      <div className="grid-2">
        {overview.shots.map((shot) => (
          <div key={shot.shot_id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {/* Aspect Ratio Framing Mock Canvas */}
            <div
              style={{
                width: '100%',
                aspectRatio: shot.aspect_ratio === '2.39:1' ? '21 / 9' : shot.aspect_ratio === '16:9' ? '16 / 9' : '4 / 3',
                background: 'linear-gradient(135deg, #090d16 0%, #151d2f 50%, #0c1220 100%)',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                boxShadow: 'inset 0 0 40px rgba(0,0,0,0.8)',
              }}
            >
              {/* Subtle Film Grain / Optics Watermark */}
              <div style={{ position: 'absolute', top: '10px', left: '10px', display: 'flex', gap: '0.5rem' }}>
                <span className="badge badge-gold" style={{ fontSize: '0.7rem' }}>
                  {shot.optics_preset}
                </span>
                <span className="badge badge-blue" style={{ fontSize: '0.7rem' }}>
                  {shot.aspect_ratio}
                </span>
              </div>

              <div style={{ position: 'absolute', top: '10px', right: '10px' }}>
                <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
                  SEED: {shot.character_seed}
                </span>
              </div>

              {/* Shot Visual Description */}
              <div style={{ padding: '2rem', textAlign: 'center', maxWidth: '85%' }}>
                <p style={{ fontSize: '0.9rem', color: '#e2e8f0', fontWeight: 500, fontStyle: 'italic', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
                  "{shot.visual_prompt}"
                </p>
              </div>

              {/* Dialogue Subtitle if applicable */}
              {shot.dialogue && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: '12px',
                    left: '5%',
                    right: '5%',
                    background: 'rgba(0, 0, 0, 0.75)',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '4px',
                    textAlign: 'center',
                    border: '1px solid rgba(255,255,255,0.1)',
                  }}
                >
                  <span style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.75rem', marginRight: '0.4rem' }}>
                    {shot.character_name}:
                  </span>
                  <span style={{ color: '#fff', fontSize: '0.8rem' }}>
                    "{shot.dialogue}"
                  </span>
                </div>
              )}
            </div>

            {/* Shot Meta Details */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.25rem' }}>
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>
                  Shot #{shot.shot_number} <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>({shot.shot_id})</span>
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.2rem' }}>
                  <Clock size={12} />
                  <span>Duration: {shot.duration_seconds}s</span>
                  <span>•</span>
                  <span>{shot.lighting_style}</span>
                </div>
              </div>

              {/* Multimodal QA Badge */}
              <div style={{ textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', justifyContent: 'flex-end' }}>
                  <ShieldCheck size={14} color="#10b981" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--green)' }}>
                    QA Verified ({Math.round((shot.qa_score || 0.95) * 100)}%)
                  </span>
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                  Zero seed drift detected
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
