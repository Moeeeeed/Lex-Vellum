import React, { useState, useEffect, useRef } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend, Cell,
} from 'recharts';

// ─── Color helpers ─────────────────────────────────────────────────────────
function getScoreColor(score) {
  if (score >= 75) return 'var(--green)';
  if (score >= 45) return 'var(--yellow)';
  return 'var(--red)';
}
function getScoreBg(score) {
  if (score >= 75) return 'rgba(39,174,96,0.15)';
  if (score >= 45) return 'rgba(243,156,18,0.15)';
  return 'rgba(231,76,60,0.18)';
}

// ─── Custom Tooltip ─────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        {label && <div className="tooltip-label">{label}</div>}
        {payload.map((p, i) => (
          <div key={i} style={{ color: p.color || p.fill, fontSize: '0.72rem' }}>
            {p.name}: <strong>{p.value}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// ─── 1. Overall Score Ring ───────────────────────────────────────────────────
function OverallScoreRing({ score }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (score == null) return;
    setDisplay(0);
    let start = 0;
    const step = score / 40;
    const timer = setInterval(() => {
      start += step;
      if (start >= score) { setDisplay(score); clearInterval(timer); }
      else setDisplay(Math.round(start));
    }, 30);
    return () => clearInterval(timer);
  }, [score]);

  if (score == null) return null;

  const radius = 38;
  const circ = 2 * Math.PI * radius;
  const progress = (display / 100) * circ;

  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Overall Compliance Score</div>
      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8 }}>
        Aggregated compliance rating calculated across all jurisdictions and identified clauses.
      </p>
      <div className="score-ring-row">
        <svg width="96" height="96" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="var(--surface-raised)" strokeWidth="8" />
          <circle
            cx="48" cy="48" r={radius} fill="none"
            stroke={getScoreColor(display)} strokeWidth="8"
            strokeDasharray={`${progress} ${circ}`}
            strokeLinecap="round"
            transform="rotate(-90 48 48)"
            style={{ transition: 'stroke-dasharray 0.05s linear' }}
          />
          <text x="48" y="44" textAnchor="middle" fill={getScoreColor(display)} fontSize="18" fontWeight="700">{display}</text>
          <text x="48" y="58" textAnchor="middle" fill="var(--text-muted)" fontSize="9">/100</text>
        </svg>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.9rem', color: getScoreColor(score) }}>
            {score >= 75 ? 'Generally Compliant' : score >= 45 ? 'Needs Attention' : 'Critical Issues Found'}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
            {score >= 75 ? 'Minor adjustments may be needed.' : score >= 45 ? 'Several clauses require review.' : 'Immediate remediation required.'}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── 2. Compliance Heatmap (FR17) ────────────────────────────────────────────
const CATEGORIES = ['Data Privacy', 'User Rights', 'Liability', 'Transparency'];
const JURISDICTIONS = ['EU', 'USA', 'GDPR'];

function buildHeatmapData(clauses) {
  // Score per (jurisdiction × category) — we approximate by looking at clause jurisdictions + keywords
  const catKeywords = {
    'Data Privacy': ['data', 'personal', 'privacy', 'collect', 'process', 'store', 'share'],
    'User Rights': ['right', 'access', 'delete', 'portability', 'consent', 'opt'],
    'Liability': ['liab', 'damage', 'indemni', 'warrant', 'disclaim'],
    'Transparency': ['notif', 'inform', 'disclos', 'transparenc', 'communicat'],
  };

  const grid = {};
  JURISDICTIONS.forEach(j => {
    grid[j] = {};
    CATEGORIES.forEach(cat => { grid[j][cat] = { total: 0, count: 0 }; });
  });

  clauses.forEach(clause => {
    const jurisdictions = (clause.jurisdiction || []).map(j => j.toUpperCase());
    const text = (clause.original_text || '').toLowerCase();
    const score = clause.score ?? 50;

    CATEGORIES.forEach(cat => {
      const hits = catKeywords[cat].some(kw => text.includes(kw));
      if (hits) {
        jurisdictions.forEach(j => {
          if (grid[j]) {
            grid[j][cat].total += score;
            grid[j][cat].count += 1;
          }
        });
      }
    });
  });

  return grid;
}

