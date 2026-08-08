import React from 'react';
import type { Achievement } from '../types';
import { Card } from './Card';
import '../styles/AchievementsCard.css';

interface AchievementsCardProps {
  data: Achievement[] | null;
  gradient?: string[];
}

export const AchievementsCard: React.FC<AchievementsCardProps> = ({ data, gradient }) => {
  if (!data || data.length === 0) {
    return <Card title="🏆 Achievements" gradient={gradient}>
      <p className="no-data">Coming soon! Achievement tracking will be implemented.</p>
    </Card>;
  }

  const unlockedCount = data.filter(a => a.unlocked).length;

  return (
    <Card title="🏆 Achievements" gradient={gradient}>
      <div className="achievements-content">
        <div className="achievements-header">
          <span className="achievements-count">{unlockedCount} / {data.length}</span>
          <span className="achievements-label">Unlocked</span>
        </div>

        <div className="achievements-list">
          {data.map(achievement => (
            <div 
              key={achievement.id} 
              className={`achievement-item ${achievement.unlocked ? 'unlocked' : 'locked'}`}
            >
              <div className="achievement-icon">{achievement.icon}</div>
              <div className="achievement-info">
                <div className="achievement-title">{achievement.title}</div>
                <div className="achievement-description">{achievement.description}</div>
                {achievement.unlocked && achievement.unlocked_at && (
                  <div className="achievement-date">
                    Unlocked: {new Date(achievement.unlocked_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};
