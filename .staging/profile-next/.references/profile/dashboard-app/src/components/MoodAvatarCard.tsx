import React from 'react';
import type { MoodData } from '../types';
import { Card } from './Card';
import '../styles/MoodAvatarCard.css';

interface MoodAvatarCardProps {
  data: MoodData | null;
  gradient?: string[];
}

export const MoodAvatarCard: React.FC<MoodAvatarCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="😊 Mood" gradient={gradient}>
      <p className="no-data">Mood data not available</p>
    </Card>;
  }

  // Handle both data structures
  const emoji = data.emoji || data.mood_icon || '😊';
  const description = data.description || data.mood_description || data.mood_name || 'Unknown';
  const score = data.score || data.mood_score || 0;
  const timestamp = data.timestamp || data.computed_at || new Date().toISOString();

  const getMoodColor = (score: number) => {
    if (score >= 80) return 'var(--color-high)';
    if (score >= 50) return 'var(--color-medium)';
    return 'var(--color-low)';
  };

  return (
    <Card title="😊 Current Mood" gradient={gradient}>
      <div className="mood-content">
        <div className="mood-emoji">{emoji}</div>
        
        <div className="mood-description">{description}</div>
        
        <div className="mood-score">
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${score}%`,
                backgroundColor: getMoodColor(score)
              }}
            />
          </div>
          <div className="score-text" style={{ color: getMoodColor(score) }}>
            {score.toFixed(0)}/100
          </div>
        </div>

        <div className="mood-timestamp">
          Updated: {new Date(timestamp).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </Card>
  );
};
