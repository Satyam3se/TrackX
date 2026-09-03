import { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const MAP_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
    },
  },
  layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
};

/* ------------------------------------------------------------------ */
/*  GeoJSON helpers                                                     */
/* ------------------------------------------------------------------ */

function lineCollection(trajectory) {
  const lineFeat = trajectory?.features?.find(
    (f) => f.geometry?.type === 'LineString',
  );
  return { type: 'FeatureCollection', features: lineFeat ? [lineFeat] : [] };
}

function waypointCollection(trajectory) {
  return {
    type: 'FeatureCollection',
    features: (trajectory?.features ?? []).filter(
      (f) => f.geometry?.type === 'Point',
    ),
  };
}

function showPopup(map, lngLat, html) {
  new maplibregl.Popup({ closeButton: true, maxWidth: '280px' })
    .setLngLat(lngLat)
    .setHTML(html)
    .addTo(map);
}

/* ------------------------------------------------------------------ */
/*  Component                                                           */
/* ------------------------------------------------------------------ */

export default function SurveillanceMap({
  trajectory = null,
  cameras = null,
  pinnedAlert = null,
  onMapReady,
}) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);

  /* ==================== Init map once ==================== */
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: [77.2090, 28.6139], // Delhi [lng, lat]
      zoom: 12,
      pitch: 45,
      attributionControl: false,
    });

    map.addControl(
      new maplibregl.NavigationControl({ showCompass: true }),
      'top-right',
    );
    map.addControl(
      new maplibregl.AttributionControl({ compact: true }),
      'bottom-right',
    );

    map.on('load', () => {
      /* --- Trajectory line --- */
      map.addSource('trajectory-line', {
        type: 'geojson',
        data: lineCollection(null),
      });

      // Glow layer (wide, transparent)
      map.addLayer({
        id: 'trajectory-glow',
        type: 'line',
        source: 'trajectory-line',
        paint: {
          'line-color': '#00E5FF',
          'line-width': 10,
          'line-opacity': 0.2,
          'line-blur': 5,
        },
      });

      // Main trajectory line
      map.addLayer({
        id: 'trajectory-line',
        type: 'line',
        source: 'trajectory-line',
        paint: {
          'line-color': '#00E5FF',
          'line-width': 4,
          'line-opacity': 0.9,
        },
      });

      /* --- Waypoint circles (detection hits) --- */
      map.addSource('waypoints', {
        type: 'geojson',
        data: waypointCollection(null),
      });

      map.addLayer({
        id: 'waypoint-dots',
        type: 'circle',
        source: 'waypoints',
        paint: {
          'circle-radius': 7,
          'circle-color': '#00E5FF',
          'circle-stroke-color': '#0b0f19',
          'circle-stroke-width': 2,
          'circle-opacity': 0.95,
        },
      });

      /* --- Camera node markers --- */
      map.addSource('camera-nodes', {
        type: 'geojson',
        data: cameras ?? { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'camera-dots',
        type: 'circle',
        source: 'camera-nodes',
        paint: {
          'circle-radius': 6,
          'circle-color': [
            'case',
            ['boolean', ['get', 'is_active'], false],
            '#00e676',
            '#546e7a',
          ],
          'circle-stroke-color': '#0b0f19',
          'circle-stroke-width': 2,
        },
      });

      /* --- Click handlers for popups --- */
      map.on('click', 'waypoint-dots', (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties;
        showPopup(
          map,
          e.lngLat,
          `<div style="font:500 13px/1.35 Inter,sans-serif;color:#e1e5ee">
            <div style="color:#00E5FF;font-weight:700;margin-bottom:4px">${p.camera_id ?? ''}</div>
            <div style="font-size:12px;opacity:.75">${p.location_name ?? ''}</div>
            <div style="font-size:11px;opacity:.6;margin-top:4px">${p.timestamp ?? ''}</div>
            ${p.confidence_score != null ? `<div style="margin-top:3px;font-size:11px;opacity:.6">OCR ${Math.round(p.confidence_score)}%</div>` : ''}
            ${p.segment_speed_kmh != null ? `<div style="font-size:11px;color:#ffab00;margin-top:2px">Segment avg ${p.segment_speed_kmh} km/h</div>` : ''}
          </div>`,
        );
      });

      map.on('click', 'camera-dots', (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties;
        const isActive =
          p.is_active === true || p.is_active === 'true';
        showPopup(
          map,
          e.lngLat,
          `<div style="font:500 13px/1.35 Inter,sans-serif;color:#e1e5ee">
            <div style="color:#00e676;font-weight:700;margin-bottom:4px">${p.camera_id ?? ''}</div>
            <div style="font-size:12px;opacity:.75">${p.location_name ?? ''}</div>
            <div style="font-size:11px;opacity:.6;margin-top:3px">${isActive ? 'Active' : 'Inactive'}</div>
          </div>`,
        );
      });

      ['waypoint-dots', 'camera-dots'].forEach((layer) => {
        map.on('mouseenter', layer, () => {
          map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', layer, () => {
          map.getCanvas().style.cursor = '';
        });
      });

      onMapReady?.(map);
    });

    mapRef.current = map;

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /* ==================== Update trajectory data ==================== */
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const lineSrc = map.getSource('trajectory-line');
    if (lineSrc) lineSrc.setData(lineCollection(trajectory));

    const wpSrc = map.getSource('waypoints');
    if (wpSrc) wpSrc.setData(waypointCollection(trajectory));

    /* Auto-fit bounds to trajectory waypoints */
    if (trajectory?.features?.length) {
      const coords = [];
      for (const feat of trajectory.features) {
        if (feat.geometry?.type === 'Point') {
          coords.push(feat.geometry.coordinates);
        } else if (feat.geometry?.type === 'LineString') {
          coords.push(...feat.geometry.coordinates);
        }
      }
      if (coords.length >= 2) {
        const lons = coords.map((c) => c[0]);
        const lats = coords.map((c) => c[1]);
        map.fitBounds(
          [
            [Math.min(...lons), Math.min(...lats)],
            [Math.max(...lons), Math.max(...lats)],
          ],
          { padding: 60, duration: 800 },
        );
      }
    }
  }, [trajectory]);

  /* ==================== Update camera nodes ==================== */
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    const src = map.getSource('camera-nodes');
    if (src) src.setData(cameras ?? { type: 'FeatureCollection', features: [] });
  }, [cameras]);

  /* ==================== Fly-to pinned alert ==================== */
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !pinnedAlert?.coordinates) return;
    map.flyTo({
      center: pinnedAlert.coordinates,
      zoom: 16,
      pitch: 60,
      duration: 1200,
    });
  }, [pinnedAlert]);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: '100%' }}
    />
  );
}