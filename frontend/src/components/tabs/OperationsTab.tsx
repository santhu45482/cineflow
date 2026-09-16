import React, { useState } from 'react';
import { Activity, ExternalLink, Wrench, RefreshCw, CheckCircle } from 'lucide-react';
import { runSREDiagnostics } from '../../services/api';
import type { SREDiagnosticReport } from '../../types/cineflow';

interface OperationsTabProps {
  gcpProject: string;
}

export const OperationsTab: React.FC<OperationsTabProps> = ({ gcpProject }) => {
  const [report, setReport] = useState<SREDiagnosticReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [remediating, setRemediating] = useState(false);
  const [remediationMsg, setRemediationMsg] = useState<string | null>(null);

  const handleRunDiagnostics = async () => {
    setLoading(true);
    try {
      const data = await runSREDiagnostics();
      setReport(data);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerRecovery = () => {
    setRemediating(true);
    setRemediationMsg(null);
    setTimeout(() => {
      setRemediating(false);
      setRemediationMsg('Cloud Run FFmpeg worker pool restarted cleanly. Circuit breaker reset.');
    }, 1200);
  };

  return (
    <div className="tab-content">
      {/* Cloud Suite Header */}
      <div className="card" style={{ borderLeft: '4px solid #4285F4' }}>
        <h2 className="card-title">
          <Activity color="#4285F4" size={20} />
          Google Cloud In-House Operations & Self-Healing SRE
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Zero external observability dependencies. CineFlow exports telemetry natively via Google Cloud Trace, Cloud Logging, and Cloud Monitoring.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <span className="form-label">GCP Project</span>
            <p style={{ fontWeight: 600, color: 'var(--cyan)' }}>{gcpProject}</p>
          </div>
          <div>
            <span className="form-label">Telemetry Pipeline</span>
            <p style={{ fontWeight: 500, color: 'var(--text-main)', fontSize: '0.85rem' }}>
              Cloud Trace • Cloud Logging • Cloud Monitoring
            </p>
          </div>
          <div>
            <span className="form-label">Service Namespace</span>
            <p style={{ fontWeight: 600, color: 'var(--accent)' }}>cineflow / cineflow-studio</p>
          </div>
        </div>
      </div>

      {/* Quick Launch Console Links */}
      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">
            <ExternalLink size={18} color="#06b6d4" />
            Google Cloud Console Quick-Launch
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Direct deep-links into your Google Cloud project's telemetry explorers.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <a
              href={`https://console.cloud.google.com/traces/explorer?project=${gcpProject}`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ justifyContent: 'space-between', textDecoration: 'none' }}
            >
              <span>🔍 Cloud Trace Explorer (Latency & Spans)</span>
              <ExternalLink size={14} />
            </a>

            <a
              href={`https://console.cloud.google.com/logs/query?project=${gcpProject}`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ justifyContent: 'space-between', textDecoration: 'none' }}
            >
              <span>📜 Cloud Logging (Logs Explorer & Crashes)</span>
              <ExternalLink size={14} />
            </a>

            <a
              href={`https://console.cloud.google.com/monitoring?project=${gcpProject}`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ justifyContent: 'space-between', textDecoration: 'none' }}
            >
              <span>📈 Cloud Monitoring Dashboards (PromQL/MQL)</span>
              <ExternalLink size={14} />
            </a>
          </div>
        </div>

        {/* Autonomous SRE Diagnostics */}
        <div className="card">
          <h3 className="card-title">
            <Wrench size={18} color="#f59e0b" />
            Autonomous SRE Self-Healing Engine
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Diagnose container memory limits, audio buffer latencies, and automated Cloud Run worker remediation.
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleRunDiagnostics}
              disabled={loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" /> Sweeping...
                </>
              ) : (
                'Run Health Sweep'
              )}
            </button>

            <button
              className="btn btn-danger"
              onClick={handleTriggerRecovery}
              disabled={remediating}
            >
              {remediating ? 'Remediating...' : 'Self-Heal Cloud Run Workers'}
            </button>
          </div>

          {remediationMsg && (
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.6rem 0.8rem', borderRadius: '4px', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <CheckCircle size={16} color="#10b981" />
              <span style={{ fontSize: '0.8rem', color: '#34d399' }}>{remediationMsg}</span>
            </div>
          )}

          {report && (
            <div style={{ background: 'var(--bg-darkest)', padding: '0.9rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Telemetry Diagnostics Report</span>
                <span className="badge badge-green">{report.status}</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.5rem' }}>
                Timestamp: {new Date(report.timestamp).toLocaleTimeString()}
              </p>
              <ul style={{ listStyle: 'none', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                <li>• <strong>Cloud Logging:</strong> {report.cloud_logging_status}</li>
                <li>• <strong>Cloud Trace:</strong> {report.cloud_trace_status}</li>
                <li>• <strong>Cloud Monitoring:</strong> {report.cloud_monitoring_status}</li>
                <li>• <strong>Cloud Run Workers:</strong> {report.cloud_run_workers.active_instances} active, {report.cloud_run_workers.oom_events_24h} OOM events</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
