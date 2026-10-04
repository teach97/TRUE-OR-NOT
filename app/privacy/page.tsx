import Link from 'next/link';

export const metadata = {title: '개인정보 처리방침 · True or Not'};

export default function PrivacyPage() {
  return <main className="policy-page">
    <Link href="/">True or Not으로 돌아가기</Link>
    <h1>개인정보 처리방침</h1>
    <p>수정일: 2026년 10월 4일 · 개발 중인 서비스의 현재 데이터 흐름을 설명합니다. 정식 공개 전 운영자 정보와 법적 검토가 필요합니다.</p>

    <section>
      <h2>수집·이용하는 정보</h2>
      <ul>
        <li>사용자가 제출한 원문과 확인 요청은 검증을 위해 서버, 설정된 AI 제공자(OpenAI 또는 Google Gemini), 웹 검색 기능과 검색된 공개 웹사이트로 전송됩니다. 제출 자체가 전송·처리에 대한 동의로 간주됩니다.</li>
        <li>채팅에 첨부한 링크의 페이지는 서버에서 직접 가져와 검증에 사용합니다. 첨부한 이미지는 주장 추출을 위해 AI 제공자에게 전송되며, 서버에 저장하지 않고 검증이 끝나면 버립니다. 얼굴·신분증 등 식별 가능한 이미지는 보내지 마세요.</li>
        <li>YouTube Data API 키가 서버에 설정되어 있으면 검색된 YouTube 영상의 ID를 Google에 보내고, 영상 제목·채널명·게시일·조회수와 관련도순 공개 최상위 댓글을 최대 10개 조회합니다. 자막·영상·답글은 수집하지 않습니다. 댓글 왼쪽 프로필 그림은 실제 이용자 사진이 아니라 화면에서 임의로 생성하는 장식 이미지입니다.</li>
        <li>YouTube 댓글은 영상별 원문 그대로 화면에 표시하는 참고 맥락입니다. 댓글을 AI 입력, 주장 판정 또는 인용 근거로 사용하지 않으며, 댓글만으로 여론이나 대표 의견을 의미하지 않습니다.</li>
      </ul>
    </section>

    <section>
      <h2>보관 및 삭제</h2>
      <p>대화 저장은 기본 꺼짐이며 검증을 위한 외부 전송 동의와 별개입니다. ‘이 브라우저에서 대화 저장’을 켠 이후의 사용자 메시지, 완료·실패·취소된 답변 및 최소 검증 결과를 Render PostgreSQL에 저장합니다. 최소 결과에는 검증 대상·확인 요청·주장·판정·인용·출처 URL/제목/발행인·검증 시각이 포함됩니다. 외부 페이지의 전체 원문, 첨부 이미지, 진행 중 메시지, 시장 데이터 및 YouTube API에서 받은 제목·채널명·게시일·조회수·댓글은 대화 DB에 저장하지 않습니다.</p>
      <p>로그인 없이 30일 유효한 HttpOnly 익명 쿠키로 대화 소유권을 확인합니다. 쿠키 삭제·만료 또는 서명 키 변경 시 이전 기록에 다시 접근할 수 없습니다. 이는 DB 기록의 자동 삭제를 뜻하지 않습니다. 저장을 끄면 새 메시지는 저장하지 않으며 기존 대화는 목록의 삭제 버튼으로 대화와 메시지를 함께 삭제할 수 있습니다. 시연용 무료 DB는 2026년 11월 3일 만료 예정이고 백업이 없어 영구 보관을 보장하지 않습니다. 지속 운영의 자동 삭제·백업 정책은 정식 공개 전에 확정합니다.</p>
      <p>저장하지 않는 결과와 YouTube API 정보는 활성 화면의 메모리에만 있습니다. JSON 내보내기에는 YouTube Data API에서 받은 정보를 포함하지 않습니다. AI·검색·Google 서비스로 전송된 정보에는 각 제공자의 정책이 별도로 적용됩니다.</p>
      <p>대화 삭제 시 제목과 모든 메시지·검증 결과는 삭제합니다. 생성 응답이 유실된 다른 탭에서 재시도해 삭제한 내용이 되살아나지 않도록, 익명 소유자·대화/생성 요청 식별자·삭제 시각 등 내용이 없는 중복 방지 표식만 DB에 남깁니다. 이 표식으로는 대화 내용을 복원할 수 없습니다.</p>
    </section>

    <section>
      <h2>외부 서비스</h2>
      <p>YouTube 기능을 제공할 때 <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 서비스 약관</a>과 <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보처리방침</a>이 적용됩니다. 민감정보나 제3자의 비공개 정보를 원문에 입력하지 마세요.</p>
    </section>

    <section>
      <h2>이용자 선택</h2>
      <p>검증을 시작하면 원문·이미지·링크가 위와 같이 외부로 전송됩니다. 전송을 원하지 않으면 검증 기능을 이용하지 마세요. YouTube API 키가 없거나 댓글 조회가 허용되지 않은 영상은 댓글을 표시하지 않으며, 다른 출처의 검증은 계속 진행할 수 있습니다.</p>
    </section>

    <section>
      <h2>관련 문서</h2>
      <p><Link href="/terms">이용약관</Link> · <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 서비스 약관</a> · <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보처리방침</a></p>
    </section>
  </main>;
}
