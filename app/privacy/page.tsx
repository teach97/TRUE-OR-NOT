import Link from 'next/link';

export const metadata = {title: '개인정보 처리방침 · True or Not'};

export default function PrivacyPage() {
  return <main className="policy-page">
    <Link href="/">True or Not으로 돌아가기</Link>
    <h1>개인정보 처리방침</h1>
    <p>시행일: 2026년 9월 23일 · 개발 중인 서비스의 현재 데이터 흐름을 설명합니다. 정식 공개 전 운영자 정보와 법적 검토가 필요합니다.</p>

    <section>
      <h2>수집·이용하는 정보</h2>
      <ul>
        <li>사용자가 동의 후 제출한 원문과 확인 요청은 검증을 위해 서버, 설정된 AI 제공자(OpenAI 또는 Google Gemini), 웹 검색 기능과 검색된 공개 웹사이트로 전송됩니다.</li>
        <li>YouTube Data API 키가 서버에 설정되어 있으면 검색된 YouTube 영상의 ID를 Google에 보내고, 해당 영상의 제목과 관련도순 공개 최상위 댓글을 최대 10개 조회합니다. 자막·영상·답글은 수집하지 않습니다.</li>
        <li>YouTube 댓글은 영상별 원문 그대로 화면에 표시하는 참고 맥락입니다. 댓글을 AI 입력, 주장 판정 또는 인용 근거로 사용하지 않으며, 댓글만으로 여론이나 대표 의견을 의미하지 않습니다.</li>
      </ul>
    </section>

    <section>
      <h2>보관 및 삭제</h2>
      <p>현재 버전은 계정·검증 이력을 서버에 저장하지 않습니다. 검증 결과와 YouTube API에서 받은 제목·댓글은 활성 화면의 메모리에만 있으며 페이지를 새로고침하거나 초기화하면 사라집니다. JSON 내보내기에는 YouTube API 제목과 댓글을 포함하지 않습니다. AI·검색·Google 서비스로 전송된 정보에는 각 제공자의 정책이 별도로 적용됩니다.</p>
    </section>

    <section>
      <h2>외부 서비스</h2>
      <p>YouTube 기능을 제공할 때 <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 서비스 약관</a>과 <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보처리방침</a>이 적용됩니다. 민감정보나 제3자의 비공개 정보를 원문에 입력하지 마세요.</p>
    </section>

    <section>
      <h2>이용자 선택</h2>
      <p>외부 전송·검색 동의 체크박스를 선택하지 않으면 검증을 시작할 수 없습니다. YouTube API 키가 없거나 댓글 조회가 허용되지 않은 영상은 댓글을 표시하지 않으며, 다른 출처의 검증은 계속 진행할 수 있습니다.</p>
    </section>

    <section>
      <h2>관련 문서</h2>
      <p><Link href="/terms">이용약관</Link> · <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 서비스 약관</a> · <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보처리방침</a></p>
    </section>
  </main>;
}
