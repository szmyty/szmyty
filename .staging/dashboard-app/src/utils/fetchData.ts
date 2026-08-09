// Individual data fetching utilities using Axios
import axios from 'axios';
import type {
  WeatherData,
  OuraMetrics,
  MoodData,
  DeveloperStats,
  LocationData,
  SoundCloudTrack,
  ThemeConfig,
  Achievement,
  AIIdentity,
} from '../types';

const BASE_PATH = import.meta.env.BASE_URL;

/**
 * Constructs a full URL from a relative path
 */
function buildURL(path: string): string {
  // Remove leading slash from path if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  // Ensure BASE_PATH ends with / before concatenating
  const basePath = BASE_PATH.endsWith('/') ? BASE_PATH : `${BASE_PATH}/`;
  return `${basePath}${cleanPath}`;
}

/**
 * Generic fetch function with comprehensive error handling
 */
async function fetchJSON<T>(path: string): Promise<T | null> {
  try {
    const url = buildURL(path);
    
    const response = await axios.get<T>(url, {
      timeout: 10000, // 10 second timeout
      validateStatus: (status) => status === 200, // Only accept 200 as success
    });

    // Check if response data is empty (but allow empty arrays as valid)
    if (!response.data || (typeof response.data === 'object' && !Array.isArray(response.data) && Object.keys(response.data).length === 0)) {
      console.warn(`Empty data received from ${url}`);
      return null;
    }

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        console.warn(`Failed to fetch ${path}: ${error.response.status} ${error.response.statusText}`);
        
        if (error.response.status === 404) {
          console.warn(`File not found: ${path}`);
        } else if (error.response.status === 403) {
          console.warn(`Access forbidden: ${path}`);
        }
      } else if (error.request) {
        // Request was made but no response received
        console.error(`No response received for ${path}:`, error.message);
      } else {
        // Error in setting up the request
        console.error(`Error setting up request for ${path}:`, error.message);
      }
    } else if (error instanceof SyntaxError) {
      // JSON parsing error
      console.error(`Invalid JSON in ${path}:`, error);
    } else {
      console.error(`Unexpected error fetching ${path}:`, error);
    }
    
    return null;
  }
}

/**
 * Fetch developer statistics
 */
export async function fetchDeveloperStats(): Promise<DeveloperStats | null> {
  return fetchJSON<DeveloperStats>('developer/stats.json');
}

/**
 * Fetch weather data
 */
export async function fetchWeather(): Promise<WeatherData | null> {
  return fetchJSON<WeatherData>('weather/weather.json');
}

/**
 * Fetch location data
 */
export async function fetchLocation(): Promise<LocationData | null> {
  return fetchJSON<LocationData>('location/location.json');
}

/**
 * Fetch Oura health metrics
 */
export async function fetchOura(): Promise<OuraMetrics | null> {
  return fetchJSON<OuraMetrics>('oura/metrics.json');
}

/**
 * Fetch mood data
 */
export async function fetchMood(): Promise<MoodData | null> {
  return fetchJSON<MoodData>('oura/mood.json');
}

/**
 * Fetch SoundCloud latest track
 */
export async function fetchSoundCloud(): Promise<SoundCloudTrack | null> {
  return fetchJSON<SoundCloudTrack>('soundcloud/latest.json');
}

/**
 * Fetch achievements
 */
export async function fetchAchievements(): Promise<Achievement[] | null> {
  return fetchJSON<Achievement[]>('achievements/achievements.json');
}

/**
 * Fetch AI identity data
 */
export async function fetchAIIdentity(): Promise<AIIdentity | null> {
  return fetchJSON<AIIdentity>('ai/identity.json');
}

/**
 * Fetch theme configuration
 */
export async function fetchTheme(): Promise<ThemeConfig | null> {
  return fetchJSON<ThemeConfig>('config/theme.json');
}
