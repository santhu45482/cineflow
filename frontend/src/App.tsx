import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { GateRibbon } from './components/GateRibbon';
import { DirectorDeck } from './components/DirectorDeck';
import { OperationsTab } from './components/tabs/OperationsTab';
import { OpticsDrawer } from './components/OpticsDrawer';
import type {
  ProductionOverviewResponse,
  RuntimeOpticsConfig,
} from './types/cineflow';
import {
  checkBackendHealth,
  getProductionOverview,
  triggerProductionPipeline,
} from './services/api';
import './App.css';

export const App: React.FC = () => {
  const [sessionId, setSessionId] = useState('cineflow-session-001');
  const [activeMode, setActiveMode] = useState<'director' | 'operations'>('director');
  const [isOpticsOpen, setIsOpticsOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const [backendHealth, setBackendHealth] = useState({
    online: true,
    message: 'Connecting to CineFlow...',
  });
  const [gcpProject] = useState('cineflow-10');

  const [opticsConfig, setOpticsConfig] = useState<RuntimeOpticsConfig>({
    aspect_ratio: '2.39:1',
    optics_preset: 'Panavision C-Series Anamorphic',
    lighting_style: 'Cyberpunk High-Contrast Neon',
    model_armor_enabled: true,
    telemetry_enabled: true,
  });

  const [overview, setOverview] = useState<ProductionOverviewResponse>({
    status: 'success',
    title: 'Neon Syndicate: Sub-Level 9',
    logline: 'In Neo-Bangalore 2088, rogue cyber-detective Kade Mercer uncovers a synthetic memory smuggling cartel.',
    genre: 'Cyberpunk Noir / Sci-Fi Thriller',
    theme: 'Identity, synthetic obsolescence, and memory commodification in a rain-soaked dystopia.',
    character_count: 2,
    shot_count: 4,
    active_gate: 'GATE_1_PREPROD',
    characters: [
      {
        name: 'Kade Mercer',
        visual_anchor_token: '<kade_m_tok>',
        seed: 48921,
        voice_preset: 'en-US-Journey-D',
        description: 'Hard-boiled cybernetic investigator wearing a weathered carbon-fiber trench coat and neural optic implant.',
      },
      {
        name: 'Nyx Vane',
        visual_anchor_token: '<nyx_v_tok>',
        seed: 71204,
        voice_preset: 'en-US-Journey-F',
        description: 'Black-market neural broker with holographic silver-blue bob cut and luminescent fingertips.',
      },
    ],
    shots: [
      {
        shot_id: 'shot_1_01',
        scene_number: 1,
        shot_number: 1,
        visual_prompt: 'High-contrast wide anamorphic establishing shot of rain-drenched Neo-Bangalore skyline, neon reflections on wet asphalt.',
        aspect_ratio: '2.39:1',
        optics_preset: 'Panavision C-Series Anamorphic 40mm',
        character_seed: 48921,
        lighting_style: 'Cyberpunk High-Contrast Neon',
        duration_seconds: 4.5,
        qa_status: 'VERIFIED',
        qa_score: 0.96,
      },
      {
        shot_id: 'shot_1_02',
        scene_number: 1,
        shot_number: 2,
        visual_prompt: 'Close-up profile of Kade Mercer lighting a synthetic cigarette under flickering violet neon signage.',
        aspect_ratio: '2.39:1',
        optics_preset: 'Panavision C-Series Anamorphic 75mm',
        character_seed: 48921,
        lighting_style: 'Cyberpunk High-Contrast Neon',
        duration_seconds: 3.8,
        dialogue: 'Every memory in this city has a price tag. Even the ones you thought were yours.',
        character_name: 'Kade Mercer',
        qa_status: 'VERIFIED',
        qa_score: 0.94,
      },
      {
        shot_id: 'shot_1_03',
        scene_number: 1,
        shot_number: 3,
        visual_prompt: 'Over-the-shoulder medium shot of Nyx Vane turning slowly inside a vapor-filled back-alley tea stall.',
        aspect_ratio: '2.39:1',
        optics_preset: 'Panavision C-Series Anamorphic 50mm',
        character_seed: 71204,
        lighting_style: 'Cyberpunk High-Contrast Neon',
        duration_seconds: 5.0,
        dialogue: 'You are late, Mercer. The Syndicate already knows which neural shard we pulled.',
        character_name: 'Nyx Vane',
        qa_status: 'VERIFIED',
        qa_score: 0.98,
      },
      {
        shot_id: 'shot_1_04',
        scene_number: 1,
        shot_number: 4,
        visual_prompt: 'Low angle two-shot of Kade and Nyx as heavy rain falls through holographic advertisements above.',
        aspect_ratio: '2.39:1',
        optics_preset: 'Panavision C-Series Anamorphic 35mm',
        character_seed: 48921,
        lighting_style: 'Cyberpunk High-Contrast Neon',
        duration_seconds: 4.2,
        qa_status: 'VERIFIED',
        qa_score: 0.95,
      },
    ],
  });

  useEffect(() => {
    checkBackendHealth().then(setBackendHealth);
    getProductionOverview(sessionId).then((data) => {
      if (data && data.status === 'success') {
        setOverview(data);
      }
    });
  }, [sessionId]);

  const handleTriggerPipeline = async (premiseText: string) => {
    setIsRunning(true);
    try {
      const res = await triggerProductionPipeline({
        session_id: sessionId,
        premise: premiseText,
        genre: overview.genre,
        runtime_optics: opticsConfig,
      });
      setOverview((prev) => ({
        ...prev,
        active_gate: res.active_gate || 'GATE_1_PREPROD',
      }));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-darkest)' }}>
      {/* 1. Slim Top Navigation Bar with Mode Switcher */}
      <Header
        sessionId={sessionId}
        setSessionId={setSessionId}
        backendHealth={backendHealth}
        gcpProject={gcpProject}
        activeMode={activeMode}
        setActiveMode={setActiveMode}
        onOpenOpticsDrawer={() => setIsOpticsOpen(true)}
      />

      {/* 2. Persistent Universal Gate & Pipeline Ribbon */}
      <GateRibbon
        sessionId={sessionId}
        overview={overview}
        setOverview={setOverview}
        isRunning={isRunning}
        setIsRunning={setIsRunning}
        onQuickRun={() => handleTriggerPipeline(overview.logline)}
      />

      {/* 3. Main Operational Viewport */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeMode === 'director' ? (
          <DirectorDeck
            overview={overview}
            setOverview={setOverview}
            sessionId={sessionId}
            onTriggerPipeline={handleTriggerPipeline}
            isRunning={isRunning}
          />
        ) : (
          <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
            <OperationsTab gcpProject={gcpProject} />
          </div>
        )}
      </main>

      {/* 4. Slide-Over Optics & Governance Drawer */}
      <OpticsDrawer
        isOpen={isOpticsOpen}
        onClose={() => setIsOpticsOpen(false)}
        opticsConfig={opticsConfig}
        setOpticsConfig={setOpticsConfig}
        gcpProject={gcpProject}
      />
    </div>
  );
};

export default App;
