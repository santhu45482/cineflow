# Live Table Read Protocol (Gemini Live API)

## WebSocket Session Lifecycle
1. **Handshake**: Connect to `/ws/live-table-read` or call `start_script_rehearsal_session`.
2. **System Instruction**: Injects character backstory, tone, scene stakes, and improvisation guidelines.
3. **Turn-taking**: Full-duplex audio stream via PCM 16-bit 24kHz.
4. **Director Interruption**: Director voice interrupts agent speech in real time with zero buffering.
5. **Session Wrap**: Saves rehearsal transcripts and suggested line adjustments to `ProductionBible`.
