// Utility functions for fetching all dashboard data
import {
  fetchDeveloperStats,
  fetchWeather,
  fetchLocation,
  fetchOura,
  fetchMood,
  fetchSoundCloud,
  fetchAchievements,
  fetchAIIdentity,
  fetchTheme,
} from './fetchData';

/**
 * Fetch all dashboard data in parallel
 * Uses Axios for all HTTP requests with comprehensive error handling
 */
export async function fetchAllData() {
  const [
    weather,
    oura,
    mood,
    developer,
    location,
    soundcloud,
    theme,
    achievements,
    aiIdentity
  ] = await Promise.all([
    fetchWeather(),
    fetchOura(),
    fetchMood(),
    fetchDeveloperStats(),
    fetchLocation(),
    fetchSoundCloud(),
    fetchTheme(),
    fetchAchievements(),
    fetchAIIdentity(),
  ]);

  return {
    weather,
    oura,
    mood,
    developer,
    location,
    soundcloud,
    theme,
    achievements,
    aiIdentity,
  };
}
