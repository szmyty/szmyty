// Type definitions for dashboard data

export interface WeatherData {
  location: string;
  display_name: string;
  coordinates: {
    lat: number;
    lon: number;
  };
  current: {
    temperature: number;
    wind_speed: number;
    weathercode: number;
    is_day: number;
    condition: string;
    emoji: string;
  };
  daily: {
    temperature_max: number;
    temperature_min: number;
    sunrise: string;
    sunset: string;
    weathercode: number;
  };
  timezone: string;
  updated_at: string;
}

export interface OuraMetrics {
  sleep_score: number | null;
  readiness_score: number | null;
  activity_score: number | null;
  hrv: number | null;
  resting_hr: number | null;
  temp_deviation: number | null;
  personal_info?: {
    id: string;
    age: number;
    weight: number;
    height: number;
    biological_sex: string;
    email: string;
  };
  sleep?: {
    id: string;
    contributors: {
      deep_sleep: number;
      efficiency: number;
      latency: number;
      rem_sleep: number;
      restfulness: number;
      timing: number;
      total_sleep: number;
    };
    day: string;
    score: number;
    timestamp: string;
  };
  readiness?: {
    id: string;
    contributors: {
      activity_balance: number;
      body_temperature: number;
      hrv_balance: number | null;
      previous_day_activity: number;
      previous_night: number;
      recovery_index: number;
      resting_heart_rate: number;
      sleep_balance: number | null;
      sleep_regularity: number | null;
    };
    day: string;
    score: number;
    temperature_deviation: number;
    temperature_trend_deviation: number | null;
    timestamp: string;
  };
  activity?: {
    id: string;
    contributors: {
      active_calories: number;
      meet_daily_targets: number;
      move_every_hour: number;
      recovery_time: number;
      stay_active: number;
      training_frequency: number;
      training_volume: number;
    };
    day: string;
    score: number;
    timestamp: string;
  };
}

export interface MoodData {
  emoji?: string;
  description?: string;
  score?: number;
  timestamp?: string;
  // Alternative structure from oura/mood.json
  mood_name?: string;
  mood_score?: number;
  mood_icon?: string;
  mood_description?: string;
  computed_at?: string;
}

export interface DeveloperStats {
  username: string;
  total_commits: number;
  total_repos: number;
  total_stars: number;
  total_pull_requests: number;
  total_issues: number;
  commit_activity: {
    total_7_days: number;
    total_30_days: number;
  };
  languages: {
    [key: string]: {
      count: number;
      percentage: number;
    };
  };
  contribution_years?: number[];
  followers?: number;
  following?: number;
}

export interface LocationData {
  display_name: string;
  lat: number;
  lon: number;
  address?: {
    city?: string;
    state?: string;
    country?: string;
  };
}

export interface SoundCloudTrack {
  title: string;
  permalink_url: string;
  artwork_url: string | null;
  created_at: string;
  duration: number;
  playback_count: number;
  likes_count: number;
  comment_count: number;
}

export interface ThemeConfig {
  default_theme: string;
  themes: {
    dark: Theme;
    light: Theme;
  };
}

export interface Theme {
  colors: {
    background: {
      primary: string;
      secondary: string;
      dark: string;
      panel: string;
      panel_sleep: string;
      panel_readiness: string;
      panel_activity: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
      accent: string;
    };
    accent: {
      [key: string]: string;
    };
    scores: {
      high: string;
      medium: string;
      low: string;
    };
    status: {
      success: string;
      warning: string;
      error: string;
      unknown: string;
    };
    languages: {
      [key: string]: string;
    };
    chart: {
      bar_background: string;
    };
  };
  gradients: {
    background: {
      default: string[];
      dark: string[];
    };
    sleep: string[];
    readiness: string[];
    activity: string[];
    heart_rate: string[];
    developer: string[];
    weather: {
      [key: string]: string[];
    };
  };
  typography?: {
    [key: string]: string | number;
  };
  spacing?: {
    [key: string]: string | number;
  };
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at?: string;
}

export interface AIIdentity {
  persona: string;
  traits: string[];
  insights: string[];
  updated_at: string;
}
