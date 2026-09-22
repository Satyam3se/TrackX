import express from 'express';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import { WebSocketServer, WebSocket } from 'ws';
import { createServer as createViteServer } from 'vite';
import {
  PRESET_SURVEILLANCE_FRAMES,
  currentModelConfig,
  updateModelConfig,
  validateAndCleanPlate,
  analyzeVehicleWithGemini,
  getModelBenchmarkStats,
  INDIAN_STATES_RTO,
} from './server/anpr_engine.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const server = http.createServer(app);

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// CORS & Preflight middleware for cross-origin and iframe compatibility
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }
  next();
});

// ---------------------------------------------------------------------------
// In-Memory TrackX Surveillance Data Store
// ---------------------------------------------------------------------------

interface Camera {
  id: number;
  camera_id: string;
  location_name: string;
  lon: number;
  lat: number;
  is_active: boolean;
}

const CAMERAS: Camera[] = [
  { id: 1, camera_id: 'CAM-042', location_name: 'Ring Rd / ITO Junction', lon: 77.2410, lat: 28.6289, is_active: true },
  { id: 2, camera_id: 'CAM-118', location_name: 'Rajghat Flyover', lon: 77.2498, lat: 28.6412, is_active: true },
  { id: 3, camera_id: 'CAM-233', location_name: 'Kashmere Gate ISBT', lon: 77.2295, lat: 28.6673, is_active: true },
  { id: 4, camera_id: 'CAM-501', location_name: 'GT Karnal Road', lon: 77.2011, lat: 28.6905, is_active: true },
  { id: 5, camera_id: 'CAM-612', location_name: 'Azadpur Mandi', lon: 77.1758, lat: 28.7078, is_active: true },
  { id: 6, camera_id: 'CAM-144', location_name: 'Rajouri Garden', lon: 77.2500, lat: 28.6820, is_active: true },
  { id: 7, camera_id: 'CAM-091', location_name: 'Connaught Place', lon: 77.2250, lat: 28.6150, is_active: true },
];

let blacklistedVehicles = [
  {
    id: 1,
    license_plate: 'DL 3C AF 9021',
    owner_name: 'Arjun Mehta',
    reason: 'Reported stolen vehicle; involved in hit and run',
    alert_level: 'CRITICAL',
    flagged_at: new Date(Date.now() - 3600000 * 24).toISOString(),
    is_active: true,
  },
  {
    id: 2,
    license_plate: 'HR 26 DQ 4412',
    owner_name: 'Ravi Khanna',
    reason: 'Repeat traffic violations in a restricted zone',
    alert_level: 'WARNING',
    flagged_at: new Date(Date.now() - 3600000 * 18).toISOString(),
    is_active: true,
  },
  {
    id: 3,
    license_plate: 'UP 14 AB 1234',
    owner_name: 'Vikram Malhotra',
    reason: 'Suspicious perimeter looping detected',
    alert_level: 'WARNING',
    flagged_at: new Date(Date.now() - 3600000 * 8).toISOString(),
    is_active: true,
  },
];

interface DetectionRecord {
  id: number;
  camera_id: string;
  location_name: string;
  lon: number;
  lat: number;
  license_plate: string;
  confidence_score: number;
  speed_estimate: number;
  captured_at: Date;
  video_feed_id?: number;
}

const detectionsStore: DetectionRecord[] = [];
let nextDetectionId = 1;

// Seed initial detections for the hotlisted & common plates
const now = Date.now();
const HOTLIST_ROUTES: Array<{ plate: string; camIndices: number[]; baseSpeed: number }> = [
  { plate: 'DL 3C AF 9021', camIndices: [0, 1, 2, 3, 4], baseSpeed: 46 },
  { plate: 'HR 26 DQ 4412', camIndices: [1, 2, 3, 4, 5], baseSpeed: 52 },
  { plate: 'UP 14 AB 1234', camIndices: [6, 0, 1, 2], baseSpeed: 38 },
  { plate: 'DL 8C X 4412', camIndices: [4, 3, 2], baseSpeed: 64 },
  { plate: 'DL 1C J 7788', camIndices: [2, 1, 0], baseSpeed: 41 },
];

