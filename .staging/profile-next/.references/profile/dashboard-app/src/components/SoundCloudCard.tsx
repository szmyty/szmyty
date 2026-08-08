import React from 'react';
import type { SoundCloudTrack } from '../types';
import { Card } from './Card';
import '../styles/SoundCloudCard.css';

interface SoundCloudCardProps {
  data: SoundCloudTrack | null;
  gradient?: string[];
}

export const SoundCloudCard: React.FC<SoundCloudCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="🎵 SoundCloud" gradient={gradient}>
      <p className="no-data">SoundCloud data not available</p>
    </Card>;
  }

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card title="🎵 Latest SoundCloud Release" gradient={gradient}>
      <div className="soundcloud-content">
        {data.artwork_url && (
          <div className="soundcloud-artwork">
            <img src={data.artwork_url} alt={data.title} />
          </div>
        )}
        
        <div className="soundcloud-info">
          <h3 className="track-title">{data.title}</h3>
          <div className="track-meta">
            <span>⏱️ {formatDuration(data.duration)}</span>
            <span>📅 {formatDate(data.created_at)}</span>
          </div>
        </div>

        <div className="soundcloud-stats">
          <div className="stat">
            <span className="stat-icon">▶️</span>
            <span className="stat-value">{data.playback_count.toLocaleString()}</span>
            <span className="stat-label">Plays</span>
          </div>
          <div className="stat">
            <span className="stat-icon">❤️</span>
            <span className="stat-value">{data.likes_count.toLocaleString()}</span>
            <span className="stat-label">Likes</span>
          </div>
          <div className="stat">
            <span className="stat-icon">💬</span>
            <span className="stat-value">{data.comment_count.toLocaleString()}</span>
            <span className="stat-label">Comments</span>
          </div>
        </div>

        <a 
          href={data.permalink_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="soundcloud-link"
        >
          Listen on SoundCloud →
        </a>
      </div>
    </Card>
  );
};
