import React from 'react';
import type { LocationData } from '../types';
import { Card } from './Card';
import '../styles/LocationCard.css';

interface LocationCardProps {
  data: LocationData | null;
  gradient?: string[];
}

export const LocationCard: React.FC<LocationCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="📍 Location" gradient={gradient}>
      <p className="no-data">Location data not available</p>
    </Card>;
  }

  return (
    <Card title="📍 Location" gradient={gradient}>
      <div className="location-content">
        <div className="location-name">
          <strong>{data.display_name}</strong>
        </div>
        
        <div className="location-coords">
          <div className="coord-item">
            <span className="coord-label">Latitude:</span>
            <span className="coord-value">{data.lat.toFixed(4)}°</span>
          </div>
          <div className="coord-item">
            <span className="coord-label">Longitude:</span>
            <span className="coord-value">{data.lon.toFixed(4)}°</span>
          </div>
        </div>

        {data.address && (
          <div className="location-address">
            {data.address.city && <div>🏙️ {data.address.city}</div>}
            {data.address.state && <div>🗺️ {data.address.state}</div>}
            {data.address.country && <div>🌍 {data.address.country}</div>}
          </div>
        )}
      </div>
    </Card>
  );
};
