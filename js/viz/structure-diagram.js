/* ═══════════════════════════════════════════════
   Corporate Structure Diagram — SVG Hierarchical Layout
   Shows ownership chains, holding structures, subsidiaries
   ═══════════════════════════════════════════════ */

function stripCurrencyHtml(text) {
  if (!text) return text;
  var audience = window.AUDIENCE || 'lyreco';
  if (audience === 'wefun') {
    // Remove EUR spans, keep KRW content
    text = text.replace(/<span class="cur-eur">[^<]*<\/span>/g, '');
    text = text.replace(/<span class="cur-krw">([^<]*)<\/span>/g, '$1');
  } else {
    // Remove KRW spans, keep EUR content
    text = text.replace(/<span class="cur-krw">[^<]*<\/span>/g, '');
    text = text.replace(/<span class="cur-eur">([^<]*)<\/span>/g, '$1');
  }
  // Strip any remaining HTML tags for SVG safety
  text = text.replace(/<[^>]+>/g, '');
  return text.trim();
}

function createStructureDiagram(containerId, config) {
  var container = document.getElementById(containerId);
  if (!container) return;

  var cfg = Object.assign({
    width: 900,
    tiers: [],
    connections: [],
    title: ''
  }, config || {});

  // Calculate height based on tiers
  var tierHeight = 120;
  var headerH = cfg.title ? 40 : 0;
  var totalH = headerH + (cfg.tiers.length * tierHeight) + 60;

  var html = '<svg viewBox="0 0 ' + cfg.width + ' ' + totalH + '" style="width:100%;height:auto;" xmlns="http://www.w3.org/2000/svg">';

  // Background
  html += '<rect width="100%" height="100%" fill="transparent"/>';

  // Title
  if (cfg.title) {
    html += '<text x="' + (cfg.width / 2) + '" y="24" text-anchor="middle" font-family="\'JetBrains Mono\', monospace" font-size="10" fill="#A0A0AC" letter-spacing="0.2em" text-transform="uppercase">' + cfg.title.toUpperCase() + '</text>';
  }

  var nodePositions = {};

  // Render tiers
  cfg.tiers.forEach(function(tier, tierIndex) {
    var y = headerH + 30 + (tierIndex * tierHeight);
    var nodeCount = tier.nodes.length;
    var totalWidth = Math.min(cfg.width - 80, nodeCount * 180);
    var startX = (cfg.width - totalWidth) / 2;
    var gap = nodeCount > 1 ? totalWidth / (nodeCount - 1) : 0;

    // Tier background band
    html += '<rect x="20" y="' + (y - 10) + '" width="' + (cfg.width - 40) + '" height="' + (tierHeight - 20) + '" rx="12" fill="rgba(244,242,237,0.02)" stroke="rgba(244,242,237,0.04)" stroke-width="0.5"/>';

    // Tier label
    if (tier.label) {
      html += '<text x="40" y="' + (y + 6) + '" font-family="\'JetBrains Mono\', monospace" font-size="8" fill="#A0A0AC" letter-spacing="0.15em">' + tier.label.toUpperCase() + '</text>';
    }

    tier.nodes.forEach(function(node, nodeIndex) {
      var nx = nodeCount === 1 ? cfg.width / 2 : startX + (nodeIndex * gap);
      var ny = y + 30;
      nodePositions[node.id] = { x: nx, y: ny };

      var boxW = node.wide ? 200 : 150;
      var boxH = 56;
      var color = node.color || '#C9A96E';

      // Node box
      html += '<rect x="' + (nx - boxW / 2) + '" y="' + (ny - boxH / 2) + '" width="' + boxW + '" height="' + boxH + '" rx="10" fill="rgba(' + hexToRgb(color) + ',0.08)" stroke="rgba(' + hexToRgb(color) + ',0.25)" stroke-width="1"/>';

      // Node label
      html += '<text x="' + nx + '" y="' + (ny - 4) + '" text-anchor="middle" font-family="\'DM Sans\', sans-serif" font-size="11" font-weight="600" fill="#F4F2ED">' + node.label + '</text>';

      // Sublabel
      if (node.sublabel) {
        var cleanSub = stripCurrencyHtml(node.sublabel);
        html += '<text x="' + nx + '" y="' + (ny + 12) + '" text-anchor="middle" font-family="\'JetBrains Mono\', monospace" font-size="8" fill="' + color + '" letter-spacing="0.05em">' + cleanSub + '</text>';
      }

      // Badge — top-right corner, fully inside box bounds
      if (node.badge) {
        var cleanBadge = stripCurrencyHtml(node.badge);
        var bw = Math.max(32, cleanBadge.length * 7 + 10);
        var bx = nx + boxW / 2 - bw - 4;
        var by = ny - boxH / 2 - 9;
        html += '<rect x="' + bx + '" y="' + by + '" width="' + bw + '" height="17" rx="8" fill="' + color + '"/>';
        html += '<text x="' + (bx + bw / 2) + '" y="' + (by + 11) + '" text-anchor="middle" font-family="\'JetBrains Mono\', monospace" font-size="8" fill="#111115" font-weight="700">' + cleanBadge + '</text>';
      }
    });
  });

  // Render connections
  cfg.connections.forEach(function(conn) {
    var from = nodePositions[conn.from];
    var to = nodePositions[conn.to];
    if (!from || !to) return;

    var fromY = from.y + 28;
    var toY = to.y - 28;
    var midY = (fromY + toY) / 2;

    // Curved connection line
    html += '<path d="M ' + from.x + ' ' + fromY + ' C ' + from.x + ' ' + midY + ' ' + to.x + ' ' + midY + ' ' + to.x + ' ' + toY + '" fill="none" stroke="rgba(201,169,110,0.2)" stroke-width="1.5" stroke-dasharray="' + (conn.dashed ? '4,4' : 'none') + '"/>';

    // Arrow
    html += '<polygon points="' + (to.x - 4) + ',' + (toY - 4) + ' ' + to.x + ',' + toY + ' ' + (to.x + 4) + ',' + (toY - 4) + '" fill="rgba(201,169,110,0.3)"/>';

    // Connection label
    if (conn.label) {
      var cleanConn = stripCurrencyHtml(conn.label);
      html += '<text x="' + ((from.x + to.x) / 2 + 8) + '" y="' + midY + '" font-family="\'JetBrains Mono\', monospace" font-size="8" fill="#A0A0AC" letter-spacing="0.05em">' + cleanConn + '</text>';
    }
  });

  html += '</svg>';
  container.innerHTML = html;
}

function hexToRgb(hex) {
  hex = hex.replace('#', '');
  var r = parseInt(hex.substring(0, 2), 16);
  var g = parseInt(hex.substring(2, 4), 16);
  var b = parseInt(hex.substring(4, 6), 16);
  return r + ',' + g + ',' + b;
}
