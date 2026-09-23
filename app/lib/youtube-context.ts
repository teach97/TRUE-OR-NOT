import type {FactSource} from './fact-check-contract';

/** Keep API-provided YouTube text in the live view only, not downloaded results. */
export function stripYoutubeApiDataForExport(sources: FactSource[]): FactSource[] {
  return sources.map(source => source.sourceType === '유튜브'
    ? {...source, youtubeTitle: null, youtubeComments: [], youtubeDataStatus: 'not_applicable'}
    : source);
}
