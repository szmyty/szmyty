import React from 'react';
import type { AIIdentity } from '../types';
import { Card } from './Card';
import '../styles/AIIdentityCard.css';

interface AIIdentityCardProps {
  data: AIIdentity | null;
  gradient?: string[];
}

export const AIIdentityCard: React.FC<AIIdentityCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="🤖 AI Identity" gradient={gradient}>
      <p className="no-data">Coming soon! AI-generated identity insights will be implemented.</p>
    </Card>;
  }

  return (
    <Card title="🤖 AI Identity" gradient={gradient}>
      <div className="ai-identity-content">
        <div className="persona">
          <h3>Persona</h3>
          <p>{data.persona}</p>
        </div>

        {data.traits && data.traits.length > 0 && (
          <div className="traits">
            <h3>Key Traits</h3>
            <div className="traits-list">
              {data.traits.map((trait, index) => (
                <span key={index} className="trait-tag">{trait}</span>
              ))}
            </div>
          </div>
        )}

        {data.insights && data.insights.length > 0 && (
          <div className="insights">
            <h3>Insights</h3>
            <ul>
              {data.insights.map((insight, index) => (
                <li key={index}>{insight}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="ai-timestamp">
          Updated: {new Date(data.updated_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })}
        </div>
      </div>
    </Card>
  );
};
