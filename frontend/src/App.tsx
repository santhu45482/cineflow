import React, { useState, useEffect } from 'react';
import {
  Clapperboard,
  FileText,
  Users,
  Film,
  Mic,
  Activity,
} from 'lucide-react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ShowrunnerTab } from './components/tabs/ShowrunnerTab';
import { ScreenplayTab } from './components/tabs/ScreenplayTab';
import { CastingTab } from './components/tabs/CastingTab';
import { StoryboardTab } from './components/tabs/StoryboardTab';
import { SoundstageTab } from './components/tabs/SoundstageTab';
import { OperationsTab } from './components/tabs/OperationsTab';
import type {
  ProductionOverviewResponse,
  RuntimeOpticsConfig,
} from './types/cineflow';
import { checkBackendHealth, getProductionOverview } from './services/api';

export const App: React.FC = () => {
  const [sessionId, setSessionId] = useState('cineflow-session-001');
  const [activeTab, setActiveTab] = useState<
    'showrunner' | 'screenplay' | 'casting' | 'storyboard' | 'soundstage' | 'operations'
  >('showrunner');

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

  return (
    <div className="app-container">
      <Sidebar
        opticsConfig={opticsConfig}
        setOpticsConfig={setOpticsConfig}
        gcpProject={gcpProject}
      />

      <div className="main-content">
        <Header
          sessionId={sessionId}
          setSessionId={setSessionId}
          backendHealth={backendHealth}
          gcpProject={gcpProject}
          activeGate={overview.active_gate}
        />

        {/* Studio Department Navigation Tabs */}
        <nav className="tabs-nav">
          <button
            className={`tab-btn ${activeTab === 'showrunner' ? 'active' : ''}`}
            onClick={() => setActiveTab('showrunner')}
          >
            <Clapperboard size={16} />
            Showrunner & Gates
          </button>

          <button
            className={`tab-btn ${activeTab === 'screenplay' ? 'active' : ''}`}
            onClick={() => setActiveTab('screenplay')}
          >
            <FileText size={16} />
            Screenplay & Beats
          </button>

          <button
            className={`tab-btn ${activeTab === 'casting' ? 'active' : ''}`}
            onClick={() => setActiveTab('casting')}
          >
            <Users size={16} />
            Casting & Seeds
          </button>

          <button
            className={`tab-btn ${activeTab === 'storyboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('storyboard')}
          >
            <Film size={16} />
            Storyboard & Visual QA
          </button>

          <button
            className={`tab-btn ${activeTab === 'soundstage' ? 'active' : ''}`}
            onClick={() => setActiveTab('soundstage')}
          >
            <Mic size={16} />
            Soundstage & Live Rehearsal
          </button>

          <button
            className={`tab-btn ${activeTab === 'operations' ? 'active' : ''}`}
            onClick={() => setActiveTab('operations')}
          >
            <Activity size={16} />
            Cloud Operations & SRE
          </button>
        </nav>

        {/* Tab Viewport */}
        {activeTab === 'showrunner' && (
          <ShowrunnerTab
            overview={overview}
            setOverview={setOverview}
            sessionId={sessionId}
            opticsConfig={opticsConfig}
          />
        )}
        {activeTab === 'screenplay' && <ScreenplayTab overview={overview} />}
        {activeTab === 'casting' && (
          <CastingTab overview={overview} setOverview={setOverview} />
        )}
        {activeTab === 'storyboard' && <StoryboardTab overview={overview} />}
        {activeTab === 'soundstage' && (
          <SoundstageTab overview={overview} sessionId={sessionId} />
        )}
        {activeTab === 'operations' && (
          <OperationsTab gcpProject={gcpProject} />
        )}
      </div>
    </div>
  );
};

export default App;
