export interface CharacterSheet {
  name: string;
  visual_anchor_token: string;
  seed: number;
  voice_preset: string;
  description: string;
  costume_notes?: string;
  palette_prompt?: string;
}

export interface ShotUnit {
  shot_id: string;
  scene_number: number;
  shot_number: number;
  visual_prompt: string;
  aspect_ratio: string;
  optics_preset: string;
  character_seed: number;
  lighting_style: string;
  duration_seconds: number;
  dialogue?: string;
  character_name?: string;
  qa_status?: string;
  qa_score?: number;
  image_url?: string;
  audio_url?: string;
}

export interface MovieProductionBible {
  title: string;
  logline: string;
  genre: string;
  theme: string;
  characters: Record<string, CharacterSheet>;
  shots: ShotUnit[];
  scenes?: any[];
  score_stems?: Record<string, string>;
  active_gate?: string;
  session_id?: string;
}

export interface ProductionOverviewResponse {
  status: string;
  title: string;
  logline: string;
  genre: string;
  theme: string;
  character_count: number;
  shot_count: number;
  characters: CharacterSheet[];
  shots: ShotUnit[];
  active_gate: string;
  pipeline_history?: Array<{
    timestamp: string;
    stage: string;
    status: string;
    notes?: string;
  }>;
}

export interface RuntimeOpticsConfig {
  aspect_ratio: string;
  optics_preset: string;
  lighting_style: string;
  model_armor_enabled: boolean;
  telemetry_enabled: boolean;
}

export interface SREDiagnosticReport {
  status: string;
  timestamp: string;
  cloud_suite: string;
  cloud_logging_status: string;
  cloud_trace_status: string;
  cloud_monitoring_status: string;
  cloud_run_workers: {
    status: string;
    active_instances: number;
    oom_events_24h: number;
    p99_latency_ms: number;
  };
}
