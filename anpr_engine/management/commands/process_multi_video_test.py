"""Multi-video, same-plate ANPR test command.

Uploads several video files, associates each with a distinct CameraNode,
and runs the YOLOv8 + EasyOCR pipeline sequentially across all of them.
A summary is printed showing how the same license plate was detected across
different cameras over time (cross-video trajectory).

Usage:
    python manage.py process_multi_video_test --videos video1.mp4 video2.mp4 \
        [--cameras CAM_NORTH CAM_SOUTH] [--sample-rate 5]
"""

import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from anpr_engine.models import CameraNode, CameraVideoFeed, DetectionLog


class Command(BaseCommand):
    help = (
        'Upload multiple videos, associate each with a distinct CameraNode, '
        'run the ANPR pipeline across them, and print a cross-camera '
        'trajectory summary for matching plates.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--videos',
            nargs='+',
            type=str,
            required=True,
            help='Paths to one or more video files.',
        )
        parser.add_argument(
            '--cameras',
            nargs='*',
            type=str,
            default=None,
            help=(
                'Camera IDs to associate with each video (must match '
                'existing CameraNode.camera_id). Defaults to CAM_NORTH, '
                'CAM_SOUTH, CAM_EAST, ...'
            ),
        )
        parser.add_argument(
            '--sample-rate',
            type=int,
            default=5,
            help='Process every Nth frame (default: 5).',
        )

    def handle(self, *args, **options):
        video_paths = options['videos']
        camera_ids = options['cameras']
        sample_rate = max(1, options['sample_rate'])

        for path in video_paths:
            if not os.path.isfile(path):
                raise CommandError(f'Video file not found: {path}')

        if camera_ids is None:
            camera_ids = [f'CAM_{d}' for d in ('NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTER', 'EXIT')]
        if len(camera_ids) < len(video_paths):
            raise CommandError(
                f'Need at least {len(video_paths)} camera IDs '
                f'(got {len(camera_ids)}).'
            )

        cameras = {}
        for cid in camera_ids[: len(video_paths)]:
            cam = CameraNode.objects.filter(camera_id=cid).first()
            if cam is None:
                raise CommandError(
                    f'No CameraNode with camera_id={cid!r}. '
                    'Create it first via seed_trackx or the admin.'
                )
            cameras[cid] = cam

        self.stdout.write('=' * 70)
        self.stdout.write('  TRACKX — MULTI-VIDEO SAME-PLATE TRAJECTORY TEST')
        self.stdout.write('=' * 70)

        total_detections = 0
        total_alerts = 0
        summaries = []

        for idx, (video_path, cid) in enumerate(
            zip(video_paths, list(cameras)), start=1
        ):
            camera = cameras[cid]

            # Reuse the feed upload flow so each video gets its own CameraVideoFeed.
            with open(video_path, 'rb') as fh:
                uploaded = File(fh, name=os.path.basename(video_path))
                feed = CameraVideoFeed.objects.create(
                    camera=camera,
                    title=f'{os.path.basename(video_path)} [{cid}]',
                    video_file=uploaded,
                )

            self.stdout.write(f'[{idx}/{len(video_paths)}] Processing {video_path}')
            self.stdout.write(
                f'    -> Camera {camera.camera_id} @ {camera.location_name}'
            )

            from anpr_engine.vision_video import process_video_stream

            summary = process_video_stream(feed.id, sample_rate=sample_rate)
            total_detections += summary['detections_created']
            total_alerts += summary['alerts_triggered']
            summaries.append({
                'video_path': video_path,
                'feed_id': feed.id,
                'camera_id': camera.camera_id,
                'location_name': camera.location_name,
                **summary,
            })

            self.stdout.write(
                f'    -> {summary["detections_created"]} detections, '
                f'{summary["alerts_triggered"]} alert(s)'
            )

        self._print_trajectory_summary(summaries, total_detections, total_alerts)

    def _print_trajectory_summary(self, summaries, total_detections, total_alerts):
        """Print a cross-camera timeline for plates seen in 2+ feeds."""
        from collections import defaultdict

        self.stdout.write('-' * 70)
        self.stdout.write('  CROSS-CAMERA TRAJECTORY SUMMARY')
        self.stdout.write('-' * 70)

        plate_events = defaultdict(list)
        for summary in summaries:
            feed_id = summary['feed_id']
            logs = DetectionLog.objects.filter(video_feed_id=feed_id).order_by(
                'frame_timestamp',
            )
            for log in logs:
                plate_events[log.license_plate].append(
                    (summary['camera_id'], summary['location_name'],
                     log.frame_timestamp, log.captured_at, log.confidence_score),
                )

        for plate, events in sorted(plate_events.items()):
            self.stdout.write(f'Plate: {plate} ({len(events)} detection(s))')
            for cam_id, loc, ts, captured_at, conf in events:
                self.stdout.write(
                    f'    {cam_id:12s} {loc:32s} frame={ts:8.2f}s  '
                    f'conf={conf:.2f}  {captured_at:%H:%M:%S}'
                )

            if len({e[0] for e in events}) > 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'    >> Plate {plate} crossed '
                        f'{len({e[0] for e in events})} cameras => '
                        'cross-video trajectory established.'
                    )
                )

        self.stdout.write('-' * 70)
        self.stdout.write(
            f'  TOTAL: {total_detections} detections, '
            f'{total_alerts} WebSocket alert(s) fired'
        )
        self.stdout.write('=' * 70)