HOTLIST_ROUTES.forEach(({ plate, camIndices, baseSpeed }) => {
  camIndices.forEach((idx, step) => {
    const cam = CAMERAS[idx];
    detectionsStore.push({
      id: nextDetectionId++,
      camera_id: cam.camera_id,
      location_name: cam.location_name,
      lon: cam.lon,
      lat: cam.lat,
      license_plate: plate,
      confidence_score: Number((0.92 + step * 0.015).toFixed(2)),
      speed_estimate: Math.round(baseSpeed + (step * 7) % 25),
      captured_at: new Date(now - (camIndices.length - step) * 7 * 60000),
    });
  });
});

// Seed detections specifically for Video Feed 1 (Ring Rd / ITO North Corridor Feed)
detectionsStore.push(
  {
    id: nextDetectionId++,
    camera_id: 'CAM-042',
    location_name: 'Ring Rd / ITO Junction',
    lon: 77.2410,
    lat: 28.6289,
    license_plate: 'DL 3C AF 9021',
    confidence_score: 0.98,
    speed_estimate: 54,
    captured_at: new Date(now - 15 * 60000),
    video_feed_id: 1,
  },
  {
    id: nextDetectionId++,
    camera_id: 'CAM-042',
    location_name: 'Ring Rd / ITO Junction',
    lon: 77.2410,
    lat: 28.6289,
    license_plate: 'HR 26 DQ 4412',
    confidence_score: 0.95,
    speed_estimate: 42,
    captured_at: new Date(now - 11 * 60000),
    video_feed_id: 1,
  },
  {
    id: nextDetectionId++,
    camera_id: 'CAM-042',
    location_name: 'Ring Rd / ITO Junction',
    lon: 77.2410,
    lat: 28.6289,
    license_plate: 'UP 14 AB 1234',
    confidence_score: 0.91,
    speed_estimate: 49,
    captured_at: new Date(now - 4 * 60000),
    video_feed_id: 1,
  }
);

let videoFeeds = [
  {
    id: 1,
    camera: 1,
    camera_id: 'CAM-042',
    location_name: 'Ring Rd / ITO Junction',
    title: 'Ring Rd / ITO North Corridor Feed',
    video_file: '/sample_feed.mp4',
    video_url: '/sample_feed.mp4',
    uploaded_at: new Date(now - 3600000 * 5).toISOString(),
    processed: true,
  },
  {
    id: 2,
    camera: 3,
    camera_id: 'CAM-233',
    location_name: 'Kashmere Gate ISBT',
    title: 'Kashmere Gate Bus Ingress Cam 02',
    video_file: '/sample_isbt.mp4',
    video_url: '/sample_isbt.mp4',
    uploaded_at: new Date(now - 3600000 * 2).toISOString(),
    processed: false,
  },
];

function haversineKm(lon1: number, lat1: number, lon2: number, lat2: number): number {
  const radiusKm = 6371.0;
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(deltaPhi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) ** 2;
  return 2 * radiusKm * Math.asin(Math.sqrt(a));
}

// ---------------------------------------------------------------------------
// REST API Routes
// ---------------------------------------------------------------------------

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'TrackX Surveillance Backend' });
});

// Camera nodes as GeoJSON FeatureCollection
app.get('/api/v1/cameras/', (req, res) => {
  const features = CAMERAS.map((cam) => ({
    id: cam.id,
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [cam.lon, cam.lat],
    },
    properties: {
      id: cam.id,
      camera_id: cam.camera_id,
      location_name: cam.location_name,
      is_active: cam.is_active,
      created_at: '2026-01-01T00:00:00Z',
    },
  }));
  res.json({ type: 'FeatureCollection', features });
});

// Analytics summary
app.get('/api/v1/analytics/summary/', (req, res) => {
  const activeCameras = CAMERAS.filter((c) => c.is_active).length;
  const totalSpeeds = detectionsStore.reduce((acc, d) => acc + d.speed_estimate, 0);
  const avgSpeed = detectionsStore.length ? Number((totalSpeeds / detectionsStore.length).toFixed(1)) : 46.8;

  res.json({
    total_cameras: CAMERAS.length,
    active_cameras: activeCameras,
    detections_today: 1420 + detectionsStore.length,
    active_blacklisted_count: blacklistedVehicles.filter((v) => v.is_active).length,
    avg_speed_kmh: avgSpeed,
  });
});