function ComplianceHeatmap({ clauses, onRegionClick, activeRegion }) {
  const grid = buildHeatmapData(clauses);

  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Compliance Heatmap (FR17)</div>
      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8 }}>
        Visualizes category-specific weaknesses across different jurisdictions using color intensity.
      </p>
      <div className="heatmap-container">
        <div className="heatmap-grid" style={{ gridTemplateColumns: `72px repeat(${CATEGORIES.length}, 1fr)` }}>
          {/* Header row */}
          <div className="heatmap-header-cell" />
          {CATEGORIES.map(cat => (
            <div key={cat} className="heatmap-header-cell">{cat}</div>
          ))}
          {/* Data rows */}
          {JURISDICTIONS.map(j => (
            <React.Fragment key={j}>
              <div
                className={`heatmap-row-label ${activeRegion === j ? 'active' : ''}`}
                onClick={() => onRegionClick(j)}
              >
                {j === 'EU' ? '🇪🇺' : j === 'USA' ? '🇺🇸' : '🔒'} {j}
              </div>
              {CATEGORIES.map(cat => {
                const cell = grid[j]?.[cat];
                const avg = cell?.count > 0 ? Math.round(cell.total / cell.count) : null;
                const bg = avg != null ? getScoreBg(avg) : 'var(--surface-raised)';
                const color = avg != null ? getScoreColor(avg) : 'var(--text-muted)';
                return (
                  <div
                    key={cat}
                    className="heatmap-cell"
                    style={{ background: bg, color }}
                    title={avg != null ? `${j} × ${cat}: ${avg}/100` : 'No data'}
                    onClick={() => onRegionClick(j)}
                  >
                    {avg != null ? avg : '—'}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── 3. Stacked Violation Bar Chart (FR18 + FR19) ────────────────────────────
function buildStackedData(clauses) {
  const map = { EU: { violation: 0, warning: 0, compliant: 0 }, USA: { violation: 0, warning: 0, compliant: 0 }, GDPR: { violation: 0, warning: 0, compliant: 0 } };
  clauses.forEach(clause => {
    const jurisdictions = (clause.jurisdiction || []).map(j => j.toUpperCase());
    const status = clause.status || 'compliant';
    jurisdictions.forEach(j => {
      if (map[j] && status in map[j]) map[j][status]++;
    });
  });
  return JURISDICTIONS.map(j => ({ name: j, ...map[j] }));
}

function StackedViolationChart({ clauses, onRegionClick, activeRegion }) {
  const data = buildStackedData(clauses);

  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Violation Breakdown by Region (FR18)</div>
      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8 }}>
        Displays the volume and severity of legal conflicts for each checked country or region.
      </p>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data} margin={{ top: 4, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 10, fill: 'var(--text-secondary)' }}
            axisLine={false} tickLine={false}
          />
          <YAxis tick={{ fontSize: 9, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Legend iconSize={8} wrapperStyle={{ fontSize: '0.65rem', color: 'var(--text-muted)' }} />
          <Bar dataKey="violation" name="Violation" stackId="a" fill="var(--red)" radius={[0,0,0,0]}
            onClick={(d) => onRegionClick(d.name)} style={{ cursor: 'pointer' }} />
          <Bar dataKey="warning"   name="Warning"   stackId="a" fill="var(--yellow)"
            onClick={(d) => onRegionClick(d.name)} style={{ cursor: 'pointer' }} />
          <Bar dataKey="compliant" name="Compliant" stackId="a" fill="var(--green)" radius={[4,4,0,0]}
            onClick={(d) => onRegionClick(d.name)} style={{ cursor: 'pointer' }} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── 4. Audit Trend Line (FR20) ──────────────────────────────────────────────
function buildTrendData(history) {
  // history: array of { label, score } snapshots over time
  return history.map((h, i) => ({ step: h.label, score: h.score }));
}

function AuditTrendLine({ history }) {
  if (!history || history.length < 2) return null;
  const data = buildTrendData(history);

  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Audit Trend Line (FR20)</div>
      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8 }}>
        Tracks the document's progress toward full compliance as AI suggestions are applied.
      </p>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="step" tick={{ fontSize: 9, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
          <Line
            type="monotone" dataKey="score" name="Score"
            stroke="var(--green)" strokeWidth={2}
            dot={{ fill: 'var(--green)', r: 3, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: 'var(--green)' }}
            isAnimationActive={true}
            animationDuration={1200}
            animationEasing="ease-out"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── 5. Category Breakdown + Region Filter Chips (FR19 + FR22) ───────────────
function CategoryBreakdownRow({ categoryBreakdown }) {
  const total = (categoryBreakdown?.violation || 0) + (categoryBreakdown?.warning || 0) + (categoryBreakdown?.compliant || 0);
  if (!total) return null;

  const v = categoryBreakdown.violation || 0;
  const w = categoryBreakdown.warning   || 0;
  const c = categoryBreakdown.compliant || 0;

  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Clause Status Breakdown (FR19)</div>
      <p className="chart-description">Red/Yellow/Green color-coded counts across all evaluated clauses.</p>
      <div className="breakdown-bar-track">
        {v > 0 && <div className="breakdown-bar-seg violation" style={{ width: `${(v/total)*100}%` }} title={`${v} Violations`} />}
        {w > 0 && <div className="breakdown-bar-seg warning"   style={{ width: `${(w/total)*100}%` }} title={`${w} Warnings`} />}
        {c > 0 && <div className="breakdown-bar-seg compliant" style={{ width: `${(c/total)*100}%` }} title={`${c} Compliant`} />}
      </div>
      <div className="breakdown-legend">
        <span className="breakdown-chip violation">🔴 {v} Violation{v !== 1 ? 's' : ''}</span>
        <span className="breakdown-chip warning">🟡 {w} Warning{w !== 1 ? 's' : ''}</span>
        <span className="breakdown-chip compliant">🟢 {c} Compliant</span>
      </div>
    </div>
  );
}

function RegionFilterChips({ activeRegion, onRegionClick }) {
  const regions = ['ALL', 'EU', 'USA', 'GDPR'];
  return (
    <div className="analytics-card">
      <div className="analytics-section-label">Filter by Region (FR22)</div>
      <p className="chart-description">Click a region to show only clauses relevant to that jurisdiction.</p>
      <div className="region-filter-chips">
        {regions.map(r => (
          <button
            key={r}
            className={`region-chip ${activeRegion === r ? 'active' : ''}`}
            onClick={() => onRegionClick(r)}
          >
            {r === 'EU' ? '🇪🇺 EU' : r === 'USA' ? '🇺🇸 USA' : r === 'GDPR' ? '🔒 GDPR' : '🌐 ALL'}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Main Export ─────────────────────────────────────────────────────────────
export default function AnalyticsDashboard({
  overallScore,
  jurisdictionScores,
  categoryBreakdown,
  clauses,
  auditHistory,
  activeRegion,
  onRegionClick,
  isFullPage = false
}) {
  if (overallScore == null) return null;

  return (
    <div className={`analytics-dashboard ${isFullPage ? 'full-page-grid' : ''} fade-in`}>
      <OverallScoreRing score={overallScore} />
      <RegionFilterChips activeRegion={activeRegion} onRegionClick={onRegionClick} />
      <CategoryBreakdownRow categoryBreakdown={categoryBreakdown} />
      <StackedViolationChart clauses={clauses} onRegionClick={onRegionClick} activeRegion={activeRegion} />
      <ComplianceHeatmap clauses={clauses} onRegionClick={onRegionClick} activeRegion={activeRegion} />
      <AuditTrendLine history={auditHistory} />
    </div>
  );
}
