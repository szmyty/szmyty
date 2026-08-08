import React from 'react';
import type { OuraMetrics } from '../types';
import { Card } from './Card';
import '../styles/OuraHealthCard.css';

interface OuraHealthCardProps {
  data: OuraMetrics | null;
  gradient?: string[];
}

export const OuraHealthCard: React.FC<OuraHealthCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="💍 Oura Health" gradient={gradient}>
      <p className="no-data">Health data not available</p>
    </Card>;
  }

  const getScoreColor = (score: number | null) => {
    if (score === null) return 'var(--color-muted)';
    if (score >= 85) return 'var(--color-high)';
    if (score >= 70) return 'var(--color-medium)';
    return 'var(--color-low)';
  };

  return (
    <Card title="💍 Oura Health" gradient={gradient}>
      <div className="oura-content">
        <div className="oura-scores">
          <div className="score-item">
            <div className="score-label">😴 Sleep</div>
            <div 
              className="score-value" 
              style={{ color: getScoreColor(data.sleep_score) }}
            >
              {data.sleep_score ?? '-'}
            </div>
          </div>
          
          <div className="score-item">
            <div className="score-label">⚡ Readiness</div>
            <div 
              className="score-value"
              style={{ color: getScoreColor(data.readiness_score) }}
            >
              {data.readiness_score ?? '-'}
            </div>
          </div>
          
          <div className="score-item">
            <div className="score-label">🏃 Activity</div>
            <div 
              className="score-value"
              style={{ color: getScoreColor(data.activity_score) }}
            >
              {data.activity_score ?? '-'}
            </div>
          </div>
        </div>

        <div className="oura-vitals">
          <div className="vital-item">
            <span className="vital-label">❤️ Resting HR:</span>
            <span className="vital-value">{data.resting_hr ?? '-'} bpm</span>
          </div>
          
          {data.hrv !== null && (
            <div className="vital-item">
              <span className="vital-label">📊 HRV:</span>
              <span className="vital-value">{data.hrv} ms</span>
            </div>
          )}
          
          {data.readiness?.temperature_deviation !== null && data.readiness?.temperature_deviation !== undefined && (
            <div className="vital-item">
              <span className="vital-label">🌡️ Body Temp:</span>
              <span className="vital-value">
                {data.readiness.temperature_deviation > 0 ? '+' : ''}{data.readiness.temperature_deviation.toFixed(2)}°C
              </span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
