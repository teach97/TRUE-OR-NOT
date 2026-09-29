import Link from 'next/link';

export const metadata = {title: '이용약관 · True or Not'};

export default function TermsPage() {
  return <main className="policy-page">
    <Link href="/">True or Not으로 돌아가기</Link>
    <h1>이용약관</h1>
    <p>시행일: 2026년 9월 23일 · 개발 중인 서비스의 이용 안내입니다. 정식 공개 전 운영자 정보와 법적 검토가 필요합니다.</p>

    <section>
      <h2>서비스의 성격</h2>
      <p>True or Not은 입력한 주장과 공개 출처를 비교해 참고 결과를 제공합니다. 결과와 점수는 오류가 있을 수 있으며 전문적인 판단이나 원출처 확인을 대체하지 않습니다. 특히 YouTube 공개 댓글은 사실 근거나 대표 의견이 아닙니다.</p>
    </section>

    <section>
      <h2>YouTube 기능</h2>
      <p>YouTube 자료 조회 기능을 사용하는 경우 사용자는 <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 서비스 약관</a>을 확인하고 이에 구속되는 데 동의해야 합니다. 이 기능은 공식 YouTube Data API를 통해 검색된 영상의 제목·채널명·게시일·조회수와 최대 10개의 공개 최상위 댓글을 조회합니다. 자막, 영상, 댓글 답글은 수집하지 않습니다. 댓글 옆 프로필 그림은 실제 댓글 작성자를 나타내지 않는 임의 생성 이미지입니다.</p>
      <p>YouTube 댓글은 영상별로 구분해 참고용 원문으로만 표시합니다. AI 판정 또는 인용 근거로 사용하지 않고, YouTube Data API에서 받은 메타데이터와 함께 JSON 내보내기에서도 제외합니다. YouTube 자료의 권리와 이용 조건은 해당 서비스 약관 및 <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보처리방침</a>을 따릅니다.</p>
    </section>

    <section>
      <h2>사용자의 책임</h2>
      <p>사용자는 제출할 권한이 있는 정보만 입력하고, 법률·안전·재정 등 중요한 판단에는 원자료와 적절한 전문가를 함께 확인해야 합니다. 원문·이미지·링크를 보내면 외부 AI·검색 제공자에게 전송됩니다. 전송에 동의하지 않는 경우 해당 검증 기능을 이용하지 마세요.</p>
    </section>

    <section>
      <h2>개인정보 처리</h2>
      <p>수집·이용·보관에 관한 자세한 내용은 <Link href="/privacy">개인정보 처리방침</Link>을 확인해 주세요.</p>
    </section>
  </main>;
}
