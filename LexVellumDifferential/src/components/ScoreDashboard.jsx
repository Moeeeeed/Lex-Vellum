import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

function getScoreColor(score) {
  if (score >= 75) return 'var(--green)';
  if (score >= 45) return 'var(--yellow)';
  return 'var(--red)';
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'var(--surface-raised)',
        border: '1px solid var(--border)',
        borderRadius: 6,
        padding: '6px 10px',
        fontSize: '0.72rem',
        color: 'var(--text-primary)',
      }}>
        {payload[0].payload.label}: <strong>{payload[0].value}/100</strong>
      </div>
    );
  }
  return null;
};

export default function ScoreDashboard({ overallScore, jurisdictionScores, categoryBreakdown }) {
  if (overallScore == null) return null;

  const barData = Object.entries(jurisdictionScores || {}).map(([key, val]) => ({
    label: key,
    score: val,
  }));

  const totalClauses =
    (categoryBreakdown?.violation || 0) +
    (categoryBreakdown?.warning   || 0) +
    (categoryBreakdown?.compliant || 0);

  return (
    <div className="score-dashboard">
      <div className="dashboard-title">Compliance Dashboard</div>

      {/* Overall score */}
      <div className="overall-score-ring">
        <div>
          <div className="ring-number" style={{ color: getScoreColor(overallScore) }}>
            {overallScore}
          </div>
          <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            / 100
          </div>
        </div>
        <div>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Overall Score
          </div>
          <div className="ring-label">
            {overallScore >= 75
              ? 'Generally compliant'
              : overallScore >= 45
              ? 'Needs attention'
              : 'Critical issues found'}
          </div>
        </div>
      </div>

      {/* Jurisdiction bar chart */}
      {barData.length > 0 && (
        <>
          <div className="panel-section-label" style={{ marginBottom: 8 }}>
            Jurisdiction Scores
          </div>
          <ResponsiveContainer width="100%" height={barData.length * 38 + 10}>
            <BarChart
              data={barData}
              layout="vertical"
              margin={{ top: 0, right: 30, left: 0, bottom: 0 }}
            >
              <XAxis
                type="number"
                domain={[0, 100]}
                tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                tick={{ fontSize: 11, fill: 'var(--text-secondary)' }}
                axisLine={false}
                tickLine={false}
                width={40}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={10}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={getScoreColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </>
      )}

      {/* Category breakdown chips */}
      {totalClauses > 0 && (
        <div className="breakdown-chips">
          {categoryBreakdown?.violation > 0 && (
            <span className="breakdown-chip violation">
              🔴 {categoryBreakdown.violation} Violation{categoryBreakdown.violation !== 1 ? 's' : ''}
            </span>
          )}
          {categoryBreakdown?.warning > 0 && (
            <span className="breakdown-chip warning">
              🟡 {categoryBreakdown.warning} Warning{categoryBreakdown.warning !== 1 ? 's' : ''}
            </span>
          )}
          {categoryBreakdown?.compliant > 0 && (
            <span className="breakdown-chip compliant">
              🟢 {categoryBreakdown.compliant} Compliant
            </span>
          )}
        </div>
      )}
    </div>
  );
}