// Detections GeoJSON for Heatmap
app.get('/api/v1/analytics/detections-geojson/', (req, res) => {
  const features = detectionsStore.map((d) => ({
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [d.lon, d.lat],
    },
    properties: {
      plate: d.license_plate,
      timestamp: d.captured_at.toISOString(),
      weight: 1.0,
    },
  }));
  res.json({ type: 'FeatureCollection', features });
});

// Vehicle Trajectory
app.get('/api/v1/trajectory/:license_plate', (req, res) => {
  const plateQuery = req.params.license_plate.trim().toUpperCase();
  const logs = detectionsStore
    .filter((d) => d.license_plate.toUpperCase().replace(/\s+/g, '') === plateQuery.replace(/\s+/g, ''))
    .sort((a, b) => a.captured_at.getTime() - b.captured_at.getTime());

  if (!logs.length) {
    // If not found in store, generate a plausible route for demo query if desired, or return 404
    return res.status(404).json({
      type: 'FeatureCollection',
      license_plate: req.params.license_plate,
      total_hits: 0,
      time_span: null,
      features: [],
    });
  }

  const lineCoords: number[][] = [];
  const waypointFeatures: any[] = [];
  let prevLog: DetectionRecord | null = null;

  logs.forEach((log) => {
    lineCoords.push([log.lon, log.lat]);
    let segmentSpeed: number | null = null;

    if (prevLog) {
      const dKm = haversineKm(prevLog.lon, prevLog.lat, log.lon, log.lat);
      const dtHours = (log.captured_at.getTime() - prevLog.captured_at.getTime()) / 3600000;
      if (dtHours > 0) {
        segmentSpeed = Number((dKm / dtHours).toFixed(1));
      }
    }

    waypointFeatures.push({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [log.lon, log.lat],
      },
      properties: {
        id: log.id,
        timestamp: log.captured_at.toISOString(),
        camera_id: log.camera_id,
        location_name: log.location_name,
        license_plate: log.license_plate,
        confidence_score: Math.round(log.confidence_score * 100),
        speed_estimate: log.speed_estimate,
        segment_speed_kmh: segmentSpeed ?? log.speed_estimate,
      },
    });

    prevLog = log;
  });

  const first = logs[0];
  const last = logs[logs.length - 1];
  const totalKm = haversineKm(first.lon, first.lat, last.lon, last.lat);
  const totalHours = (last.captured_at.getTime() - first.captured_at.getTime()) / 3600000;
  const avgSpeed = totalHours > 0 ? Number((totalKm / totalHours).toFixed(1)) : 48.0;

  res.json({
    type: 'FeatureCollection',
    license_plate: last.license_plate,
    total_hits: logs.length,
    time_span: {
      start: first.captured_at.toISOString(),
      end: last.captured_at.toISOString(),
    },
    summary: {
      distance_km: Number(totalKm.toFixed(2)),
      avg_speed_kmh: avgSpeed,
    },
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: lineCoords,
        },
        properties: {
          source: 'trackx-anpr',
          total_hits: logs.length,
        },
      },
      ...waypointFeatures,
    ],
  });
});

// Blacklisted Vehicles CRUD
app.get('/api/v1/blacklisted-vehicles/', (req, res) => {
  res.json(blacklistedVehicles);
});

app.post('/api/v1/blacklisted-vehicles/', (req, res) => {
  const { license_plate, owner_name, reason, alert_level } = req.body;
  const newVehicle = {
    id: Date.now(),
    license_plate: license_plate?.trim()?.toUpperCase() || 'UNKNOWN',
    owner_name: owner_name?.trim() || 'Unknown Owner',
    reason: reason?.trim() || 'Manual surveillance addition',
    alert_level: alert_level || 'INFO',
    flagged_at: new Date().toISOString(),
    is_active: true,
  };
  blacklistedVehicles.unshift(newVehicle);

  // Broadcast alert to connected clients
  broadcastAlert({
    type: 'send_alert_notification',
    alert_level: newVehicle.alert_level,
    plate: newVehicle.license_plate,
    owner: newVehicle.owner_name,
    reason: newVehicle.reason,
    camera: 'Command Center Manual Entry',
    coordinates: [77.2090, 28.6139],
    timestamp: new Date().toISOString(),
  });

  res.status(201).json(newVehicle);
});

