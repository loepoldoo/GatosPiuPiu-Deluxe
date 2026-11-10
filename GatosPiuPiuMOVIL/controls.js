/* ================================================================
   controls.js — Controles táctiles + ayudas PWA para GATOSPIUPIU

   IDEA CLAVE: este archivo NO toca la lógica del juego. Convierte cada
   toque en los MISMOS eventos que ya escucha game.js:
     · D-pad / botones  → KeyboardEvent  (KeyW/A/S/D, Space, KeyZ, KeyQ, KeyE, Tab, Escape)
     · FUEGO / apuntado → MouseEvent     (mousemove + mousedown/mouseup sobre el canvas)
     · Cambiar de arma  → WheelEvent     (igual que la rueda del ratón)
     · Menús            → toques en el canvas = clics de ratón
   Así el juego activa exactamente las mismas variables (keys, mouse.d, mouse.x/y…).
   ================================================================ */
(() => {
  'use strict';

  const W = 960, H = 640, K = 0.5;                 // resolución lógica y factor de inclinación del juego
  const root = document.documentElement;
  const cv = document.getElementById('c');
  const $ = id => document.getElementById(id);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const params = new URLSearchParams(location.search);
  const TOUCH = matchMedia('(pointer: coarse)').matches || params.has('touch');   // ?touch=1 para probar en PC

  /* ---------------------------------------------------------------
     1) Emisores de eventos (el "puente" hacia game.js)
     --------------------------------------------------------------- */
  const held = new Set();                           // teclas virtuales actualmente pulsadas

  function kb(type, code) {
    window.dispatchEvent(new KeyboardEvent(type, { code, key: code, bubbles: true, cancelable: true }));
  }
  function setKey(code, on) {                       // evita keydown/keyup repetidos
    if (held.has(code) === on) return;
    on ? held.add(code) : held.delete(code);
    kb(on ? 'keydown' : 'keyup', code);
  }
  function sendMouse(type, clientX, clientY) {
    cv.dispatchEvent(new MouseEvent(type, {
      clientX, clientY, button: 0, buttons: type === 'mouseup' ? 0 : 1,
      bubbles: true, cancelable: true, view: window
    }));
  }
  const toClient = (mx, my) => {                    // coordenadas del canvas (960x640) → pantalla
    const r = cv.getBoundingClientRect();
    return { x: r.left + mx * r.width / W, y: r.top + my * r.height / H };
  };
  const buzz = () => { try { navigator.vibrate && navigator.vibrate(8); } catch (e) {} };
  const inPlay = () => !!(window.GPP && window.GPP.state === 'play');

  /* ---------------------------------------------------------------
     2) Utilidad multitáctil: un "dedo" por control, por identifier
     --------------------------------------------------------------- */
  function findTouch(list, id) {
    for (let i = 0; i < list.length; i++) if (list[i].identifier === id) return list[i];
    return null;
  }
  function bind(el, h) {
    let id = null;
    el.addEventListener('touchstart', e => {
      e.preventDefault();                           // sin latencia de 300 ms ni clics fantasma
      if (id !== null) return;
      const t = e.changedTouches[0];
      id = t.identifier;
      el.classList.add('on');
      h.down && h.down(t);
    }, { passive: false });
    el.addEventListener('touchmove', e => {
      e.preventDefault();
      const t = findTouch(e.changedTouches, id);
      if (t && h.move) h.move(t);
    }, { passive: false });
    const end = e => {
      const t = findTouch(e.changedTouches, id);
      if (!t) return;
      e.preventDefault();
      id = null;
      el.classList.remove('on');
      h.up && h.up(t);
    };
    el.addEventListener('touchend', end, { passive: false });
    el.addEventListener('touchcancel', end, { passive: false });
  }

  /* ---------------------------------------------------------------
     3) D-pad → WASD
     --------------------------------------------------------------- */
  const dpad = $('dpad');
  const padKeys = { up: 'KeyW', left: 'KeyA', down: 'KeyS', right: 'KeyD' };
  const padEls = {};
  for (const d in padKeys) padEls[padKeys[d]] = dpad.querySelector('.' + d);
  let lastAngle = 0;                                // última dirección útil para apuntar

  function padSet(code, on) { setKey(code, on); padEls[code].classList.toggle('on', on); }
  function padUpdate(t) {
    const r = dpad.getBoundingClientRect();
    const dx = (t.clientX - (r.left + r.width / 2)) / (r.width / 2);
    const dy = (t.clientY - (r.top + r.height / 2)) / (r.height / 2);
    const dead = 0.26;                              // zona muerta central
    padSet('KeyA', dx < -dead);  padSet('KeyD', dx > dead);
    padSet('KeyW', dy < -dead);  padSet('KeyS', dy > dead);   // ejes independientes → diagonales
    const ax = (held.has('KeyD') ? 1 : 0) - (held.has('KeyA') ? 1 : 0);
    const ay = (held.has('KeyS') ? 1 : 0) - (held.has('KeyW') ? 1 : 0);
    if (ax || ay) lastAngle = Math.atan2(ay / K, ax);
  }
  function resetPad() { for (const c in padEls) padSet(c, false); }

  /* ---------------------------------------------------------------
     4) FUEGO: auto-apuntado al enemigo más cercano, o apuntado manual
        arrastrando el dedo desde el botón (como un stick).
     --------------------------------------------------------------- */
  const fire = { on: false, manual: false, sx: 0, sy: 0, tx: 0, ty: 0 };

  function pickAngle(g) {
    if (fire.manual) {                              // vector de pantalla → ángulo del mundo inclinado
      lastAngle = Math.atan2((fire.ty - fire.sy) / K, fire.tx - fire.sx);
      return lastAngle;
    }
    const P = g.P;
    let best = null, bd = 900;
    for (const e of g.G.en) {
      if (e.dead) continue;
      const d = Math.hypot(e.x - P.x, e.y - P.y);
      if (d < bd) { bd = d; best = e; }
    }
    if (best) lastAngle = Math.atan2(best.y - P.y, best.x - P.x);
    return lastAngle;
  }
  // Coloca el "ratón virtual" en la dirección `a` (invierte la proyección del juego)
  function aim(a, g) {
    const P = g.P, D = 260;
    const tx = P.x + Math.cos(a) * D, ty = P.y + Math.sin(a) * D;
    let my = (ty - g.cam.y) * g.K + g.H / 2 - 18;
    const ps = g.pS(my + 18);
    let mx = (tx - g.cam.x) * ps + g.W / 2;
    mx = clamp(mx, 6, W - 6); my = clamp(my, 6, H - 6);
    const c = toClient(mx, my);
    sendMouse('mousemove', c.x, c.y);
    return c;
  }
  function startFire(t) {
    const g = window.GPP;
    if (!g || !inPlay()) return;
    fire.on = true; fire.manual = false;
    fire.sx = fire.tx = t.clientX; fire.sy = fire.ty = t.clientY;
    const c = aim(pickAngle(g), g);
    sendMouse('mousedown', c.x, c.y);               // → mouse.d = 1 (disparo continuo)
    buzz();
  }
  function moveFire(t) {
    fire.tx = t.clientX; fire.ty = t.clientY;
    fire.manual = Math.hypot(fire.tx - fire.sx, fire.ty - fire.sy) > 24;
  }
  function stopFire() {
    if (!fire.on) return;
    fire.on = false; fire.manual = false;
    sendMouse('mouseup', 0, 0);                     // → mouse.d = 0
  }

  function releaseAll() {
    for (const c of [...held]) setKey(c, false);
    resetPad();
    stopFire();
  }

  /* ---------------------------------------------------------------
     5) Bucle ligero: estado del juego → CSS, apuntado continuo, avisos
     --------------------------------------------------------------- */
  const MENU = ['menu', 'sel', 'dif', 'opc', 'ctl', 'cred'];
  let lastState = null, lastSP = -1;
  const buyBtn = $('btn-buy'), skillsBtn = $('btn-skills'), badge = $('sp-badge');

  function tick() {
    const g = window.GPP;
    if (g) {
      const st = g.state;
      if (st !== lastState) {
        lastState = st;
        document.body.dataset.state = st;
        document.body.dataset.menu = MENU.includes(st) ? '1' : '0';
        if (TOUCH && st !== 'play') releaseAll();   // al abrir menús/ruleta/pausa: soltar todo
      }
      if (TOUCH && st === 'play' && g.P && g.G) {
        if (fire.on) aim(pickAngle(g), g);          // el apuntado sigue al enemigo mientras disparas
        const b = g.G.box;
        buyBtn.classList.toggle('ready', Math.hypot(g.P.x - b.x, g.P.y - b.y) < 80);
        const sp = g.P.sp | 0;
        if (sp !== lastSP) { lastSP = sp; badge.textContent = sp > 0 ? '+' + sp : ''; skillsBtn.classList.toggle('ready', sp > 0); }
      }
    }
    requestAnimationFrame(tick);
  }

  /* ---------------------------------------------------------------
     6) Instalación PWA (botón "Instalar app" en Chrome/Edge/Android)
     --------------------------------------------------------------- */
  let deferredInstall = null;
  const installBtn = $('install-btn');
  addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferredInstall = e; installBtn.hidden = false; });
  installBtn.addEventListener('click', async () => {
    if (!deferredInstall) return;
    deferredInstall.prompt();
    try { await deferredInstall.userChoice; } catch (e) {}
    deferredInstall = null; installBtn.hidden = true;
  });
  addEventListener('appinstalled', () => { installBtn.hidden = true; });

  /* ---------------------------------------------------------------
     7) Inicialización táctil
     --------------------------------------------------------------- */
  function layoutVars() {                           // para colocar la barra superior junto al canvas
    const r = cv.getBoundingClientRect(), s = root.style;
    s.setProperty('--cv-top', r.top + 'px');
    s.setProperty('--cv-h', r.height + 'px');
    s.setProperty('--cv-right', Math.max(0, innerWidth - r.right) + 'px');
  }
  function pauseIfPlaying() {
    if (inPlay()) { kb('keydown', 'Escape'); kb('keyup', 'Escape'); }
  }
  function goFullscreen() {
    if (matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches || document.fullscreenElement) return;
    const req = root.requestFullscreen || root.webkitRequestFullscreen;
    if (!req) return;                               // iPhone Safari no lo permite → instalar la PWA
    try {
      const p = req.call(root, { navigationUI: 'hide' });
      if (p && p.then) p.then(() => {
        if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => {});
      }).catch(() => {});
    } catch (e) {}
  }

  function initTouch() {
    root.classList.add('has-touch');

    // Ajustes ligeros por defecto en móvil (resolución 0.75x). game.js los lee al arrancar.
    try { if (!localStorage.getItem('gpp_s')) localStorage.setItem('gpp_s', JSON.stringify({ res: 0, part: 1 })); } catch (e) {}

    // Sin zoom por gestos, sin menú contextual, sin selección, sin scroll
    ['gesturestart', 'gesturechange', 'gestureend', 'contextmenu', 'dblclick', 'selectstart']
      .forEach(t => document.addEventListener(t, e => e.preventDefault()));
    document.addEventListener('touchmove', e => e.preventDefault(), { passive: false });

    // --- D-pad ---
    bind(dpad, { down: padUpdate, move: padUpdate, up: resetPad });

    // --- Botones con tecla asociada: tocar = keydown, soltar = keyup (igual que el teclado) ---
    document.querySelectorAll('[data-key]').forEach(el => {
      const code = el.dataset.key;
      bind(el, { down() { setKey(code, true); buzz(); }, up() { setKey(code, false); } });
    });

    // --- Cambiar de arma (equivale a la rueda del ratón) ---
    document.querySelectorAll('[data-wheel]').forEach(el => {
      const dir = +el.dataset.wheel;
      bind(el, { down() { cv.dispatchEvent(new WheelEvent('wheel', { deltaY: dir, bubbles: true, cancelable: true })); buzz(); } });
    });

    // --- FUEGO ---
    bind($('btn-fire'), { down: startFire, move: moveFire, up: stopFire });

    // --- Menús, ruleta, nivel, pausa…: un toque en el canvas = clic de ratón (también arrastrar sliders) ---
    let menuTouch = null;
    cv.addEventListener('touchstart', e => {
      e.preventDefault();
      if (inPlay() || menuTouch !== null) return;   // jugando, el canvas no recibe toques
      const t = e.changedTouches[0];
      menuTouch = t.identifier;
      sendMouse('mousemove', t.clientX, t.clientY);
      sendMouse('mousedown', t.clientX, t.clientY);
    }, { passive: false });
    cv.addEventListener('touchmove', e => {
      e.preventDefault();
      const t = findTouch(e.changedTouches, menuTouch);
      if (t) sendMouse('mousemove', t.clientX, t.clientY);
    }, { passive: false });
    const endMenu = e => {
      const t = findTouch(e.changedTouches, menuTouch);
      if (!t) return;
      e.preventDefault();
      menuTouch = null;
      sendMouse('mouseup', t.clientX, t.clientY);
    };
    cv.addEventListener('touchend', endMenu, { passive: false });
    cv.addEventListener('touchcancel', endMenu, { passive: false });

    // --- Primer toque: desbloquea audio (iOS exige touchend) y pide pantalla completa ---
    let unlocked = false;
    document.addEventListener('touchend', () => {
      if (unlocked) return;
      unlocked = true;
      kb('keydown', 'ShiftLeft'); kb('keyup', 'ShiftLeft');   // el handler de teclado del juego crea/reanuda el AudioContext
      goFullscreen();
    }, { passive: true });

    // --- Seguridad: pausa y suelta controles si cambia la orientación o se oculta la app ---
    matchMedia('(orientation: portrait)').addEventListener('change', e => { if (e.matches) { releaseAll(); pauseIfPlaying(); } });
    document.addEventListener('visibilitychange', () => { if (document.hidden) { releaseAll(); pauseIfPlaying(); } });
    addEventListener('blur', releaseAll);

    addEventListener('resize', layoutVars);
    addEventListener('orientationchange', () => setTimeout(layoutVars, 250));
    layoutVars();
  }

  if (TOUCH) initTouch();
  requestAnimationFrame(tick);
})();
