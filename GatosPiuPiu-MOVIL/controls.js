/* ================================================================
   controls.js — Controles táctiles + ayudas PWA para GATOSPIUPIU  (v2)

   · D-pad / botones  → KeyboardEvent  (KeyW/A/S/D, Space, KeyZ, KeyQ, KeyE, Tab, Escape)
   · FUEGO            → API directa GPP.touch.fire()/aim()  (ya NO usa clics de ratón falsos:
                        antes el clic caía sobre la interfaz y el disparo se "trababa" en
                        ciertos ángulos)
   · Cambiar de arma  → WheelEvent (igual que la rueda del ratón)
   · Menús / ruleta   → toques en el canvas = clics de ratón
   ================================================================ */
(() => {
  'use strict';

  const K = 0.5;                                    // inclinación de la cámara del juego
  const root = document.documentElement;
  const cv = document.getElementById('c');
  const $ = id => document.getElementById(id);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const params = new URLSearchParams(location.search);
  const TOUCH = matchMedia('(pointer: coarse)').matches || params.has('touch');   // ?touch=1 para probar en PC
  const game = () => window.GPP;
  const cfg = () => (window.GPP && window.GPP.S) || {};
  const inPlay = () => !!(window.GPP && window.GPP.state === 'play');
  const buzz = ms => { try { if (cfg().vib !== false && navigator.vibrate) navigator.vibrate(ms || 8); } catch (e) {} };

  /* ---------------------------------------------------------------
     1) Teclado virtual (el "puente" hacia game.js)
     --------------------------------------------------------------- */
  const held = new Set();
  function kb(type, code) {
    window.dispatchEvent(new KeyboardEvent(type, { code, key: code, bubbles: true, cancelable: true }));
  }
  function setKey(code, on) {
    if (held.has(code) === on) return;
    on ? held.add(code) : held.delete(code);
    kb(on ? 'keydown' : 'keyup', code);
  }
  function sendMouse(type, clientX, clientY) {       // solo para MENÚS
    cv.dispatchEvent(new MouseEvent(type, {
      clientX, clientY, button: 0, buttons: type === 'mouseup' ? 0 : 1,
      bubbles: true, cancelable: true, view: window
    }));
  }

  /* ---------------------------------------------------------------
     2) Multitáctil: un "dedo" por control + limpieza global
     --------------------------------------------------------------- */
  const controls = [];
  function findTouch(list, id) {
    for (let i = 0; i < list.length; i++) if (list[i].identifier === id) return list[i];
    return null;
  }
  function release(c, t) {
    if (c.id === null) return;
    c.id = null;
    c.el.classList.remove('on');
    if (c.h.up) c.h.up(t);
  }
  function bind(el, h) {
    const c = { el, h, id: null };
    controls.push(c);
    el.addEventListener('touchstart', e => {
      e.preventDefault();                           // sin retardo de 300 ms ni clics fantasma
      if (c.id !== null) return;
      const t = e.changedTouches[0];
      c.id = t.identifier;
      el.classList.add('on');
      if (h.down) h.down(t);
    }, { passive: false });
    el.addEventListener('touchmove', e => {
      e.preventDefault();
      const t = findTouch(e.changedTouches, c.id);
      if (t && h.move) h.move(t);
    }, { passive: false });
    const end = e => {
      const t = findTouch(e.changedTouches, c.id);
      if (!t) return;
      e.preventDefault();
      release(c, t);
    };
    el.addEventListener('touchend', end, { passive: false });
    el.addEventListener('touchcancel', end, { passive: false });
  }
  // Red de seguridad: si un dedo desaparece sin que el control reciba touchend
  // (gesto del sistema, cambio de estado, etc.) se suelta el control igualmente.
  const reconcile = e => {
    const live = new Set();
    for (let i = 0; i < e.touches.length; i++) live.add(e.touches[i].identifier);
    for (const c of controls) if (c.id !== null && !live.has(c.id)) release(c);
  };
  function releaseAll() { for (const c of controls) release(c); for (const k of [...held]) setKey(k, false); stopFire(); }

  /* ---------------------------------------------------------------
     3) D-pad → WASD
     --------------------------------------------------------------- */
  const dpad = $('dpad');
  const padKeys = { up: 'KeyW', left: 'KeyA', down: 'KeyS', right: 'KeyD' };
  const padEls = {};
  for (const d in padKeys) padEls[padKeys[d]] = dpad.querySelector('.' + d);
  let lastAngle = 0;                                // última dirección útil (en coordenadas del MUNDO)

  function padSet(code, on) { setKey(code, on); padEls[code].classList.toggle('on', on); }
  function padUpdate(t) {
    const r = dpad.getBoundingClientRect();
    const dx = (t.clientX - (r.left + r.width / 2)) / (r.width / 2);
    const dy = (t.clientY - (r.top + r.height / 2)) / (r.height / 2);
    const dead = 0.26;
    padSet('KeyA', dx < -dead);  padSet('KeyD', dx > dead);
    padSet('KeyW', dy < -dead);  padSet('KeyS', dy > dead);        // ejes independientes → diagonales
    const ax = (held.has('KeyD') ? 1 : 0) - (held.has('KeyA') ? 1 : 0);
    const ay = (held.has('KeyS') ? 1 : 0) - (held.has('KeyW') ? 1 : 0);
    if (ax || ay) lastAngle = Math.atan2(ay, ax);
  }
  function resetPad() { for (const c in padEls) padSet(c, false); }

  /* ---------------------------------------------------------------
     4) FUEGO: auto-apuntado (experimental, se puede apagar en Opciones › Táctil)
        o apuntado manual arrastrando el dedo desde el botón.
     --------------------------------------------------------------- */
  const fire = { on: false, manual: false, sx: 0, sy: 0, tx: 0, ty: 0 };
  let tgt = null;                                   // objetivo "pegajoso" (evita saltar entre enemigos)

  function nearest(g) {
    const P = g.P, en = g.G && g.G.en;
    if (!P || !en) return null;
    const d = e => Math.hypot(e.x - P.x, e.y - P.y);
    if (tgt && !tgt.dead && en.includes(tgt) && d(tgt) < 1000) {
      let best = null, bd = d(tgt) * 0.75;          // cambia solo si otro está claramente más cerca
      for (const e of en) if (!e.dead && e !== tgt && isFinite(e.x)) { const q = d(e); if (q < bd) { bd = q; best = e; } }
      if (best) tgt = best;
      return tgt;
    }
    let best = null, bd = 1000;
    for (const e of en) if (!e.dead && isFinite(e.x) && isFinite(e.y)) { const q = d(e); if (q < bd) { bd = q; best = e; } }
    return (tgt = best);
  }
  function aimAngle() {
    const g = game();
    if (!g || !g.P) return lastAngle;
    if (fire.manual) {                              // vector de pantalla → ángulo del mundo inclinado
      lastAngle = Math.atan2((fire.ty - fire.sy) / K, fire.tx - fire.sx);
      return lastAngle;
    }
    if (g.S.auto !== false) {
      const e = nearest(g);
      if (e) lastAngle = Math.atan2(e.y - g.P.y, e.x - g.P.x);
    }
    return lastAngle;
  }
  function startFire(t) {
    const g = game();
    if (!g || !inPlay()) return;
    fire.on = true; fire.manual = false;
    fire.sx = fire.tx = t.clientX; fire.sy = fire.ty = t.clientY;
    g.touch.aim(aimAngle());
    g.touch.fire(true);
    buzz(10);
  }
  function moveFire(t) {
    fire.tx = t.clientX; fire.ty = t.clientY;
    fire.manual = Math.hypot(fire.tx - fire.sx, fire.ty - fire.sy) > 22;
  }
  function stopFire() {
    if (!fire.on) return;
    fire.on = false; fire.manual = false;
    const g = game();
    if (g) { g.touch.fire(false); g.touch.aim(null); }
  }
  // Para Z / Q / HAB: apunta un instante hacia el objetivo (la katana usa la dirección del apuntado)
  let pulseT = 0;
  function aimPulse() {
    const g = game();
    if (!g || !inPlay()) return;
    g.touch.aim(aimAngle());
    clearTimeout(pulseT);
    pulseT = setTimeout(() => { if (!fire.on && game()) game().touch.aim(null); }, 450);
  }

  /* ---------------------------------------------------------------
     5) Bucle ligero: estado del juego → CSS, apuntado continuo
     --------------------------------------------------------------- */
  const MENU = ['menu', 'sel', 'dif', 'opc', 'ctl', 'cred'];
  let lastState = null, lastSP = -1, cfgApplied = false;
  const buyBtn = $('btn-buy'), skillsBtn = $('btn-skills'), badge = $('sp-badge');

  function applySettings() {
    const s = cfg();
    root.style.setProperty('--ui', [0.82, 1, 1.2][s.csize == null ? 1 : s.csize] || 1);
    root.style.setProperty('--ui-op', (0.25 + 0.75 * (s.copa == null ? 0.5 : s.copa)).toFixed(2));
    layoutVars();
  }
  addEventListener('gpp-settings', applySettings);

  function tick() {
    const g = game();
    if (g) {
      if (!cfgApplied && g.S) { cfgApplied = true; applySettings(); }
      const st = g.state;
      if (st !== lastState) {
        lastState = st;
        document.body.dataset.state = st;
        document.body.dataset.menu = MENU.includes(st) ? '1' : '0';
      }
      if (TOUCH) {
        if (fire.on) {                              // el dedo sigue en FUEGO
          if (st === 'play') { g.touch.aim(aimAngle()); g.touch.fire(true); }
          else { g.touch.fire(false); g.touch.aim(null); }        // pausa/ruleta/nivel: no dispara
        }
        if (st === 'play' && g.P && g.G && g.G.box) {
          const b = g.G.box;
          buyBtn.classList.toggle('ready', Math.hypot(g.P.x - b.x, g.P.y - b.y) < 80);
          const sp = g.P.sp | 0;
          if (sp !== lastSP) { lastSP = sp; badge.textContent = sp > 0 ? '+' + sp : ''; skillsBtn.classList.toggle('ready', sp > 0); }
        }
      }
    }
    requestAnimationFrame(tick);
  }

  /* ---------------------------------------------------------------
     6) Instalación PWA + avisos según plataforma
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

  (function platformHint() {
    const ua = navigator.userAgent || '';
    const isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    const standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
    const inApp = (isIOS && !/Safari|CriOS|FxiOS|EdgiOS/.test(ua)) || /; wv\)|FBAN|FBAV|Instagram|MicroMessenger|Snapchat|TikTok|Line\//.test(ua);
    const el = $('hint');
    if (!el || standalone || !TOUCH) return;
    let msg = '';
    if (inApp) msg = 'Estás en el navegador de otra app (WhatsApp, Instagram…). Ábrelo en Safari o Chrome para instalarlo y jugar mejor.';
    else if (isIOS) msg = 'Para instalarlo: toca Compartir ⬆ y luego «Agregar a Inicio».';
    if (!msg) return;
    let n = 0;
    try { n = +localStorage.getItem('gpp_hint') || 0; } catch (e) {}
    if (n >= 4 && !inApp) return;
    try { localStorage.setItem('gpp_hint', String(n + 1)); } catch (e) {}
    el.querySelector('span').textContent = msg;
    el.hidden = false;
    el.addEventListener('click', () => { el.hidden = true; });
    setTimeout(() => { el.hidden = true; }, 15000);
  })();

  /* ---------------------------------------------------------------
     7) Inicialización táctil
     --------------------------------------------------------------- */
  function layoutVars() {
    const r = cv.getBoundingClientRect(), s = root.style;
    s.setProperty('--cv-top', r.top + 'px');
    s.setProperty('--cv-h', r.height + 'px');
    s.setProperty('--cv-right', Math.max(0, innerWidth - r.right) + 'px');
  }
  function pauseIfPlaying() {
    if (inPlay()) { kb('keydown', 'Escape'); kb('keyup', 'Escape'); }
  }

  function initTouch() {
    root.classList.add('has-touch');

    // Sin zoom por gestos, sin menú contextual, sin selección, sin scroll
    ['gesturestart', 'gesturechange', 'gestureend', 'contextmenu', 'dblclick', 'selectstart']
      .forEach(t => document.addEventListener(t, e => e.preventDefault()));
    document.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
    document.addEventListener('touchend', reconcile, { capture: true, passive: true });
    document.addEventListener('touchcancel', reconcile, { capture: true, passive: true });

    // --- D-pad ---
    bind(dpad, { down: padUpdate, move: padUpdate, up: resetPad });

    // --- Botones con tecla asociada ---
    document.querySelectorAll('[data-key]').forEach(el => {
      const code = el.dataset.key;
      bind(el, {
        down() { if (code === 'KeyZ' || code === 'KeyQ' || code === 'Space') aimPulse(); setKey(code, true); buzz(); },
        up() { setKey(code, false); }
      });
    });

    // --- Cambiar de arma (equivale a la rueda del ratón) ---
    document.querySelectorAll('[data-wheel]').forEach(el => {
      const dir = +el.dataset.wheel;
      bind(el, { down() { cv.dispatchEvent(new WheelEvent('wheel', { deltaY: dir, bubbles: true, cancelable: true })); buzz(); } });
    });

    // --- FUEGO ---
    bind($('btn-fire'), { down: startFire, move: moveFire, up: stopFire });

    // --- Menús, ruleta, nivel, pausa…: un toque en el canvas = clic (también arrastrar sliders) ---
    let menuTouch = null;
    cv.addEventListener('touchstart', e => {
      e.preventDefault();
      if (inPlay() || menuTouch !== null) return;
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

    // --- Primer toque: desbloquea el audio (iOS exige touchend). La pantalla completa la gestiona game.js ---
    let unlocked = false;
    document.addEventListener('touchend', () => {
      if (unlocked) return;
      unlocked = true;
      kb('keydown', 'ShiftLeft'); kb('keyup', 'ShiftLeft');
    }, { passive: true });

    // --- Seguridad: suelta todo y pausa si cambia la orientación o se oculta la app ---
    matchMedia('(orientation: portrait)').addEventListener('change', e => { if (e.matches) { releaseAll(); pauseIfPlaying(); } });
    document.addEventListener('visibilitychange', () => { if (document.hidden) { releaseAll(); pauseIfPlaying(); } });
    addEventListener('pagehide', releaseAll);
    addEventListener('blur', releaseAll);

    addEventListener('resize', layoutVars);
    addEventListener('orientationchange', () => setTimeout(layoutVars, 250));
    layoutVars();
  }

  // Actualización silenciosa: si hay una versión nueva y estás en el menú, recarga sola
  if ('serviceWorker' in navigator) {
    let had = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (had && game() && MENU.includes(game().state)) location.reload();
      had = true;
    });
  }

  if (TOUCH) initTouch();
  requestAnimationFrame(tick);
})();
