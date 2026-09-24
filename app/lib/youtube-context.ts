import type {FactSource} from './fact-check-contract';

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
    ? {...source, youtubeTitle: null, youtubeComments: [], youtubeDataStatus: 'not_applicable'}
    : source);
}
