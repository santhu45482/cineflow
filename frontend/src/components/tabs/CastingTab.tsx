import React, { useState } from 'react';
import { Users, Key, Mic, PlusCircle, Check } from 'lucide-react';
import type { CharacterSheet, ProductionOverviewResponse } from '../../types/cineflow';

interface CastingTabProps {
  overview: ProductionOverviewResponse;
  setOverview: React.Dispatch<React.SetStateAction<ProductionOverviewResponse>>;
}

export const CastingTab: React.FC<CastingTabProps> = ({ overview, setOverview }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [voicePreset, setVoicePreset] = useState('en-US-Journey-F');
  const [seed, setSeed] = useState(65432);
  const [added, setAdded] = useState(false);

  const handleAddCharacter = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const newChar: CharacterSheet = {
      name: name.trim(),
      description: description.trim() || 'Supporting character in Neo-Bangalore syndicate.',
      seed,
      visual_anchor_token: `<${name.toLowerCase().replace(/\s+/g, '_')}_tok>`,
      voice_preset: voicePreset,
    };

    setOverview((prev) => ({
      ...prev,
      characters: [...prev.characters, newChar],
      character_count: prev.characters.length + 1,
    }));

    setName('');
    setDescription('');
    setAdded(true);
    setTimeout(() => setAdded(false), 2500);
  };

  return (
    <div className="tab-content">
      <div className="card">
        <h2 className="card-title">
          <Users color="#f59e0b" size={20} />
          Casting Bible & Deterministic Character Seed Locking
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          To guarantee zero visual drift across consecutive shots, each character is bound to a persistent pseudo-random visual seed and specialized visual anchor token injected into Gemini 3.1 Flash Image prompts.
        </p>
      </div>

      {/* Characters List */}
      <div className="grid-2">
        {overview.characters.map((char) => (
          <div
            key={char.name}
            className="card"
            style={{ borderLeft: '3px solid #06b6d4' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{char.name}</h3>
                <code style={{ fontSize: '0.75rem', color: 'var(--cyan)' }}>{char.visual_anchor_token}</code>
              </div>
              <span className="badge badge-gold">SEED: {char.seed}</span>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', marginBottom: '1rem' }}>
              {char.description}
            </p>

            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Mic size={14} color="#8b5cf6" />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Voice Preset:</span>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#a78bfa' }}>{char.voice_preset}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Key size={14} color="#10b981" />
                <span style={{ fontSize: '0.75rem', color: 'var(--green)' }}>Identity Locked</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add New Character Form */}
      <div className="card" style={{ marginTop: '0.5rem' }}>
        <h3 className="card-title">
          <PlusCircle size={18} color="#10b981" />
          Register New Character to Production Bible
        </h3>

        <form onSubmit={handleAddCharacter} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Character Name</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Inspector Jin Zhao"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Voice Preset (Cloud TTS)</label>
            <select
              className="form-control"
              value={voicePreset}
              onChange={(e) => setVoicePreset(e.target.value)}
            >
              <option value="en-US-Journey-D">en-US-Journey-D (Deep Baritone)</option>
              <option value="en-US-Journey-F">en-US-Journey-F (Sharp Contralto)</option>
              <option value="en-US-Journey-O">en-US-Journey-O (Authoritative Mid)</option>
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Deterministic Visual Seed</label>
            <input
              type="number"
              className="form-control"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value, 10) || 12345)}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0, gridColumn: 'span 2' }}>
            <label className="form-label">Visual & Costume Profile</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Enforcer wearing matte black body armor with scarred visor"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ height: '38px' }}>
            {added ? (
              <>
                <Check size={16} /> Locked to Bible
              </>
            ) : (
              'Lock Character Seed'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
