import React from 'react';
import { FileText, Film, Bookmark } from 'lucide-react';
import type { ProductionOverviewResponse } from '../../types/cineflow';

interface ScreenplayTabProps {
  overview: ProductionOverviewResponse;
}

export const ScreenplayTab: React.FC<ScreenplayTabProps> = ({ overview }) => {
  return (
    <div className="tab-content">
      {/* Script Header Meta */}
      <div className="card">
        <h2 className="card-title">
          <Film color="#f59e0b" size={20} />
          Screenplay & Narrative Architecture: {overview.title}
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <span className="form-label">Genre</span>
            <p style={{ fontWeight: 600, color: 'var(--cyan)' }}>{overview.genre}</p>
          </div>
          <div>
            <span className="form-label">Theme</span>
            <p style={{ fontWeight: 500, color: 'var(--text-main)', fontSize: '0.85rem' }}>{overview.theme}</p>
          </div>
          <div>
            <span className="form-label">Scene Count</span>
            <p style={{ fontWeight: 600, color: 'var(--accent)' }}>1 Scene ({overview.shots.length} Planned Shots)</p>
          </div>
        </div>
      </div>

      {/* Screenplay Document Viewer */}
      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">
            <FileText size={18} color="#06b6d4" />
            Fountain Screenplay (Scene 1)
          </h3>
          <div
            style={{
              fontFamily: 'Courier New, Courier, monospace',
              background: 'var(--bg-darkest)',
              padding: '1.25rem',
              borderRadius: '6px',
              border: '1px solid var(--border)',
              lineHeight: '1.6',
              fontSize: '0.85rem',
              whiteSpace: 'pre-wrap',
            }}
          >
            {`EXT. NEO-BANGALORE - SUB-LEVEL 9 - NIGHT (RAIN)

Torrential rain lashes holographic advertisements reflecting off pooled water in narrow alleys. Steam erupts from rusted ventilation grates.

A figure steps out from the shadows. KADE MERCER (40s), synth-eye glowing a faint cobalt blue, coat soaked.

He strikes an electric match. The flare illuminates weary eyes.

KADE
(to himself)
Every memory in this city has a price tag. Even the ones you thought were yours.

He halts before a neon-lit stall. NYX VANE (30s) watches him from behind steam, silver hair shimmering.

NYX
You're late, Mercer. The Syndicate already knows which neural shard we pulled.

Kade glares, pulling back his coat to reveal an encrypted datachip.

KADE
Then we have four minutes before the perimeter collapses.`}
          </div>
        </div>

        {/* Narrative Beats */}
        <div className="card">
          <h3 className="card-title">
            <Bookmark size={18} color="#8b5cf6" />
            Decomposed Story Beats & Pacing
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ background: 'var(--bg-darkest)', padding: '0.9rem', borderRadius: '6px', borderLeft: '3px solid #3b82f6' }}>
              <span className="badge badge-blue">BEAT 1 • ESTABLISHING</span>
              <h4 style={{ margin: '0.3rem 0', fontSize: '0.9rem' }}>Rain-Drenched Dystopian Atmosphere</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Visual framing establishing high density, neon light reflections, and environmental isolation.
              </p>
            </div>

            <div style={{ background: 'var(--bg-darkest)', padding: '0.9rem', borderRadius: '6px', borderLeft: '3px solid #f59e0b' }}>
              <span className="badge badge-gold">BEAT 2 • CHARACTER INTRODUCTION</span>
              <h4 style={{ margin: '0.3rem 0', fontSize: '0.9rem' }}>Kade Mercer Cynical Monologue</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Establishes the core thematic premise: commodification of synthetic memories in Neo-Bangalore.
              </p>
            </div>

            <div style={{ background: 'var(--bg-darkest)', padding: '0.9rem', borderRadius: '6px', borderLeft: '3px solid #8b5cf6' }}>
              <span className="badge badge-purple">BEAT 3 • RENDEZVOUS & THREAT INJECTION</span>
              <h4 style={{ margin: '0.3rem 0', fontSize: '0.9rem' }}>Encounter with Nyx Vane</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Tension escalates. Syndicate alert triggers high-tempo pacing transition towards asset generation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
