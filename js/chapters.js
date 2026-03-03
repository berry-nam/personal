/* ═══════════════════════════════════════════════
   Chapter Metadata — Audience-Segmented
   ═══════════════════════════════════════════════ */

var CHAPTERS = {
  shared: [
    {
      num: 1, slug: '1-bookshop', audience: 'shared', displayOrder: 1,
      title: 'A Bookshop in Valenciennes',
      subtitle: 'Where a family legacy began — a century ago',
      readTime: '6 min',
      teaser: 'In 1926, in a small town in northern France, Georges-Gaston Gaspard opened a bookshop. Four generations later, it became a <span class="cur-eur">€3 billion</span><span class="cur-krw">₩4.35조</span> empire.',
      teaserKr: '1926년, 프랑스 북부의 작은 마을에서 조르주-가스통 가스파르가 서점을 열었습니다. 4대에 걸쳐 <span class="cur-eur">30억 유로</span><span class="cur-krw">₩4.35조</span> 제국이 되었습니다.',
    },
    {
      num: 2, slug: '2-dynasty', audience: 'shared', displayOrder: 2,
      title: 'The Gaspard Dynasty',
      subtitle: 'Four generations of family control through Corely SAS',
      readTime: '8 min',
      teaser: 'The Gaspard family controls Lyreco through Corely SAS via Holding Lyreco France. Their investment vehicles reach from artificial hearts to Belgian real estate.',
      teaserKr: '가스파르 가문은 Corely SAS를 통해 Holding Lyreco France를 거쳐 리레코를 지배합니다. 인공심장에서 벨기에 부동산까지 그들의 투자 영역은 넓습니다.',
    },
    {
      num: 3, slug: '3-bigeard', audience: 'shared', displayOrder: 3,
      title: 'The Bigeard Era',
      subtitle: 'The legendary CEO who built a €2B empire from €15M',
      readTime: '10 min',
      teaser: 'Eric Bigeard became CEO at 33 and spent 22 years transforming Lyreco from a French-only operation into a 29-country powerhouse.',
      teaserKr: '에릭 비제아르는 33세에 CEO가 되어 22년간 리레코를 프랑스 전용 기업에서 29개국 강자로 성장시켰습니다.',
    },
    {
      num: 4, slug: '4-goes-east', audience: 'shared', displayOrder: 4,
      title: 'Lyreco Goes East',
      subtitle: 'Hong Kong, Korea, Singapore — the Asian expansion',
      readTime: '8 min',
      teaser: 'Starting with Hong Kong in 1996, Lyreco built a five-market Asian presence. Korea\'s "Lounge Service" directly mirrors workplace wellness trends.',
      teaserKr: '1996년 홍콩을 시작으로 리레코는 아시아 5개 시장에 진출했습니다. 한국의 "라운지 서비스"는 직장 웰니스 트렌드를 직접 반영합니다.',
    },
    {
      num: 5, slug: '5-christmas-eve', audience: 'shared', displayOrder: 5,
      title: 'Christmas Eve 2018',
      subtitle: 'The founding of WEFUN and its extraordinary growth',
      readTime: '12 min',
      teaser: 'Kim Heon incorporated WEFUN on December 24, 2018 with <span class="cur-eur">€34K</span><span class="cur-krw">₩50M</span>. Seven years later: <span class="cur-eur">€138M</span><span class="cur-krw">₩2,000억</span> revenue, 800 employees, 6 acquisitions.',
      teaserKr: '김헌 대표는 2018년 12월 24일 자본금 <span class="cur-eur">€34K</span><span class="cur-krw">5천만 원</span>으로 위펀을 설립했습니다. 7년 후: 매출 <span class="cur-eur">€138M</span><span class="cur-krw">2,000억 원</span>, 800명, 6건의 인수.',
    },
    {
      num: 7, slug: '7-convergence', audience: 'shared', displayOrder: 7,
      title: 'Convergence',
      subtitle: 'Where two stories meet — the strategic thesis',
      readTime: '8 min',
      teaser: 'WeFun and Lyreco are converging on the same destination from opposite directions. The combined entity creates something that doesn\'t yet exist in Asia.',
      teaserKr: '위펀과 리레코는 반대 방향에서 같은 목적지를 향해 수렴하고 있습니다. 통합 기업은 아시아에 아직 없는 것을 만들어냅니다.',
    },
  ],
  wefun: [
    {
      num: 6, slug: '6-people', audience: 'wefun', displayOrder: 6,
      title: 'The People in the Room',
      subtitle: 'Deep profiles of everyone at the table on February 26',
      readTime: '14 min',
      teaser: 'Helen Riley: 20-year Lyreco lifer turned M&A director. Eric Bigeard: the legendary ex-CEO and guardian of legacy. Know who you\'re meeting.',
      teaserKr: '헬렌 라일리: 20년 리레코 경력의 M&A 디렉터. 에릭 비제아르: 전설적인 전 CEO이자 레거시 수호자. 만날 분들을 파악하세요.',
    },
    {
      num: 8, slug: '8-february-26', audience: 'wefun', displayOrder: 8,
      title: 'February 26',
      subtitle: 'The meeting playbook — every minute planned',
      readTime: '10 min',
      teaser: 'This is 70% relationship, 30% substance. The meeting architecture should feel like a conversation between believers.',
      teaserKr: '관계 70%, 실질 30%. 미팅은 신념을 공유하는 이들 간의 대화처럼 느껴져야 합니다.',
    },
    {
      num: 9, slug: 'w1-strategy-notes', audience: 'wefun', displayOrder: 9,
      title: 'Buyer\'s Playbook',
      subtitle: 'Strategic intelligence consolidated from all chapters',
      readTime: '15 min',
      teaser: 'Negotiation insights, talking points, and strategic framings — everything WeFun needs to prepare for the conversation.',
      teaserKr: '협상 인사이트, 대화 포인트, 전략적 프레이밍 — 위펀이 대화 준비에 필요한 모든 것.',
    },
  ],
  lyreco: [
    {
      num: 6, slug: 'l1-wefun-profile', audience: 'lyreco', displayOrder: 6,
      title: 'Inside WeFun',
      subtitle: 'A comprehensive profile of your potential partner',
      readTime: '12 min',
      teaser: 'From a Christmas Eve founding to €138M in revenue — WeFun\'s growth, platform, M&A track record, and the team behind it.',
      teaserKr: '크리스마스 이브 창업부터 매출 €138M까지 — 위펀의 성장, 플랫폼, M&A 실적, 그리고 팀.',
    },
    {
      num: 7, slug: '7-convergence', audience: 'shared', displayOrder: 7,
      title: 'Convergence',
      subtitle: 'Where two stories meet — the strategic thesis',
      readTime: '8 min',
      teaser: 'WeFun and Lyreco are converging on the same destination from opposite directions. The combined entity creates something that doesn\'t yet exist in Asia.',
      teaserKr: '위펀과 리레코는 반대 방향에서 같은 목적지를 향해 수렴하고 있습니다. 통합 기업은 아시아에 아직 없는 것을 만들어냅니다.',
    },
    {
      num: 8, slug: 'l3-lyreco-convergence', audience: 'lyreco', displayOrder: 8,
      title: 'Why This Makes Sense',
      subtitle: 'The partnership argument — from Lyreco\'s perspective',
      readTime: '10 min',
      teaser: 'Asia is 3% of group revenue. A locally-rooted operator with proven M&A integration can unlock its full potential.',
      teaserKr: '아시아는 그룹 매출의 3%입니다. 검증된 M&A 통합 역량을 갖춘 현지 운영자가 잠재력을 발휘할 수 있습니다.',
    },
    {
      num: 9, slug: 'l2-deal-tracker', audience: 'lyreco', displayOrder: 9,
      title: 'Deal Milestones',
      subtitle: 'Timeline, contacts, and next steps',
      readTime: '5 min',
      teaser: 'Key dates, meeting log, WeFun team contacts, and outstanding questions — a living document updated as the deal progresses.',
      teaserKr: '주요 일정, 미팅 기록, 위펀 팀 연락처, 미해결 사항 — 딜 진행에 따라 업데이트되는 문서.',
    },
  ],
};

// ─── Helpers ───

function toRoman(num) {
  var map = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'];
  return map[num - 1] || String(num);
}

function getChaptersForAudience(audience) {
  var list = [];
  // Add shared chapters
  CHAPTERS.shared.forEach(function (ch) { list.push(ch); });
  // Add audience-specific chapters
  if (audience && CHAPTERS[audience]) {
    CHAPTERS[audience].forEach(function (ch) {
      // Avoid duplicate convergence for lyreco
      var isDupe = list.some(function (existing) { return existing.slug === ch.slug; });
      if (!isDupe) list.push(ch);
    });
  }
  // Sort by displayOrder
  list.sort(function (a, b) { return a.displayOrder - b.displayOrder; });
  return list;
}

function getAdjacentChapters(slug, audience) {
  var list = getChaptersForAudience(audience);
  var idx = -1;
  for (var i = 0; i < list.length; i++) {
    if (list[i].slug === slug) { idx = i; break; }
  }
  if (idx === -1) return { prev: null, next: null };
  return {
    prev: idx > 0 ? list[idx - 1] : null,
    next: idx < list.length - 1 ? list[idx + 1] : null,
  };
}
