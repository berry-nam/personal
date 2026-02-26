/* ═══════════════════════════════════════════════
   Chapter Metadata
   ═══════════════════════════════════════════════ */

const CHAPTERS = [
  {
    num: 1,
    slug: '1-bookshop',
    title: 'A Bookshop in Valenciennes',
    subtitle: 'Where a family legacy began — a century ago',
    readTime: '6 min',
    teaser: 'In 1926, in a small town in northern France, Georges-Gaston Gaspard opened a bookshop. Four generations later, it became a €3 billion empire.',
  },
  {
    num: 2,
    slug: '2-dynasty',
    title: 'The Gaspard Dynasty',
    subtitle: 'Four generations of family control through Corely SAS',
    readTime: '10 min',
    teaser: 'The Gaspard family controls Lyreco through Corely SAS via Holding Lyreco France. ~€2.5B revenue, 100% family-owned, no PE pressure. Selling from strength, not weakness.',
  },
  {
    num: 3,
    slug: '3-bigeard',
    title: 'The Bigeard Era',
    subtitle: 'The legendary CEO who built a €2B empire from €15M',
    readTime: '10 min',
    teaser: 'Eric Bigeard became CEO at 33 and spent 22 years transforming Lyreco from a French-only operation into a 29-country powerhouse.',
  },
  {
    num: 4,
    slug: '4-goes-east',
    title: 'Lyreco Goes East',
    subtitle: 'Hong Kong, Korea, Singapore — the Asian expansion',
    readTime: '14 min',
    teaser: 'Canada (2014), Australia (2018) — now Asia. Lyreco\'s divestment playbook: exit distant markets, keep as partner, buy deep in Europe. Korea\'s "Lounge Service" mirrors WEFUN.',
  },
  {
    num: 5,
    slug: '5-christmas-eve',
    title: 'Christmas Eve 2018',
    subtitle: 'The founding of WEFUN and its extraordinary growth',
    readTime: '12 min',
    teaser: 'Kim Heon incorporated WEFUN on December 24, 2018 with ₩50M. Seven years later: ₩143B revenue, 252 employees, 6 acquisitions, IPO imminent.',
  },
  {
    num: 6,
    slug: '6-people',
    title: 'The People in the Room',
    subtitle: 'Deep profiles of everyone at the table on February 26',
    readTime: '14 min',
    teaser: 'Helen Riley: 20-year Lyreco lifer turned M&A director. Eric Bigeard: the legendary ex-CEO and guardian of legacy. Know who you\'re meeting.',
  },
  {
    num: 7,
    slug: '7-convergence',
    title: 'Convergence',
    subtitle: 'Where two stories meet — the strategic thesis',
    readTime: '16 min',
    teaser: 'WEFUN and Lyreco converge from opposite directions. The partner model precedent, GREAT 2026 strategy, Lyreco\'s €2.5B financial context, and the industry-wide rationalization.',
  },
  {
    num: 8,
    slug: '8-february-26',
    title: 'February 26',
    subtitle: 'The meeting playbook — every minute planned',
    readTime: '10 min',
    teaser: 'This is 70% relationship, 30% substance. The meeting architecture should feel like a conversation between believers, not a pitch deck review.',
  },
];

// Roman numeral helper
function toRoman(num) {
  const map = ['I','II','III','IV','V','VI','VII','VIII'];
  return map[num - 1] || num;
}
