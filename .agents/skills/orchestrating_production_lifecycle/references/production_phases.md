# Production Phase Transitions and Escalation Matrix

## Gate Definitions & Success Criteria

### Gate 1: Pre-Production (`GATE_1_PREPROD`)
- **Required State**:
  - Minimum 1 screenplay document parsed and embedded in RAG vector store.
  - All speaking characters registered with locked deterministic seed tokens.
  - Minimum 1 atomic shot unit registered in `ProductionBible.shots`.
- **Exit Action**: Director human approval or revision notes logged.

### Gate 2: Asset Production (`GATE_2_ASSETS`)
- **Required State**:
  - GCS storyboard frame URIs generated for all active shot units.
  - Multi-track dialogue audio stems synthesized.
  - Scene score audio stems generated.
  - QA Critic consistency verification score >= 0.85 on all frames.
- **Exit Action**: Director human approval or re-rendering pass requested.

### Gate 3: Final Assembly (`GATE_3_FINAL`)
- **Required State**:
  - FFmpeg stitch operation completed (`timeline_cut.mp4`).
  - Total duration matching sum of shot unit timings.
- **Exit Action**: Final sign-off.
