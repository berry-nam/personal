/* ═══════════════════════════════════════════════
   Interactive Asia Map — SVG Market Visualization
   ═══════════════════════════════════════════════ */

function createAsiaMap(containerId) {
  var container = document.getElementById(containerId);
  if (!container) return;

  var w = 700, h = 500;

  // Market locations (approximate lat/lon → SVG coords)
  var markets = [
    { id: 'hk', label: 'Hong Kong', year: '1996', x: 485, y: 290, detail: 'Zone HQ · Est. 1996/97 · ISO 9001 & 14001', color: '#C9A96E', delay: 0 },
    { id: 'kr', label: 'Korea', year: '2004', x: 530, y: 210, detail: 'Est. April 2004 · €16M Revenue · Lounge Service', color: '#4A72FF', delay: 400 },
    { id: 'sg', label: 'Singapore', year: '2005', x: 440, y: 380, detail: 'Est. 2005 · Deskright 2019 · €19M Revenue · ASEAN Hub', color: '#C9A96E', delay: 800 },
    { id: 'my', label: 'Malaysia', year: '2005', x: 410, y: 350, detail: 'Est. 2005 · €4.5M Revenue · ASEAN Growth', color: '#C9A96E', delay: 1200 },
    { id: 'th', label: 'Thailand', year: '2002', x: 380, y: 310, detail: 'Est. 2002 · €29.6M Revenue · Largest Asian Market', color: '#C9A96E', delay: 1600 }
  ];

  // Connection routes
  var routes = [
    { from: 'hk', to: 'kr' },
    { from: 'hk', to: 'sg' },
    { from: 'sg', to: 'my' },
    { from: 'sg', to: 'th' }
  ];

  var html = '<svg viewBox="0 0 ' + w + ' ' + h + '" style="width:100%;height:auto;max-height:500px;" xmlns="http://www.w3.org/2000/svg">';

  // Subtle grid
  html += '<defs><pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">';
  html += '<path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(244,242,237,0.03)" stroke-width="0.5"/>';
  html += '</pattern></defs>';
  html += '<rect width="100%" height="100%" fill="url(#grid-pattern)"/>';

  // Simplified Asia coastline outline (decorative)
  html += '<path d="M 300,80 Q 340,100 370,120 Q 400,140 430,160 Q 460,170 500,180 L 540,190 Q 560,200 550,230 Q 545,250 530,260 Q 520,270 500,280 Q 490,300 470,320 Q 450,340 440,360 Q 430,380 420,400 Q 400,420 380,430 L 350,410 Q 330,380 320,350 Q 310,320 300,290 Q 290,260 285,230 Q 280,200 290,170 Q 295,140 300,120 Z" fill="rgba(244,242,237,0.03)" stroke="rgba(244,242,237,0.06)" stroke-width="1"/>';

  // Connection lines (animated)
  var marketMap = {};
  markets.forEach(function(m) { marketMap[m.id] = m; });

  routes.forEach(function(r) {
    var from = marketMap[r.from];
    var to = marketMap[r.to];
    html += '<line class="map-route" x1="' + from.x + '" y1="' + from.y + '" x2="' + to.x + '" y2="' + to.y + '" stroke="rgba(201,169,110,0.15)" stroke-width="1" stroke-dasharray="4,4"/>';
  });

  // Market dots and labels
  markets.forEach(function(m) {
    // Pulse ring
    html += '<circle class="map-pulse" cx="' + m.x + '" cy="' + m.y + '" r="8" fill="none" stroke="' + m.color + '" stroke-width="1" opacity="0" style="animation: mapPulse 2s ' + (m.delay + 500) + 'ms infinite">';
    html += '</circle>';
    // Core dot
    html += '<circle class="map-dot" cx="' + m.x + '" cy="' + m.y + '" r="5" fill="' + m.color + '" opacity="0" style="animation: mapDotIn 0.6s ' + m.delay + 'ms forwards"/>';
    // Label
    html += '<text x="' + m.x + '" y="' + (m.y - 14) + '" text-anchor="middle" font-family="\'DM Sans\', sans-serif" font-size="11" font-weight="600" fill="#F4F2ED" opacity="0" style="animation: mapDotIn 0.6s ' + (m.delay + 200) + 'ms forwards">' + m.label + '</text>';
    // Year tag
    html += '<text x="' + m.x + '" y="' + (m.y + 20) + '" text-anchor="middle" font-family="\'JetBrains Mono\', monospace" font-size="8" fill="' + m.color + '" letter-spacing="0.1em" opacity="0" style="animation: mapDotIn 0.6s ' + (m.delay + 300) + 'ms forwards">' + m.year + '</text>';
  });

  html += '</svg>';

  // CSS for animations
  html += '<style>';
  html += '@keyframes mapDotIn { from { opacity: 0; transform: scale(0.5); } to { opacity: 1; transform: scale(1); } }';
  html += '@keyframes mapPulse { 0% { r: 8; opacity: 0.6; } 100% { r: 24; opacity: 0; } }';
  html += '</style>';

  container.innerHTML = html;

  // Add interactive tooltips
  container.style.position = 'relative';
  var tooltip = document.createElement('div');
  tooltip.style.cssText = 'position:absolute;background:#242430;border:1px solid rgba(201,169,110,0.25);border-radius:12px;padding:10px 14px;font-size:11px;color:#F4F2ED;pointer-events:none;opacity:0;transition:opacity 0.2s;z-index:10;font-family:"DM Sans",sans-serif;max-width:220px;';
  container.appendChild(tooltip);

  var dots = container.querySelectorAll('.map-dot');
  dots.forEach(function(dot, i) {
    var m = markets[i];
    dot.style.cursor = 'pointer';
    dot.addEventListener('mouseover', function(e) {
      tooltip.innerHTML = '<strong style="color:' + m.color + '">' + m.label + '</strong><div style="margin-top:4px;color:#A0A0AC;font-size:10px;">' + m.detail + '</div>';
      tooltip.style.opacity = '1';
    });
    dot.addEventListener('mousemove', function(e) {
      var rect = container.getBoundingClientRect();
      tooltip.style.left = (e.clientX - rect.left + 12) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
    });
    dot.addEventListener('mouseout', function() {
      tooltip.style.opacity = '0';
    });
  });
}