app.delete('/api/v1/blacklisted-vehicles/:id/', (req, res) => {
  const id = Number(req.params.id);
  blacklistedVehicles = blacklistedVehicles.filter((v) => v.id !== id);
  res.status(204).send();
});

// Video Feeds
app.get('/api/v1/video-feeds/', (req, res) => {
  res.json(videoFeeds);
});

app.post('/api/v1/video-feeds/', (req, res) => {
  const { camera, title } = req.body;
  const camObj = CAMERAS.find((c) => c.id === Number(camera)) || CAMERAS[0];
  const newFeed = {
    id: Date.now(),
    camera: camObj.id,
    camera_id: camObj.camera_id,
    location_name: camObj.location_name,
    title: title || `${camObj.location_name} Stream`,
    video_file: '/sample_feed.mp4',
    video_url: '/sample_feed.mp4',
    uploaded_at: new Date().toISOString(),
    processed: false,
  };
  videoFeeds.unshift(newFeed);
  res.status(201).json(newFeed);
});

app.post('/api/v1/video-feeds/:id/process_video/', (req, res) => {
  const feedId = Number(req.params.id);
  const feed = videoFeeds.find((f) => f.id === feedId);
  const sampleRate = req.body.sample_rate || 5;

  // Simulate progressive detection processing
  let progress = 0;
  const interval = setInterval(() => {
    progress += 25;
    broadcastToAll({
      type: 'send_progress_update',
      video_feed_id: feedId,
      progress: Math.min(progress, 100),
    });

    if (progress >= 100) {
      clearInterval(interval);
      if (feed) feed.processed = true;

      // Add detection result to feed
      const detectedPlate = 'DL 3C AF 9021';
      detectionsStore.unshift({
        id: nextDetectionId++,
        camera_id: feed?.camera_id || 'CAM-042',
        location_name: feed?.location_name || 'Ring Rd / ITO Junction',
        lon: 77.2410,
        lat: 28.6289,
        license_plate: detectedPlate,
        confidence_score: 0.98,
        speed_estimate: 48,
        captured_at: new Date(),
        video_feed_id: feedId,
      });

      broadcastAlert({
        type: 'send_alert_notification',
        alert_level: 'CRITICAL',
        plate: detectedPlate,
        owner: 'Arjun Mehta',
        reason: 'Automated ANPR match in video feed',
        camera: feed?.location_name || 'CCTV Feed',
        coordinates: [77.2410, 28.6289],
        timestamp: new Date().toISOString(),
      });
    }
  }, 1000);

  res.status(202).json({
    video_feed_id: feedId,
    sample_rate: sampleRate,
    task_id: `task_${Date.now()}`,
    status: 'queued',
  });
});

app.get('/api/v1/video-feeds/:id/detections/', (req, res) => {
  const feedId = Number(req.params.id);
  const feedLogs = detectionsStore.filter((d) => d.video_feed_id === feedId);
  res.json(feedLogs);
});

// Trigger test alert endpoint
app.get('/api/v1/fire-test-alert/', (req, res) => {
  const plate = (req.query.plate as string) || 'DL 3C AF 9021';
  const cam = CAMERAS[0];
  const payload = {
    type: 'send_alert_notification',
    alert_level: 'CRITICAL',
    plate,
    owner: 'Arjun Mehta',
    reason: 'Simulated high-priority surveillance alert',
    camera: cam.location_name,
    coordinates: [cam.lon, cam.lat],
    timestamp: new Date().toISOString(),
  };
  broadcastAlert(payload);
  res.json({ broadcast: true, payload });
});

// ---------------------------------------------------------------------------
// SIH Live Demo Multi-Checkpoint Corridor Simulation Engine
// Ported from anpr_engine/management/commands/run_sih_demo.py
// ---------------------------------------------------------------------------

