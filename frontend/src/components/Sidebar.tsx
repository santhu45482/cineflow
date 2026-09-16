import React from 'react';
import { Camera, Sliders, Cloud } from 'lucide-react';
import type { RuntimeOpticsConfig } from '../types/cineflow';

interface SidebarProps {
  opticsConfig: RuntimeOpticsConfig;
  setOpticsConfig: React.Dispatch<React.SetStateAction<RuntimeOpticsConfig>>;
  gcpProject: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  opticsConfig,
  setOpticsConfig,
  gcpProject,
}) => {
  return (
    <aside className="sidebar">
      <div>
        <h3
          style={{
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            color: 'var(--text-dim)',
            letterSpacing: '1px',
            marginBottom: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Cloud size={16} color="#06b6d4" />
          Cloud Infrastructure
        </h3>
        <div style={{ background: 'var(--bg-darkest)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PROJECT ID</p>
          <p style={{ fontWeight: 600, color: 'var(--cyan)', wordBreak: 'break-all' }}>{gcpProject}</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>REGION / RUNTIME</p>
          <p style={{ fontWeight: 500, color: 'var(--text-main)', fontSize: '0.8rem' }}>Vertex AI Global • Agent Runtime</p>
        </div>
      </div>

      <div>
        <h3
          style={{
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            color: 'var(--text-dim)',
            letterSpacing: '1px',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Camera size={16} color="#f59e0b" />
          Runtime Optics Engine
        </h3>

        <div className="form-group">
          <label className="form-label">Aspect Ratio</label>
          <select
            className="form-control"
            value={opticsConfig.aspect_ratio}
            onChange={(e) =>
              setOpticsConfig((prev) => ({ ...prev, aspect_ratio: e.target.value }))
            }
          >
            <option value="2.39:1">2.39:1 (Anamorphic Cinema)</option>
            <option value="16:9">16:9 (Cinematic Widescreen)</option>
            <option value="4:3">4:3 (IMAX 70mm Standard)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Lens & Optics Preset</label>
          <select
            className="form-control"
            value={opticsConfig.optics_preset}
            onChange={(e) =>
              setOpticsConfig((prev) => ({ ...prev, optics_preset: e.target.value }))
            }
          >
            <option value="Panavision C-Series Anamorphic">Panavision C-Series Anamorphic</option>
            <option value="ARRI Master Prime T1.3">ARRI Master Prime T1.3</option>
            <option value="Cooke Anamorphic/i Full Frame">Cooke Anamorphic/i Full Frame</option>
            <option value="IMAX 70mm Dual-Camera Rig">IMAX 70mm Dual-Camera Rig</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Lighting Palette</label>
          <select
            className="form-control"
            value={opticsConfig.lighting_style}
            onChange={(e) =>
              setOpticsConfig((prev) => ({ ...prev, lighting_style: e.target.value }))
            }
          >
            <option value="Cyberpunk High-Contrast Neon">Cyberpunk High-Contrast Neon</option>
            <option value="Film Noir Low-Key Chiaroscuro">Film Noir Low-Key Chiaroscuro</option>
            <option value="Golden Hour Naturalistic">Golden Hour Naturalistic</option>
            <option value="Volumetric Dystopian Fog">Volumetric Dystopian Fog</option>
          </select>
        </div>
      </div>

      <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
        <h3
          style={{
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            color: 'var(--text-dim)',
            letterSpacing: '1px',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Sliders size={16} />
          Studio Governance
        </h3>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Google Model Armor</span>
          <input
            type="checkbox"
            checked={opticsConfig.model_armor_enabled}
            onChange={(e) =>
              setOpticsConfig((prev) => ({ ...prev, model_armor_enabled: e.target.checked }))
            }
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Cloud Operations Export</span>
          <input
            type="checkbox"
            checked={opticsConfig.telemetry_enabled}
            onChange={(e) =>
              setOpticsConfig((prev) => ({ ...prev, telemetry_enabled: e.target.checked }))
            }
          />
        </div>
      </div>
    </aside>
  );
};
