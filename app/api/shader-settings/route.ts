import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { normalizeShaderSettings } from '../../components/shader-settings';

export const runtime = 'nodejs';

const settingsFile = path.join(process.cwd(), 'app', 'components', 'shader-settings-config.ts');

function sourceFor(settings: ReturnType<typeof normalizeShaderSettings>) {
  return [
    "import type { ShaderSettings } from './shader-settings';",
    '',
    `export const defaultShaderSettings: ShaderSettings = ${JSON.stringify(settings, null, 2)};`,
    '',
  ].join('\n');
}

export async function POST(request: Request) {
  if (process.env.NODE_ENV === 'production') {
    return Response.json({error: '프로젝트 설정 저장은 개발 환경에서만 사용할 수 있습니다.'}, {status: 404});
  }

  const origin = request.headers.get('origin');
  const requestUrl = new URL(request.url);
  const forwardedProtocol = request.headers.get('x-forwarded-proto') || requestUrl.protocol.replace(':', '');
  const hostOrigin = `${forwardedProtocol}://${request.headers.get('host') || requestUrl.host}`;
  if (origin && origin !== requestUrl.origin && origin !== hostOrigin) {
    return Response.json({error: '다른 출처에서 프로젝트 설정을 저장할 수 없습니다.'}, {status: 403});
  }

  try {
    const settings = normalizeShaderSettings(await request.json());
    await writeFile(settingsFile, sourceFor(settings), 'utf8');
    return Response.json({ok: true});
  } catch {
    return Response.json({error: '프로젝트 설정 파일을 저장하지 못했습니다.'}, {status: 500});
  }
}