const SIH_CAMERA_GRID = [
  { camera_id: 'CAM-042', location_name: 'Ring Rd / ITO Junction', lon: 77.2410, lat: 28.6289 },
  { camera_id: 'CAM-118', location_name: 'Rajghat Flyover', lon: 77.2498, lat: 28.6412 },
  { camera_id: 'CAM-233', location_name: 'Kashmere Gate ISBT', lon: 77.2295, lat: 28.6673 },
  { camera_id: 'CAM-501', location_name: 'GT Karnal Road', lon: 77.2011, lat: 28.6905 },
  { camera_id: 'CAM-612', location_name: 'Azadpur Mandi', lon: 77.1758, lat: 28.7078 },
];

let sihSimState = {
  activePlate: 'DL 3C AF 9021',
  currentStep: 0,
  history: [] as any[],
  isRunning: false,
};

app.get('/api/v1/simulation/sih-demo/status/', (req, res) => {
  res.json({
    activePlate: sihSimState.activePlate,
    currentStep: sihSimState.currentStep,
    totalSteps: SIH_CAMERA_GRID.length,
    isRunning: sihSimState.isRunning,
    history: sihSimState.history,
    grid: SIH_CAMERA_GRID,
  });
});

app.post('/api/v1/simulation/sih-demo/step/', (req, res) => {
  const plate = (req.body.plate || sihSimState.activePlate || 'DL 3C AF 9021').toUpperCase().trim();
  const stepIndex = typeof req.body.checkpoint_index === 'number'
    ? req.body.checkpoint_index
    : sihSimState.currentStep;

  if (stepIndex >= SIH_CAMERA_GRID.length) {
    return res.status(400).json({ error: 'All checkpoints already completed. Please reset simulation.' });
  }

  const cam = SIH_CAMERA_GRID[stepIndex];
  const nowTime = new Date();
  const speed = req.body.speed_kmh || Math.round(35 + (stepIndex * 8) + (Math.random() * 6));
  const confidence = Number((0.93 + stepIndex * 0.015).toFixed(2));

  // Add detection log
  const newLog: DetectionRecord = {
    id: nextDetectionId++,
    camera_id: cam.camera_id,
    location_name: cam.location_name,
    lon: cam.lon,
    lat: cam.lat,
    license_plate: plate,
    confidence_score: Math.min(confidence, 0.99),
    speed_estimate: speed,
    captured_at: nowTime,
  };
  detectionsStore.unshift(newLog);

  sihSimState.activePlate = plate;
  sihSimState.currentStep = stepIndex + 1;
  const hitRecord = {
    step: stepIndex + 1,
    camera_id: cam.camera_id,
    location_name: cam.location_name,
    coordinates: [cam.lon, cam.lat],
    speed_kmh: speed,
    confidence,
    captured_at: nowTime.toISOString(),
  };
  sihSimState.history.push(hitRecord);

  // Check if plate matches blacklisted vehicle
  const matched = blacklistedStore.find(
    (b) => b.license_plate.replace(/\s+/g, '') === plate.replace(/\s+/g, '')
  );

  // Broadcast checkpoint hit event to all connected WebSocket clients
  broadcastToAll({
    type: 'simulation_checkpoint_hit',
    step: stepIndex + 1,
    total_steps: SIH_CAMERA_GRID.length,
    plate,
    camera: cam.location_name,
    camera_id: cam.camera_id,
    coordinates: [cam.lon, cam.lat],
    speed_kmh: speed,
    confidence,
    is_hotlisted: Boolean(matched),
    timestamp: nowTime.toISOString(),
  });

  // If this is the final checkpoint or matched on hotlist, trigger high-priority critical alert!
  if (matched || stepIndex === SIH_CAMERA_GRID.length - 1) {
    const alertLevel = matched?.alert_level || 'CRITICAL';
    const reason = matched?.reason || `Multi-checkpoint corridor intercept (${speed} km/h at ${cam.location_name})`;
    broadcastAlert({
      type: 'send_alert_notification',
      alert_level: alertLevel,
      plate,
      owner: matched?.owner_name || 'Flagged Target',
      reason,
      camera: `${cam.camera_id} — ${cam.location_name}`,
      coordinates: [cam.lon, cam.lat],
      timestamp: nowTime.toISOString(),
    });
  }

  res.json({
    status: 'ok',
    step: stepIndex + 1,
    totalSteps: SIH_CAMERA_GRID.length,
    hit: hitRecord,
    isFinal: stepIndex + 1 >= SIH_CAMERA_GRID.length,
    isHotlisted: Boolean(matched),
  });
});

