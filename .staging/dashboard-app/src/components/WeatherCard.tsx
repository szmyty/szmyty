import React from 'react';
import type { WeatherData } from '../types';
import { Card } from './Card';
import '../styles/WeatherCard.css';

interface WeatherCardProps {
  data: WeatherData | null;
  gradient?: string[];
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="🌦️ Weather" gradient={gradient}>
      <p className="no-data">Weather data not available</p>
    </Card>;
  }

  return (
    <Card title="🌦️ Weather" gradient={gradient}>
      <div className="weather-content">
        <div className="weather-location">
          <strong>{data.location}</strong>
        </div>
        
        <div className="weather-current">
          <div className="weather-emoji">{data.current.emoji}</div>
          <div className="weather-temp">{Math.round(data.current.temperature)}°C</div>
          <div className="weather-condition">{data.current.condition}</div>
        </div>

        <div className="weather-details">
          <div className="weather-detail">
            <span className="label">Wind Speed:</span>
            <span className="value">{data.current.wind_speed} km/h</span>
          </div>
          <div className="weather-detail">
            <span className="label">High/Low:</span>
            <span className="value">
              {Math.round(data.daily.temperature_max)}°C / {Math.round(data.daily.temperature_min)}°C
            </span>
          </div>
        </div>

        <div className="weather-sun">
          <div className="sun-time">
            <span>🌅 {new Date(data.daily.sunrise).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
          <div className="sun-time">
            <span>🌇 {new Date(data.daily.sunset).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
