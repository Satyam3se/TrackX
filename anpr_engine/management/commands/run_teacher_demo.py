from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.gis.geos import Point
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from anpr_engine.models import CameraNode, DetectionLog, BlacklistedVehicle

class Command(BaseCommand):
    help = 'Runs an end-to-end demonstration of the TrackX trajectory and alert system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting TrackX Live Demonstration...'))

        # 1. Cleanup
        DetectionLog.objects.all().delete()
        CameraNode.objects.all().delete()
        BlacklistedVehicle.objects.all().delete()
        self.stdout.write('Cleaned existing demo data.')

        # 2. Seed Camera Nodes (Mock City Route)
        # Route: Central Station -> North Gate -> Market Sq -> Bridge -> Exit Tunnel
        route_data = [
            ('CAM_01', 'Central Station', 77.2090, 28.6139),
            ('CAM_02', 'North Gate', 77.2150, 28.6200),
            ('CAM_03', 'Market Square', 77.2200, 28.6250),
            ('CAM_04', 'City Bridge', 77.2250, 28.6200),
            ('CAM_05', 'Exit Tunnel', 77.2300, 28.6150),
        ]
        
        nodes = []
        for cid, name, lon, lat in route_data:
            node = CameraNode.objects.create(
                camera_id=cid,
                location_name=name,
                location=Point(lon, lat),
                is_active=True
            )
            nodes.append(node)
        self.stdout.write(f'Seeded {len(nodes)} CameraNodes across the city route.')

        # 3. Seed Blacklisted Vehicle
        target_plate = 'UP14AB1234'
        blacklisted = BlacklistedVehicle.objects.create(
            license_plate=target_plate,
            owner_name='Suspicious Subject A',
            reason='Wanted for urban traffic violation',
            alert_level='CRITICAL',
            is_active=True
        )
        self.stdout.write(f'Added target vehicle {target_plate} to hotlist.')

        # 4. Simulate Trajectory (Vehicle moving through nodes)
        self.stdout.write(f'Simulating vehicle {target_plate} movement...')
        start_time = timezone.now()

        for i, node in enumerate(nodes):
            # Increment time by 2-5 minutes per node
            captured_at = start_time + timezone.timedelta(minutes=i * 3)
            
            DetectionLog.objects.create(
                camera=node,
                license_plate=target_plate,
                confidence_score=0.98 - (i * 0.02), # Slight decay in confidence
                captured_at=captured_at,
                speed_estimate=45.0 + (i * 2.5)
            )
            self.stdout.write(f'  -> Detected at {node.location_name} at {captured_at.strftime("%H:%M:%S")}')

        # 5. Trigger Live WebSocket Alert (Final Node)
        self.stdout.write('Triggering live WebSocket alert for final node...')
        channel_layer = get_channel_layer()
        final_node = nodes[-1]
        
        payload = {
            'type': 'send_alert_notification',
            'alert_level': blacklisted.alert_level,
            'plate': target_plate,
            'owner': blacklisted.owner_name,
            'reason': blacklisted.reason,
            'camera': final_node.location_name,
            'coordinates': [final_node.location.x, final_node.location.y],
            'timestamp': timezone.now().isoformat(),
        }
        
        async_to_sync(channel_layer.group_send)('surveillance_alerts', payload)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DEMO COMPLETE: Check your Dashboard now!'))
        self.stdout.write(self.style.SUCCESS(f'1. Search for plate: {target_plate}'))
        self.stdout.write(self.style.SUCCESS('2. You should see a neon trajectory line on the map.'))
        self.stdout.write(self.style.SUCCESS('3. A CRITICAL alert popup should have appeared.'))
        self.stdout.write(self.style.SUCCESS('='*60))