app.post('/api/v1/simulation/sih-demo/reset/', (req, res) => {
  const plate = (req.body.plate || sihSimState.activePlate || 'DL 3C AF 9021').toUpperCase().trim();
  sihSimState.currentStep = 0;
  sihSimState.history = [];
  sihSimState.activePlate = plate;
  sihSimState.isRunning = false;

  res.json({ status: 'reset', activePlate: plate, currentStep: 0 });
});

// ---------------------------------------------------------------------------
// Advanced AI Model Studio & ANPR Workbench Endpoints
// ---------------------------------------------------------------------------

// List curated surveillance frames
app.get('/api/v1/anpr/presets/', (req, res) => {
  res.json(PRESET_SURVEILLANCE_FRAMES);
});

// Model benchmark telemetry and hyperparameter config
app.get('/api/v1/anpr/benchmark/', (req, res) => {
  res.json({
    config: currentModelConfig,
    benchmarks: getModelBenchmarkStats(),
    indian_states: INDIAN_STATES_RTO,
  });
});

// Update model hyperparameters
app.post('/api/v1/anpr/configure/', (req, res) => {
  const updated = updateModelConfig(req.body);
  res.json({ status: 'ok', config: updated });
});

// Deep ANPR Image & Frame Inspection
app.post('/api/v1/anpr/inspect/', async (req, res) => {
  try {
    const { preset_id, image, license_plate_hint, use_gemini } = req.body;
    let targetPlate = license_plate_hint || '';
    let vehicleType = 'Sedan';
    let vehicleMake = 'Unknown Vehicle';
    let vehicleColor = 'White';
    let imageUrl = '';
    let location = 'City CCTV Camera';
    let cameraId = 'CAM-042';
    let speed = 48;
    let coordinates: [number, number] = [77.2410, 28.6289];
    let condition = 'Standard HSRP Plate';
    let bbox = [245, 250, 395, 290]; // [x1, y1, x2, y2]
    let presetMatch = null;

    if (preset_id) {
      presetMatch = PRESET_SURVEILLANCE_FRAMES.find((p) => p.id === preset_id);
      if (presetMatch) {
        targetPlate = presetMatch.plate;
        vehicleType = presetMatch.vehicle_type;
        vehicleMake = presetMatch.vehicle_make;
        vehicleColor = presetMatch.color;
        imageUrl = presetMatch.image_url;
        location = presetMatch.location;
        cameraId = presetMatch.camera_id;
        speed = presetMatch.speed_kmh;
        coordinates = presetMatch.coordinates;
        condition = presetMatch.condition;
      }
    }

    if (!targetPlate && image) {
      targetPlate = 'DL 3C AF 9021';
    }

    // Run Indian RTO structural solver
    const slotAnalysis = validateAndCleanPlate(targetPlate);

    // Run Gemini Vision Co-Pilot if requested or enabled
    let geminiAnalysis = null;
    const shouldRunGemini = use_gemini !== false && currentModelConfig.enable_gemini_multimodal;
    if (shouldRunGemini) {
      geminiAnalysis = await analyzeVehicleWithGemini(
        image || imageUrl || targetPlate,
        slotAnalysis.cleaned_text || targetPlate
      );
    }

    // Merge vehicle intelligence
    const finalVehicleType = geminiAnalysis?.vehicle_type || vehicleType;
    const finalMakeModel = geminiAnalysis?.make_model || vehicleMake;
    const finalColor = geminiAnalysis?.color || vehicleColor;
    const finalCondition = geminiAnalysis?.condition || condition;
    const plateClassification = geminiAnalysis?.plate_classification || (targetPlate.includes('UP 14') ? 'Commercial (Yellow)' : targetPlate.includes('DL 8C') ? 'Electric Vehicle (Green)' : 'Private Transport (White HSRP)');
    const tamperCheck = geminiAnalysis?.tamper_check || 'HSRP Chromium Hologram Verified';

    // Cross-check with blacklisted vehicles
    const normalizedPlate = (slotAnalysis.cleaned_text || targetPlate).replace(/\s+/g, '');
    const matchedBlacklist = blacklistedVehicles.find(
      (b) => b.is_active && b.license_plate.replace(/\s+/g, '') === normalizedPlate
    );

    // Compute ensemble score
    const yoloScore = 0.94;
    const slotScore = slotAnalysis.confidence;
    const geminiScore = geminiAnalysis ? geminiAnalysis.confidence : 0.95;
    const ensembleConfidence = Number(((yoloScore * 0.35 + slotScore * 0.35 + geminiScore * 0.30)).toFixed(2));

    res.json({
      plate_detected: slotAnalysis.formatted_plate || targetPlate,
      raw_ocr: targetPlate,
      cleaned_plate: slotAnalysis.cleaned_text,
      confidence: ensembleConfidence,
      bbox,
      image_url: imageUrl || image || null,
      location,
      camera_id: cameraId,
      speed_kmh: speed,
      coordinates,
      slot_analysis: slotAnalysis,
      vehicle_intelligence: {
        vehicle_type: finalVehicleType,
        make_model: finalMakeModel,
        color: finalColor,
        condition: finalCondition,
        plate_classification: plateClassification,
        tamper_check: tamperCheck,
        gemini_notes: geminiAnalysis?.notes || 'Deterministic Indian RTO syntax validation applied successfully',
      },
      models_evaluated: [
        {
          name: currentModelConfig.detector_name,
          role: 'Bounding Box Localization',
          confidence: yoloScore,
          latency: '8.4ms',
          status: 'Passed',
        },
        {
          name: currentModelConfig.ocr_engine,
          role: 'Positional Character Recognizer',
          confidence: slotScore,
          latency: '4.2ms',
          status: slotAnalysis.is_valid_indian_format ? 'Verified RTO Format' : 'Warning: Irregular Format',
        },
        {
          name: 'Gemini 3.8 Flash Multimodal AI',
          role: 'Vehicle Reasoning & Obscuration Recovery',
          confidence: geminiScore,
          latency: geminiAnalysis ? '340ms' : 'Skipped (Config)',
          status: geminiAnalysis ? 'AI Intelligence Verified' : 'Standby',
        },
      ],
      hotlist_status: {
        is_flagged: Boolean(matchedBlacklist),
        alert_level: matchedBlacklist?.alert_level || 'CLEAR',
        owner_name: matchedBlacklist?.owner_name || null,
        reason: matchedBlacklist?.reason || null,
        flagged_at: matchedBlacklist?.flagged_at || null,
      },
    });
  } catch (err: any) {
    console.error('ANPR Inspection error:', err);
    res.status(500).json({ error: err.message || 'Inspection failed' });
  }
});

