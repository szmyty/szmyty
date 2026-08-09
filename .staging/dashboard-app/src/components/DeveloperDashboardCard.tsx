import React from 'react';
import type { DeveloperStats } from '../types';
import { Card } from './Card';
import '../styles/DeveloperDashboardCard.css';

interface DeveloperDashboardCardProps {
  data: DeveloperStats | null;
  gradient?: string[];
}

export const DeveloperDashboardCard: React.FC<DeveloperDashboardCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="💻 Developer Stats" gradient={gradient}>
      <p className="no-data">Developer data not available</p>
    </Card>;
  }

  const topLanguages = Object.entries(data.languages)
    .sort(([, a], [, b]) => b.percentage - a.percentage)
    .slice(0, 5);

  return (
    <Card title={`💻 Developer Stats - @${data.username}`} gradient={gradient}>
      <div className="developer-content">
        <div className="developer-stats">
          <div className="stat-item">
            <div className="stat-icon">📝</div>
            <div className="stat-info">
              <div className="stat-value">{data.total_commits.toLocaleString()}</div>
              <div className="stat-label">Commits</div>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">📦</div>
            <div className="stat-info">
              <div className="stat-value">{data.total_repos}</div>
              <div className="stat-label">Repositories</div>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">⭐</div>
            <div className="stat-info">
              <div className="stat-value">{data.total_stars}</div>
              <div className="stat-label">Stars</div>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">🔀</div>
            <div className="stat-info">
              <div className="stat-value">{data.total_pull_requests}</div>
              <div className="stat-label">Pull Requests</div>
            </div>
          </div>
        </div>

        <div className="commit-activity">
          <h3>Recent Activity</h3>
          <div className="activity-row">
            <span className="activity-label">Last 7 days:</span>
            <span className="activity-value">{data.commit_activity.total_7_days} commits</span>
          </div>
          <div className="activity-row">
            <span className="activity-label">Last 30 days:</span>
            <span className="activity-value">{data.commit_activity.total_30_days} commits</span>
          </div>
        </div>

        <div className="languages">
          <h3>Top Languages</h3>
          <div className="language-list">
            {topLanguages.map(([lang, stats]) => (
              <div key={lang} className="language-item">
                <span className="language-name">{lang}</span>
                <span className="language-percent">{stats.percentage.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};
