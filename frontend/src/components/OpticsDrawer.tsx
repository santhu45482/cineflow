import React, { useEffect } from 'react';
import { Camera, Sliders, Cloud, X, Check } from 'lucide-react';
import type { RuntimeOpticsConfig } from '../types/cineflow';

interface OpticsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  opticsConfig: RuntimeOpticsConfig;
  setOpticsConfig: React.Dispatch<React.SetStateAction<RuntimeOpticsConfig>>;
  gcpProject: string;
}

export const OpticsDrawer: React.FC<OpticsDrawerProps> = ({
  isOpen,
  onClose,
  opticsConfig,
  setOpticsConfig,
  gcpProject,
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Camera size={20} color="#f59e0b" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Studio Optics & Governance</h2>
          </div>
          <button
            className="btn btn-outline"
            style={{ padding: '0.3rem 0.5rem', borderRadius: '50%' }}
            onClick={onClose}
            title="Close Drawer"
          >
            <X size={16} />
          </button>
        </div>

        {/* Cloud Infrastructure Info */}
        <div>
          <h3
            style={{
              fontSize: '0.8rem',
              textTransform: 'uppercase',
              color: 'var(--text-dim)',
              letterSpacing: '1px',
              marginBottom: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Cloud size={15} color="#06b6d4" />
            Target Cloud Infrastructure
          </h3>
          <div style={{ background: 'var(--bg-darkest)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>PROJECT ID</p>
            <p style={{ fontWeight: 600, color: 'var(--cyan)', wordBreak: 'break-all', fontSize: '0.85rem' }}>
              {gcpProject}
            </p>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>RUNTIME ENVIRONMENT</p>
            <p style={{ fontWeight: 500, color: 'var(--text-main)', fontSize: '0.8rem' }}>
              Vertex AI Global • ADK 2.0 Agent Engine
            </p>
          </div>
        </div>

        {/* Runtime Optics Controls */}
        <div>
          <h3
            style={{
              fontSize: '0.8rem',
              textTransform: 'uppercase',
              color: 'var(--text-dim)',
              letterSpacing: '1px',
              marginBottom: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Camera size={15} color="#f59e0b" />
            Cinematic Optics Presets
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

        {/* Studio Governance & Policies */}
        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
          <h3
            style={{
              fontSize: '0.8rem',
              textTransform: 'uppercase',
              color: 'var(--text-dim)',
              letterSpacing: '1px',
              marginBottom: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Sliders size={15} />
            Studio Governance & Security
          </h3>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div>
              <p style={{ fontSize: '0.825rem', fontWeight: 500, color: 'var(--text-main)' }}>Google Model Armor</p>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Prompt sanitization & jailbreak shielding</p>
            </div>
            <input
              type="checkbox"
              style={{ width: '16px', height: '16px', accentColor: 'var(--cyan)' }}
              checked={opticsConfig.model_armor_enabled}
              onChange={(e) =>
                setOpticsConfig((prev) => ({ ...prev, model_armor_enabled: e.target.checked }))
              }
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontSize: '0.825rem', fontWeight: 500, color: 'var(--text-main)' }}>Google Cloud Telemetry Export</p>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Native Cloud Trace & Cloud Logging export</p>
            </div>
            <input
              type="checkbox"
              style={{ width: '16px', height: '16px', accentColor: 'var(--cyan)' }}
              checked={opticsConfig.telemetry_enabled}
              onChange={(e) =>
                setOpticsConfig((prev) => ({ ...prev, telemetry_enabled: e.target.checked }))
              }
            />
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              onClick={onClose}
            >
              <Check size={16} />
              Apply Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