// Register detection into real-time tracking system from Model Studio
app.post('/api/v1/anpr/register-hit/', (req, res) => {
  const { license_plate, camera_id, location_name, speed, confidence, coordinates } = req.body;
  const plate = (license_plate || '').trim().toUpperCase();
  const cam = CAMERAS.find((c) => c.camera_id === camera_id) || CAMERAS[0];

  const newLog: DetectionRecord = {
    id: nextDetectionId++,
    camera_id: cam.camera_id,
    location_name: location_name || cam.location_name,
    lon: coordinates?.[0] || cam.lon,
    lat: coordinates?.[1] || cam.lat,
    license_plate: plate,
    confidence_score: Number(confidence) || 0.95,
    speed_estimate: Number(speed) || 50,
    captured_at: new Date(),
  };

  detectionsStore.unshift(newLog);

  // Check if plate is on hotlist
  const matched = blacklistedVehicles.find(
    (b) => b.is_active && b.license_plate.replace(/\s+/g, '') === plate.replace(/\s+/g, '')
  );

  if (matched) {
    broadcastAlert({
      type: 'send_alert_notification',
      alert_level: matched.alert_level,
      plate: matched.license_plate,
      owner: matched.owner_name,
      reason: matched.reason,
      camera: newLog.location_name,
      coordinates: [newLog.lon, newLog.lat],
      timestamp: new Date().toISOString(),
    });
  }

  res.status(201).json({
    status: 'registered',
    detection: newLog,
    is_hotlisted: Boolean(matched),
    total_detections_for_plate: detectionsStore.filter(
      (d) => d.license_plate.replace(/\s+/g, '') === plate.replace(/\s+/g, '')
    ).length,
  });
});

