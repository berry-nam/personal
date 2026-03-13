/**
 * Cloudflare Pages middleware — server-side auth gate.
 *
 * Everything except gate.html and its assets requires a valid
 * signed session cookie. Unauthenticated requests are redirected to "/gate.html".
 *
 * POST /api/login  — validate password, set httpOnly cookie
 * POST /api/logout — clear cookie
 */

// ── Helpers ──────────────────────────────────────────────

async function sha256(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function hmacSign(payload, secret) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function hmacVerify(payload, signature, secret) {
  const expected = await hmacSign(payload, secret);
  return expected === signature;
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  header.split(';').forEach((pair) => {
    const [key, ...rest] = pair.trim().split('=');
    if (key) cookies[key.trim()] = rest.join('=').trim();
  });
  return cookies;
}

function sessionCookie(value, maxAge) {
  return `briefing_session=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${maxAge}`;
}

// ── Public path check (everything else is protected) ─────

function isPublic(pathname) {
  if (pathname === '/gate.html') return true;
  if (pathname === '/gate') return true;
  if (pathname === '/robots.txt') return true;
  if (pathname === '/favicon.ico') return true;
  if (pathname.startsWith('/css/')) return true;
  if (pathname.startsWith('/api/')) return true;
  return false;
}

// ── API handlers ─────────────────────────────────────────

async function handleLogin(request, env) {
  try {
    const body = await request.json();
    const password = (body.password || '').trim();
    if (!password) {
      return new Response(JSON.stringify({ error: 'Missing password' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const hash = await sha256(password);

    let audience = null;
    if (hash === env.LYRECO_HASH) audience = 'lyreco';
    else if (hash === env.WEFUN_HASH) audience = 'wefun';

    if (!audience) {
      return new Response(JSON.stringify({ error: 'Invalid password' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Build signed session: audience.timestamp.signature
    const ts = Date.now().toString();
    const payload = `${audience}.${ts}`;
    const sig = await hmacSign(payload, env.SESSION_SECRET);
    const token = `${payload}.${sig}`;

    const maxAge = 60 * 60 * 24 * 7; // 7 days

    return new Response(JSON.stringify({ audience }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': sessionCookie(token, maxAge),
      },
    });
  } catch {
    return new Response(JSON.stringify({ error: 'Bad request' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

function handleLogout() {
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Set-Cookie': sessionCookie('', 0),
    },
  });
}

// ── Session validation ───────────────────────────────────

async function validateSession(cookieHeader, secret) {
  const cookies = parseCookies(cookieHeader);
  const token = cookies['briefing_session'];
  if (!token) return null;

  const parts = token.split('.');
  if (parts.length !== 3) return null;

  const [audience, ts, sig] = parts;
  if (!audience || !ts || !sig) return null;

  const payload = `${audience}.${ts}`;
  const valid = await hmacVerify(payload, sig, secret);
  if (!valid) return null;

  // Check expiry (7 days)
  const age = Date.now() - parseInt(ts, 10);
  if (isNaN(age) || age > 7 * 24 * 60 * 60 * 1000) return null;

  if (audience !== 'lyreco' && audience !== 'wefun') return null;
  return audience;
}

// ── Main middleware ──────────────────────────────────────

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // API routes
  if (url.pathname === '/api/login' && request.method === 'POST') {
    return handleLogin(request, env);
  }
  if (url.pathname === '/api/logout' && request.method === 'POST') {
    return handleLogout();
  }

  // Everything except public paths requires a valid session
  if (!isPublic(url.pathname)) {
    const audience = await validateSession(
      request.headers.get('Cookie'),
      env.SESSION_SECRET,
    );
    if (!audience) {
      return Response.redirect(new URL('/gate.html', request.url), 302);
    }
  }

  // Add security headers to all responses
  const response = await next();
  const headers = new Headers(response.headers);
  headers.set('X-Frame-Options', 'DENY');
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('Referrer-Policy', 'origin-when-cross-origin');
  headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  if (url.protocol === 'https:') {
    headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains');
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
