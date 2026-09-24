import type {FactSource} from './fact-check-contract';

const YOUTUBE_PUBLISHED_AT = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$/;

export function formatYoutubePublishedAt(value: string | null): string | null {
  if (typeof value !== 'string' || value.length > 50 || !YOUTUBE_PUBLISHED_AT.test(value)) return null;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return null;
  return `${date.getUTCFullYear()}.${String(date.getUTCMonth() + 1).padStart(2, '0')}.${String(date.getUTCDate()).padStart(2, '0')}`;
}

export function formatYoutubeViewCount(value: string | null): string | null {
  if (typeof value !== 'string' || !/^\d{1,30}$/.test(value)) return null;
  return `${value.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}회`;
}

/** Build a YouTube thumbnail URL only for recognized HTTPS video URLs. */
export function youtubeThumbnailUrl(rawUrl: string): string | null {
  if (typeof rawUrl !== 'string' || rawUrl.length > 2048) return null;

  try {
    const parsed = new URL(rawUrl);
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.port) return null;

    const host = parsed.hostname.toLowerCase().replace(/\.$/, '');
    let videoId = '';
    if (host === 'youtu.be') {
      const parts = parsed.pathname.split('/').filter(Boolean);
      videoId = parts.length === 1 ? parts[0] : '';
    } else if (['youtube.com', 'www.youtube.com', 'm.youtube.com'].includes(host)) {
      if (parsed.pathname === '/watch') {
        const ids = parsed.searchParams.getAll('v');
        videoId = ids.length === 1 ? ids[0] : '';
      } else {
        const parts = parsed.pathname.split('/').filter(Boolean);
        videoId = parts.length === 2 && ['embed', 'live', 'shorts', 'v'].includes(parts[0]) ? parts[1] : '';
      }
    }

    return /^[A-Za-z0-9_-]{11}$/.test(videoId)
      ? `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`
      : null;
  } catch {
    return null;
  }
}

/** Keep API-provided YouTube text in the live view only, not downloaded results. */
export function stripYoutubeApiDataForExport(sources: FactSource[]): FactSource[] {
  return sources.map(source => source.sourceType === '유튜브'
    ? {
      ...source,
      youtubeTitle: null,
      youtubeChannelTitle: null,
      youtubePublishedAt: null,
      youtubeViewCount: null,
      youtubeComments: [],
      youtubeDataStatus: 'not_applicable',
    }
    : source);
}
