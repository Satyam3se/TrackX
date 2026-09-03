/* global L */
(function () {
  "use strict";

  const DATA = window.TRACKX || {};
  const trajectory = DATA.trajectory || [];
  const heatPoints = DATA.heatmap || [];
  const cameras = DATA.cameras || [];

  // -------------------------------------------------------------------
  // System clock
  // -------------------------------------------------------------------
  const clockEl = document.getElementById("clock");
  function tick() {
    if (!clockEl) return;
    const now = new Date();
    const ist = new Date(now.getTime() + (now.getTimezoneOffset() + 330) * 60000);
    const utc = new Date(now.getTime() + now.getTimezoneOffset() * 60000);
    const fmt = (d) =>
      d.getHours().toString().padStart(2, "0") + ":" +
      d.getMinutes().toString().padStart(2, "0") + ":" +
      d.getSeconds().toString().padStart(2, "0");
    clockEl.innerHTML =
      '<b>' + fmt(ist) + '</b> IST<br><span class="dim">' + fmt(utc) + " UTC</span>";
  }
  tick();
  setInterval(tick, 1000);

  // -------------------------------------------------------------------
  // Alarm mute toggle
  // -------------------------------------------------------------------
  const alarmBtn = document.getElementById("alarm-toggle");
  if (alarmBtn) {
    alarmBtn.addEventListener("click", () => alarmBtn.classList.toggle("active"));
  }

  // -------------------------------------------------------------------
  // Radial gauges (SVG)
  // -------------------------------------------------------------------
  function drawGauge(el) {
    const pct = Math.max(0, Math.min(100, parseFloat(el.dataset.pct)));
    const color = el.dataset.color;
    const R = 30, C = 2 * Math.PI * R, off = C * (1 - pct / 100);
    el.innerHTML =
      '<svg width="72" height="72" viewBox="0 0 72 72">' +
      '<circle cx="36" cy="36" r="' + R + '" fill="none" stroke="#1f2937" stroke-width="6"/>' +
      '<circle cx="36" cy="36" r="' + R + '" fill="none" stroke="' + color + '" stroke-width="6" ' +
      'stroke-linecap="round" stroke-dasharray="' + C + '" stroke-dashoffset="' + C + '" ' +
      'transform="rotate(-90 36 36)" style="transition:stroke-dashoffset 1s ease"/>' +
      '</svg>';
    const arc = el.querySelector("circle:last-child");
    requestAnimationFrame(() => { arc.style.strokeDashoffset = off; });
  }
  document.querySelectorAll("[data-gauge]").forEach(drawGauge);

  // -------------------------------------------------------------------
  // Leaflet map
  // -------------------------------------------------------------------
  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined" || trajectory.length === 0) return;

  const map = L.map("map", { zoomControl: true, attributionControl: true })
    .setView([28.665, 77.22], 12);

  // Keyless dark basemap: standard OSM raster tiles rendered dark via a CSS
  // filter (see .trackx-dark-tiles in dashboard.css). No API key required.
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    className: "trackx-dark-tiles",
    attribution: "&copy; OpenStreetMap contributors — TrackX GIS Surveillance Grid",
  }).addTo(map);

  // --- Ambient camera nodes (emerald) ---
  const camLayer = L.layerGroup().addTo(map);
  cameras.forEach((c) => {
    L.marker([c.lat, c.lng], {
      icon: L.divIcon({ className: "", html: '<div class="cam-ambient"></div>', iconSize: [9, 9] }),
    })
      .bindTooltip(c.id + " · ONLINE", { direction: "top" })
      .addTo(camLayer);
  });

  // --- Heatmap layer (toggleable, built from circles) ---
  const heatLayer = L.layerGroup();
  heatPoints.forEach((p) => {
    const w = p[2];
    const color = w > 0.7 ? "#ff1744" : w > 0.45 ? "#ffab00" : "#00e676";
    L.circle([p[0], p[1]], {
      radius: 260 + w * 340,
      color: color,
      fillColor: color,
      fillOpacity: 0.18 + w * 0.22,
      weight: 0,
    }).addTo(heatLayer);
  });

  // --- Trajectory polyline (neon blue) ---
  const path = trajectory.map((n) => [n.lat, n.lng]);
  // glow underlay
  L.polyline(path, { color: "#00e5ff", weight: 9, opacity: 0.18 }).addTo(map);
  const line = L.polyline(path, {
    color: "#00e5ff",
    weight: 3,
    opacity: 0.95,
    dashArray: "1 8",
    lineCap: "round",
  }).addTo(map);

  // Animate the dash to simulate flow direction.
  let dashOffset = 0;
  setInterval(() => {
    dashOffset = (dashOffset - 1) % 18;
    const el = line.getElement();
    if (el) el.style.strokeDashoffset = dashOffset;
  }, 60);

  // Directional arrow decorations at each segment midpoint.
  for (let i = 1; i < trajectory.length; i++) {
    const a = trajectory[i - 1], b = trajectory[i];
    const midLat = (a.lat + b.lat) / 2, midLng = (a.lng + b.lng) / 2;
    const ang = (Math.atan2(b.lat - a.lat, b.lng - a.lng) * 180) / Math.PI;
    L.marker([midLat, midLng], {
      icon: L.divIcon({
        className: "",
        html:
          '<div style="color:#00e5ff;transform:rotate(' + -ang + 'deg);' +
          'font-size:14px;text-shadow:0 0 8px rgba(0,229,255,0.8)">&#10148;</div>',
        iconSize: [14, 14],
      }),
      interactive: false,
    }).addTo(map);
  }

  // --- Numbered trajectory camera nodes with popovers ---
  trajectory.forEach((n) => {
    const last = n.status === "LAST SEEN";
    const marker = L.marker([n.lat, n.lng], {
      icon: L.divIcon({
        className: "",
        html: '<div class="cam-node ' + (last ? "last" : "") + '">' + n.id + "</div>",
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      }),
      zIndexOffset: 1000,
    }).addTo(map);

    const html =
      '<div class="node-popup">' +
        '<div class="np-cam">' +
          '<div class="np-scan"></div>' +
          '<div class="np-live"><span class="dot"></span>LIVE</div>' +
          '<div class="np-plate">' + (DATA.plate || "UP 14 AB 1234") + "</div>" +
        "</div>" +
        '<div class="np-body">' +
          '<div class="np-name">' + n.name + "</div>" +
          '<div class="np-row"><span class="dim">Timestamp</span><span>' + n.time + " IST</span></div>" +
          '<div class="np-row"><span class="dim">OCR match</span><span style="color:#00e676">' + n.confidence + "%</span></div>" +
          '<div class="np-row"><span class="dim">Speed</span><span>' + n.speed + " km/h · " + n.heading + "</span></div>" +
          '<div class="np-row"><span class="dim">Status</span><span style="color:' + (last ? "#ff1744" : "#00e5ff") + '">' + n.status + "</span></div>" +
        "</div>" +
      "</div>";
    marker.bindPopup(html, { maxWidth: 240, minWidth: 210, className: "trackx-popup" });
  });

  map.fitBounds(line.getBounds(), { padding: [70, 70] });

  // -------------------------------------------------------------------
  // Map toggles
  // -------------------------------------------------------------------
  const heatToggle = document.getElementById("toggle-heat");
  if (heatToggle) {
    heatToggle.addEventListener("click", () => {
      const on = heatToggle.classList.toggle("on");
      if (on) heatLayer.addTo(map);
      else map.removeLayer(heatLayer);
    });
  }
  const camToggle = document.getElementById("toggle-cams");
  if (camToggle) {
    camToggle.addEventListener("click", () => {
      const on = camToggle.classList.toggle("on");
      if (on) camLayer.addTo(map);
      else map.removeLayer(camLayer);
    });
  }
})();