// ---------------------------------------------------------------------------
// WebSocket Handling
// ---------------------------------------------------------------------------

const wss = new WebSocketServer({ noServer: true });
const alertClients = new Set<WebSocket>();

function broadcastToAll(data: any) {
  const msg = JSON.stringify(data);
  for (const client of alertClients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  }
}

function broadcastAlert(payload: any) {
  broadcastToAll(payload);
}

// Periodic ambient alerts for live monitoring demo
setInterval(() => {
  if (alertClients.size === 0) return;
  const sampleAlerts = [
    { plate: 'DL 3C AF 9021', level: 'CRITICAL', reason: 'Stolen vehicle flagged by ANPR', camIdx: 0 },
    { plate: 'HR 26 DQ 4412', level: 'WARNING', reason: 'High-speed anomaly in sector', camIdx: 2 },
    { plate: 'UP 14 AB 1234', level: 'WARNING', reason: 'Suspicious trajectory pattern', camIdx: 3 },
  ];
  const pick = sampleAlerts[Math.floor(Math.random() * sampleAlerts.length)];
  const cam = CAMERAS[pick.camIdx];
  broadcastAlert({
    type: 'send_alert_notification',
    alert_level: pick.level,
    plate: pick.plate,
    owner: 'TrackX Anomaly Engine',
    reason: pick.reason,
    camera: cam.location_name,
    coordinates: [cam.lon, cam.lat],
    timestamp: new Date().toISOString(),
  });
}, 25000);

server.on('upgrade', (request, socket, head) => {
  const pathname = request.url ? new URL(request.url, `http://${request.headers.host}`).pathname : '';

  if (pathname.startsWith('/ws/alerts') || pathname.startsWith('/ws/live-video') || pathname.startsWith('/ws')) {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

wss.on('connection', (ws: WebSocket, request: http.IncomingMessage) => {
  const pathname = request.url ? new URL(request.url, `http://${request.headers.host}`).pathname : '';

  if (pathname.includes('live-video')) {
    let frameCount = 0;
    ws.on('message', (data: Buffer | string) => {
      try {
        const parsed = JSON.parse(data.toString());
        frameCount++;
        const scale = parsed.scale || 1;

        // Simulate bounding box detection on the frame
        // Slightly wobble box coordinates to simulate natural tracking
        const wobbleX = Math.sin(frameCount * 0.2) * 15;
        const wobbleY = Math.cos(frameCount * 0.2) * 10;
        const x1 = Math.max(10, 180 * scale + wobbleX);
        const y1 = Math.max(10, 220 * scale + wobbleY);
        const x2 = x1 + 160 * scale;
        const y2 = y1 + 55 * scale;

        const plate = frameCount > 8 ? 'DL 3C AF 9021' : 'DL 3C AF 90??';
        const confirmed = frameCount > 15 ? 'DL 3C AF 9021' : null;

        ws.send(
          JSON.stringify({
            bbox: [x1, y1, x2, y2],
            scale,
            plate_text: plate,
            confidence: 0.96,
            confirmed,
          }),
        );
      } catch (err) {
        console.error('Error handling live video frame:', err);
      }
    });
  } else {
    // Default alert consumer connection
    alertClients.add(ws);

    // Send immediate welcome alert so connection is verified
    ws.send(
      JSON.stringify({
        type: 'send_alert_notification',
        alert_level: 'INFO',
        plate: 'SYS-ONLINE',
        owner: 'Command Center',
        reason: 'Surveillance stream synchronized with 7 CCTV nodes',
        camera: 'Sector Central-DEL',
        coordinates: [77.2090, 28.6139],
        timestamp: new Date().toISOString(),
      }),
    );

    ws.on('close', () => {
      alertClients.delete(ws);
    });
  }
});

// ---------------------------------------------------------------------------
// Vite Middleware / Static Serving
// ---------------------------------------------------------------------------

async function setupVite() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  server.listen(PORT, '0.0.0.0', () => {
    console.log(`TrackX Platform running at http://0.0.0.0:${PORT}`);
  });
}

setupVite().catch((err) => {
  console.error('Failed to start TrackX server:', err);
  process.exit(1);
});
