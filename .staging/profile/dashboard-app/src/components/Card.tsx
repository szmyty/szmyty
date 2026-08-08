import React from 'react';
import '../styles/Card.css';

interface CardProps {
  title: string;
  gradient?: string[];
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, gradient, children, className }) => {
  const gradientStyle = gradient
    ? { background: `linear-gradient(135deg, ${gradient[0]}, ${gradient[1]})` }
    : {};

  return (
    <div className={`card ${className || ''}`} style={gradientStyle}>
      <h2 className="card-title">{title}</h2>
      <div className="card-content">{children}</div>
    </div>
  );
};
