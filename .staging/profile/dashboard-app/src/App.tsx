import { useState, useEffect } from 'react'
import './App.css'
import { fetchAllData } from './utils/dataFetcher'
import { WeatherCard } from './components/WeatherCard'
import { OuraHealthCard } from './components/OuraHealthCard'
import { DeveloperDashboardCard } from './components/DeveloperDashboardCard'
import { LocationCard } from './components/LocationCard'
import { SoundCloudCard } from './components/SoundCloudCard'
import { MoodAvatarCard } from './components/MoodAvatarCard'
import { AchievementsCard } from './components/AchievementsCard'
import { AIIdentityCard } from './components/AIIdentityCard'
import type {
  WeatherData,
  OuraMetrics,
  MoodData,
  DeveloperStats,
  LocationData,
  SoundCloudTrack,
  ThemeConfig,
  Achievement,
  AIIdentity
} from './types'

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState<{
    weather: WeatherData | null;
    oura: OuraMetrics | null;
    mood: MoodData | null;
    developer: DeveloperStats | null;
    location: LocationData | null;
    soundcloud: SoundCloudTrack | null;
    theme: ThemeConfig | null;
    achievements: Achievement[] | null;
    aiIdentity: AIIdentity | null;
  }>({
    weather: null,
    oura: null,
    mood: null,
    developer: null,
    location: null,
    soundcloud: null,
    theme: null,
    achievements: null,
    aiIdentity: null,
  })

  useEffect(() => {
    const loadData = async () => {
      const result = await fetchAllData()
      setData(result)
      setIsLoading(false)
    }

    loadData()
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light')
  }, [isDarkMode])

  const theme = data.theme?.themes[isDarkMode ? 'dark' : 'light']

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎯 Personal Dashboard</h1>
          <button 
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
            aria-label="Toggle theme"
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {isLoading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading dashboard data...</p>
          </div>
        ) : (
          <div className="dashboard-grid">
            <DeveloperDashboardCard 
              data={data.developer} 
              gradient={theme?.gradients.developer}
            />
            <WeatherCard 
              data={data.weather} 
              gradient={theme?.gradients.weather.clear_day}
            />
            <LocationCard 
              data={data.location} 
              gradient={theme?.gradients.background.default}
            />
            <OuraHealthCard 
              data={data.oura} 
              gradient={theme?.gradients.readiness}
            />
            <MoodAvatarCard 
              data={data.mood} 
              gradient={theme?.gradients.sleep}
            />
            <SoundCloudCard 
              data={data.soundcloud} 
              gradient={theme?.gradients.activity}
            />
            <AchievementsCard 
              data={data.achievements} 
              gradient={theme?.gradients.heart_rate}
            />
            <AIIdentityCard 
              data={data.aiIdentity} 
              gradient={theme?.gradients.developer}
            />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          🚀 Powered by React + Vite • Auto-updated via GitHub Actions • 
          <a 
            href="https://github.com/szmyty/profile" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            View Source
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
