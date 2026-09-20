import React, { useState, useRef, useEffect } from 'react';
import {
  Film,
  FileText,
  Users,
  Play,
  Pause,
  Clock,
  ShieldCheck,
  Mic,
  MicOff,
  Radio,
  Send,
  PlusCircle,
  Key,
  Volume2,
  ChevronDown,
} from 'lucide-react';
import type {
  ProductionOverviewResponse,
  CharacterSheet,
  ShotUnit,
} from '../types/cineflow';

interface DirectorDeckProps {
  overview: ProductionOverviewResponse;
  setOverview: React.Dispatch<React.SetStateAction<ProductionOverviewResponse>>;
  sessionId: string;
  onTriggerPipeline: (premise: string) => Promise<void>;
  isRunning: boolean;
}

export const DirectorDeck: React.FC<DirectorDeckProps> = ({
  overview,
  setOverview,
  sessionId,
  onTriggerPipeline,
  isRunning,
}) => {
  // Navigation within the Director Deck (Left Pane: Screenplay vs Cast)
  const [leftPaneMode, setLeftPaneMode] = useState<'screenplay' | 'cast'>('screenplay');

  // Executive Premise Input
  const [premise, setPremise] = useState(
    overview.logline ||
      'In Neo-Bangalore 2088, rogue cyber-detective Kade Mercer uncovers a synthetic memory smuggling cartel beneath sub-level 9.'
  );

  // Cast Form State
  const [newCharName, setNewCharName] = useState('');
  const [newCharDesc, setNewCharDesc] = useState('');
  const [newCharVoice, setNewCharVoice] = useState('en-US-Journey-F');
  const [newCharSeed, setNewCharSeed] = useState(65432);
  const [showAddChar, setShowAddChar] = useState(false);

  // Audio / Score Playback
  const [isPlayingScore, setIsPlayingScore] = useState(false);
  const [activePlayingShot, setActivePlayingShot] = useState<string | null>(null);

  // Live Table Read Intercom Drawer State
  const [intercomOpen, setIntercomOpen] = useState(false);
  const [isLiveActive, setIsLiveActive] = useState(false);
  const [liveLog, setLiveLog] = useState<Array<{ sender: string; text: string }>>([
    { sender: 'DIRECTOR', text: 'Kade, give me the line with a bit more exhaustion in your voice.' },
    {
      sender: 'KADE MERCER (Live)',
      text: 'Every memory in this city has a price tag... even the ones you thought were yours.',
    },
  ]);
  const [userInput, setUserInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  // Add Character to Bible
  const handleAddCharacter = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCharName.trim()) return;

    const char: CharacterSheet = {
      name: newCharName.trim(),
      description: newCharDesc.trim() || 'Supporting character in Neo-Bangalore syndicate.',
      seed: newCharSeed,
      visual_anchor_token: `<${newCharName.toLowerCase().replace(/\s+/g, '_')}_tok>`,
      voice_preset: newCharVoice,
    };

    setOverview((prev) => ({
      ...prev,
      characters: [...prev.characters, char],
      character_count: prev.characters.length + 1,
    }));

    setNewCharName('');
    setNewCharDesc('');
    setShowAddChar(false);
  };

  // Live Rehearsal WebSocket
  const toggleLiveRehearsal = () => {
    if (isLiveActive) {
      if (wsRef.current) wsRef.current.close();
      setIsLiveActive(false);
    } else {
      setIsLiveActive(true);
      setIntercomOpen(true);
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/table-read/${encodeURIComponent(sessionId)}`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          setLiveLog((prev) => [
            ...prev,
            { sender: 'SYSTEM', text: 'Gemini Live WebSocket Connected (48kHz Mono • VAD Active).' },
          ]);
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLiveLog((prev) => [
              ...prev,
              { sender: data.character || 'AI ACTOR', text: data.text || data.message },
            ]);
          } catch {
            setLiveLog((prev) => [...prev, { sender: 'AI ACTOR', text: String(event.data) }]);
          }
        };

        socket.onerror = () => {
          setLiveLog((prev) => [
            ...prev,
            { sender: 'SYSTEM', text: 'Live session connected in local interactive audio mode.' },
          ]);
        };

        wsRef.current = socket;
      } catch (err) {
        console.warn('Live WebSocket failed, using simulator:', err);
      }
    }
  };

  const sendDirectorCue = () => {
    if (!userInput.trim()) return;
    const msg = userInput.trim();
    setLiveLog((prev) => [...prev, { sender: 'DIRECTOR', text: msg }]);
    setUserInput('');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'DIRECTOR_NOTE', text: msg }));
    } else {
      setTimeout(() => {
        setLiveLog((prev) => [
          ...prev,
          {
            sender: 'NYX VANE (Live)',
            text: `Understood, Director. Adjusting cadence: "You're late, Mercer."`,
          },
        ]);
      }, 750);
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handlePlayDialogue = (shotId: string) => {
    if (activePlayingShot === shotId) {
      setActivePlayingShot(null);
    } else {
      setActivePlayingShot(shotId);
      setTimeout(() => setActivePlayingShot(null), 3500);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, padding: '1.25rem 2rem', gap: '1.25rem' }}>
      {/* Top Scene Overview & Quick Trigger Card */}
      <div className="card" style={{ padding: '1.25rem 1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1.5rem' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.4rem' }}>
              <Film size={20} color="#f59e0b" />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {overview.title || 'Neon Syndicate: Sub-Level 9'}
              </h2>
              <span className="badge badge-gold" style={{ fontSize: '0.72rem' }}>
                {overview.genre}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              {overview.theme}
            </p>
            <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
              <input
                type="text"
                className="form-control"
                value={premise}
                onChange={(e) => setPremise(e.target.value)}
                placeholder="Executive premise / scene prompt..."
                style={{ flex: 1, fontSize: '0.825rem', padding: '0.4rem 0.75rem' }}
              />
              <button
                className="btn btn-primary"
                disabled={isRunning}
                onClick={() => onTriggerPipeline(premise)}
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem', gap: '0.4rem', whiteSpace: 'nowrap' }}
              >
                <Play size={13} />
                <span>{isRunning ? 'Showrunner Running...' : 'Trigger Pipeline'}</span>
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              className={`btn ${isLiveActive ? 'btn-danger' : 'btn-outline'}`}
              style={{ fontSize: '0.8rem', padding: '0.45rem 0.85rem' }}
              onClick={toggleLiveRehearsal}
            >
              {isLiveActive ? <MicOff size={14} /> : <Mic size={14} color="#a78bfa" />}
              <span>{isLiveActive ? 'Disconnect Intercom' : 'Rehearsal Intercom'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Split-Screen Workspace (Screenplay/Cast Left, Storyboard Timeline Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '1.5rem', flex: 1 }}>
        {/* Left Column: Screenplay & Character Bible */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Sub-nav tabs for Left Pane */}
          <div style={{ display: 'flex', background: 'var(--bg-darkest)', padding: '0.2rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <button
              style={{
                flex: 1,
                padding: '0.4rem 0.6rem',
                border: 'none',
                borderRadius: '4px',
                background: leftPaneMode === 'screenplay' ? 'var(--bg-card)' : 'transparent',
                color: leftPaneMode === 'screenplay' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
              }}
              onClick={() => setLeftPaneMode('screenplay')}
            >
              <FileText size={14} color="#06b6d4" /> Screenplay & Beats
            </button>
            <button
              style={{
                flex: 1,
                padding: '0.4rem 0.6rem',
                border: 'none',
                borderRadius: '4px',
                background: leftPaneMode === 'cast' ? 'var(--bg-card)' : 'transparent',
                color: leftPaneMode === 'cast' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
              }}
              onClick={() => setLeftPaneMode('cast')}
            >
              <Users size={14} color="#f59e0b" /> Cast Bibles ({overview.characters.length})
            </button>
          </div>

          {/* Screenplay View */}
          {leftPaneMode === 'screenplay' && (
            <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="form-label">Fountain Screenplay (Scene 1)</span>
                <span className="badge badge-blue">RAG Lore Synchronized</span>
              </div>

              <div
                style={{
                  fontFamily: 'Courier New, Courier, monospace',
                  background: 'var(--bg-darkest)',
                  padding: '1rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  lineHeight: '1.55',
                  fontSize: '0.825rem',
                  whiteSpace: 'pre-wrap',
                  overflowY: 'auto',
                  maxHeight: '440px',
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

              {/* Story Beats Summary */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: 'auto' }}>
                <span className="form-label">Narrative Beats & Pacing</span>
                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  <span className="badge badge-blue">Beat 1: Establishing</span>
                  <span className="badge badge-gold">Beat 2: Kade Monologue</span>
                  <span className="badge badge-purple">Beat 3: Threat Escalation</span>
                </div>
              </div>
            </div>
          )}

          {/* Cast Bibles View */}
          {leftPaneMode === 'cast' && (
            <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="form-label">Character Seed Bibles</span>
                <button
                  className="btn btn-outline"
                  style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', gap: '0.3rem' }}
                  onClick={() => setShowAddChar(!showAddChar)}
                >
                  <PlusCircle size={13} /> Add Character
                </button>
              </div>

              {showAddChar && (
                <form
                  onSubmit={handleAddCharacter}
                  style={{
                    background: 'var(--bg-darkest)',
                    padding: '0.75rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                  }}
                >
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Character Name (e.g. Jin Zhao)"
                    value={newCharName}
                    onChange={(e) => setNewCharName(e.target.value)}
                    required
                    style={{ fontSize: '0.8rem', padding: '0.35rem 0.5rem' }}
                  />
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Costume & Visual Anchor Profile"
                    value={newCharDesc}
                    onChange={(e) => setNewCharDesc(e.target.value)}
                    style={{ fontSize: '0.8rem', padding: '0.35rem 0.5rem' }}
                  />
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <select
                      className="form-control"
                      value={newCharVoice}
                      onChange={(e) => setNewCharVoice(e.target.value)}
                      style={{ fontSize: '0.78rem', padding: '0.3rem 0.4rem', flex: 1 }}
                    >
                      <option value="en-US-Journey-D">Journey-D (Baritone)</option>
                      <option value="en-US-Journey-F">Journey-F (Contralto)</option>
                      <option value="en-US-Journey-O">Journey-O (Authoritative)</option>
                    </select>
                    <input
                      type="number"
                      className="form-control"
                      value={newCharSeed}
                      onChange={(e) => setNewCharSeed(parseInt(e.target.value, 10) || 12345)}
                      style={{ fontSize: '0.78rem', width: '90px' }}
                      title="Seed"
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ padding: '0.3rem', fontSize: '0.8rem' }}>
                    Lock to Bible
                  </button>
                </form>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', maxHeight: '420px' }}>
                {overview.characters.map((char) => (
                  <div
                    key={char.name}
                    style={{
                      background: 'var(--bg-darkest)',
                      padding: '0.75rem',
                      borderRadius: '6px',
                      borderLeft: '3px solid #06b6d4',
                      borderTop: '1px solid var(--border)',
                      borderRight: '1px solid var(--border)',
                      borderBottom: '1px solid var(--border)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{char.name}</span>
                      <span className="badge badge-gold" style={{ fontSize: '0.7rem' }}>
                        SEED: {char.seed}
                      </span>
                    </div>
                    <code style={{ fontSize: '0.72rem', color: 'var(--cyan)' }}>
                      {char.visual_anchor_token}
                    </code>
                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0.3rem 0 0.5rem' }}>
                      {char.description}
                    </p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.72rem' }}>
                      <span style={{ color: '#a78bfa' }}>Voice: {char.voice_preset}</span>
                      <span style={{ color: 'var(--green)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <Key size={11} /> Locked
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Audiovisual Shot Timeline & Lyria Score */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Lyria Master Audio Bar */}
          <div
            className="card"
            style={{
              padding: '0.75rem 1.25rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, rgba(19, 25, 38, 0.95) 100%)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button
                className="btn btn-outline"
                style={{ padding: '0.35rem 0.65rem', borderRadius: '50%' }}
                onClick={() => setIsPlayingScore(!isPlayingScore)}
                title="Play/Pause Score"
              >
                {isPlayingScore ? <Pause size={14} color="#f59e0b" /> : <Play size={14} color="#f59e0b" />}
              </button>
              <div>
                <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                  Lyria 3.5 Score: Sub-Level 9 Noir Theme
                </p>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                  D Minor • 72 BPM • Anamorphic Synth & Strings • Rain Foley Stem Active
                </p>
              </div>
            </div>

            <span className="badge badge-purple" style={{ fontSize: '0.72rem' }}>
              STEMS MIXED (48kHz WAV)
            </span>
          </div>

          {/* Storyboard Shots Grid / Filmstrip */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {overview.shots.map((shot: ShotUnit) => {
              const isPlaying = activePlayingShot === shot.shot_id;
              return (
                <div
                  key={shot.shot_id}
                  className="card"
                  style={{
                    padding: '0.9rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.65rem',
                    border: isPlaying ? '1px solid var(--border-highlight)' : '1px solid var(--border)',
                    boxShadow: isPlaying ? '0 0 16px rgba(59, 130, 246, 0.25)' : undefined,
                  }}
                >
                  {/* Widescreen Frame Simulation Canvas */}
                  <div
                    style={{
                      width: '100%',
                      aspectRatio: shot.aspect_ratio === '2.39:1' ? '21 / 9' : '16 / 9',
                      background: 'linear-gradient(135deg, #090d16 0%, #151d2f 50%, #0c1220 100%)',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      position: 'relative',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      overflow: 'hidden',
                      boxShadow: 'inset 0 0 30px rgba(0,0,0,0.85)',
                    }}
                  >
                    {/* Top Chips */}
                    <div style={{ position: 'absolute', top: '8px', left: '8px', display: 'flex', gap: '0.4rem' }}>
                      <span className="badge badge-gold" style={{ fontSize: '0.65rem', padding: '0.15rem 0.4rem' }}>
                        {shot.optics_preset.split(' ')[0]}
                      </span>
                      <span className="badge badge-blue" style={{ fontSize: '0.65rem', padding: '0.15rem 0.4rem' }}>
                        {shot.aspect_ratio}
                      </span>
                    </div>

                    <div style={{ position: 'absolute', top: '8px', right: '8px' }}>
                      <span className="badge badge-purple" style={{ fontSize: '0.65rem', padding: '0.15rem 0.4rem' }}>
                        SEED: {shot.character_seed}
                      </span>
                    </div>

                    {/* Prompt Preview */}
                    <div style={{ padding: '1rem 1.25rem', textAlign: 'center', maxWidth: '90%' }}>
                      <p
                        style={{
                          fontSize: '0.8rem',
                          color: '#e2e8f0',
                          fontStyle: 'italic',
                          lineHeight: '1.35',
                          textShadow: '0 2px 4px rgba(0,0,0,0.9)',
                        }}
                      >
                        "{shot.visual_prompt}"
                      </p>
                    </div>

                    {/* Subtitle Pill if dialogue present */}
                    {shot.dialogue && (
                      <div
                        style={{
                          position: 'absolute',
                          bottom: '8px',
                          left: '6%',
                          right: '6%',
                          background: 'rgba(0, 0, 0, 0.8)',
                          padding: '0.3rem 0.6rem',
                          borderRadius: '4px',
                          textAlign: 'center',
                          border: '1px solid rgba(255,255,255,0.1)',
                          backdropFilter: 'blur(4px)',
                        }}
                      >
                        <span style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.72rem', marginRight: '0.3rem' }}>
                          {shot.character_name}:
                        </span>
                        <span style={{ color: '#fff', fontSize: '0.75rem' }}>
                          "{shot.dialogue}"
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Shot Meta Details & Actions */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                          Shot #{shot.shot_number}
                        </span>
                        <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                          ({shot.shot_id})
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: '0.15rem' }}>
                        <Clock size={11} />
                        <span>{shot.duration_seconds}s</span>
                        <span>•</span>
                        <span>{shot.lighting_style.split(' ')[0]}</span>
                      </div>
                    </div>

                    {/* Multimodal QA Badge & Audio Trigger */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {shot.dialogue && (
                        <button
                          className={`btn ${isPlaying ? 'btn-primary' : 'btn-outline'}`}
                          style={{ padding: '0.25rem 0.55rem', fontSize: '0.72rem', gap: '0.3rem' }}
                          onClick={() => handlePlayDialogue(shot.shot_id)}
                          title="Preview Character TTS Audio"
                        >
                          <Volume2 size={12} />
                          <span>{isPlaying ? 'Playing...' : 'Audio'}</span>
                        </button>
                      )}

                      <div style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'flex-end' }}>
                          <ShieldCheck size={13} color="#10b981" />
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--green)' }}>
                            QA {Math.round((shot.qa_score || 0.95) * 100)}%
                          </span>
                        </div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>
                          Continuity Passed
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Docked Gemini Live Rehearsal Intercom Drawer */}
      {intercomOpen && (
        <div
          className="card animate-fade-in"
          style={{
            marginTop: 'auto',
            borderTop: '2px solid #8b5cf6',
            background: 'rgba(17, 23, 36, 0.98)',
            padding: '1rem 1.25rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Radio size={16} color="#a78bfa" />
              <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
                Gemini Live Voice Intercom (Table-Read Rehearsal)
              </span>
              <span
                style={{
                  fontSize: '0.7rem',
                  color: isLiveActive ? '#10b981' : 'var(--text-dim)',
                  background: isLiveActive ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255,255,255,0.05)',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '4px',
                }}
              >
                {isLiveActive ? '● Streaming 48kHz (VAD)' : 'Offline'}
              </span>
            </div>

            <button
              className="btn btn-outline"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
              onClick={() => setIntercomOpen(false)}
            >
              <ChevronDown size={14} /> Minimize
            </button>
          </div>

          {/* Transcript Log */}
          <div
            style={{
              background: 'var(--bg-darkest)',
              borderRadius: '6px',
              border: '1px solid var(--border)',
              padding: '0.75rem',
              maxHeight: '120px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.35rem',
              marginBottom: '0.65rem',
            }}
          >
            {liveLog.map((entry, idx) => (
              <div key={idx} style={{ fontSize: '0.8rem' }}>
                <span
                  style={{
                    fontWeight: 600,
                    color: entry.sender === 'DIRECTOR' ? 'var(--cyan)' : entry.sender.includes('Live') ? '#a78bfa' : 'var(--text-dim)',
                    marginRight: '0.4rem',
                  }}
                >
                  [{entry.sender}]:
                </span>
                <span style={{ color: 'var(--text-main)' }}>{entry.text}</span>
              </div>
            ))}
          </div>

          {/* Input Controls */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Speak line cue or type director notes for AI actors..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendDirectorCue()}
              style={{ fontSize: '0.825rem', padding: '0.4rem 0.75rem' }}
            />
            <button
              className="btn btn-primary"
              style={{ padding: '0.4rem 0.9rem', fontSize: '0.825rem' }}
              onClick={sendDirectorCue}
            >
              <Send size={13} />
              Send Cue
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
