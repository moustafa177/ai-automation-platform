/**
 * platform-charts.js — Chart.js Global Defaults (Light Theme)
 * Load AFTER chart.js CDN, BEFORE any chart initialization
 */
(function () {
  if (typeof Chart === 'undefined') return;

  const BLUE    = '#1b6ac9';
  const GREEN   = '#10b981';
  const AMBER   = '#f59e0b';
  const RED     = '#ef4444';
  const PURPLE  = '#8b5cf6';
  const CYAN    = '#06b6d4';

  /* ── Palette used for multi-dataset charts ── */
  Chart.defaults.color        = '#64748b';
  Chart.defaults.borderColor  = '#e8ecf0';

  /* ── Scales ── */
  Chart.defaults.scale = Chart.defaults.scale || {};
  Chart.defaults.scale.grid = {
    color:       'rgba(226,232,240,.8)',
    drawBorder:  false,
    lineWidth:   1,
  };
  Chart.defaults.scale.ticks = {
    color: '#94a3b8',
    font:  { size: 11, family: "'Cairo', 'Inter', sans-serif" },
    padding: 6,
  };

  /* ── Tooltip ── */
  Object.assign(Chart.defaults.plugins.tooltip, {
    backgroundColor:  '#0f172a',
    titleColor:       '#f1f5f9',
    bodyColor:        '#94a3b8',
    borderColor:      '#1e293b',
    borderWidth:      1,
    padding:          12,
    cornerRadius:     8,
    titleFont:        { family: "'Cairo','Inter',sans-serif", weight:'700', size:12 },
    bodyFont:         { family: "'Cairo','Inter',sans-serif", size:11 },
    displayColors:    true,
    boxPadding:       4,
    rtl:              true,
    textDirection:    'rtl',
  });

  /* ── Legend ── */
  Object.assign(Chart.defaults.plugins.legend.labels, {
    color:           '#64748b',
    font:            { family: "'Cairo','Inter',sans-serif", size:11 },
    padding:         18,
    usePointStyle:   true,
    pointStyleWidth: 8,
    boxHeight:       8,
  });

  /* ── Animation ── */
  Chart.defaults.responsive          = true;
  Chart.defaults.maintainAspectRatio = true;
  Chart.defaults.animation           = { duration: 700, easing: 'easeInOutQuart' };

  /* ── Default dataset colors (for convenience) ── */
  Chart.defaults.datasets = Chart.defaults.datasets || {};
  Chart.defaults.datasets.line = Chart.defaults.datasets.line || {};
  Chart.defaults.datasets.line.borderWidth = 2.5;
  Chart.defaults.datasets.line.pointRadius = 3;
  Chart.defaults.datasets.line.pointHoverRadius = 5;
  Chart.defaults.datasets.line.tension = 0.4;

  /* ── Platform color palette (accessible via window.PC) ── */
  window.PC = { BLUE, GREEN, AMBER, RED, PURPLE, CYAN,
    PALETTE: [BLUE, GREEN, AMBER, RED, PURPLE, CYAN] };
})();
