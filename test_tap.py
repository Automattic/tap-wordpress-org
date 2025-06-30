#!/usr/bin/env python3
"""Test script for tap-wordpress-org-api"""

import json
import subprocess
import sys

def run_tap_for_stream(stream_name, max_records=5):
    """Run the tap and extract a limited number of records for a specific stream."""
    print(f"\n{'='*60}")
    print(f"Testing stream: {stream_name}")
    print('='*60)
    
    # Create a custom catalog with only the specified stream
    catalog = {
        "streams": [
            {
                "tap_stream_id": stream_name,
                "schema": {},
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "selected": True
                        }
                    }
                ]
            }
        ]
    }
    
    # Write temporary catalog
    with open('temp_catalog.json', 'w') as f:
        json.dump(catalog, f)
    
    # Run the tap
    cmd = [
        sys.executable, '-m', 'tap_wordpress_org_api.tap',
        '--config', 'config.json',
        '--catalog', 'temp_catalog.json'
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    record_count = 0
    for line in process.stdout:
        if line.strip():
            data = json.loads(line)
            if data['type'] == 'RECORD' and data['stream'] == stream_name:
                record_count += 1
                print(f"\nRecord #{record_count}:")
                record = data['record']
                # Print key fields
                if stream_name == 'plugins':
                    print(f"  Name: {record.get('name', 'N/A')}")
                    print(f"  Slug: {record.get('slug', 'N/A')}")
                    print(f"  Active Installs: {record.get('active_installs', 'N/A'):,}")
                elif stream_name == 'themes':
                    print(f"  Name: {record.get('name', 'N/A')}")
                    print(f"  Slug: {record.get('slug', 'N/A')}")
                    print(f"  Downloads: {record.get('downloaded', 'N/A'):,}")
                elif stream_name == 'events':
                    print(f"  Title: {record.get('title', 'N/A')}")
                    print(f"  Type: {record.get('type', 'N/A')}")
                    print(f"  Date: {record.get('date', 'N/A')}")
                elif stream_name == 'patterns':
                    print(f"  ID: {record.get('id', 'N/A')}")
                    title = record.get('title', {})
                    print(f"  Title: {title.get('rendered', 'N/A') if isinstance(title, dict) else 'N/A'}")
                
                if record_count >= max_records:
                    process.terminate()
                    break
    
    # Clean up
    subprocess.run(['rm', 'temp_catalog.json'])
    
    print(f"\nTotal records shown: {record_count}")

if __name__ == "__main__":
    print("Testing tap-wordpress-org-api")
    print("This will test each stream and show sample records.\n")
    
    streams = ['plugins', 'themes', 'events', 'patterns']
    
    for stream in streams:
        try:
            run_tap_for_stream(stream, max_records=3)
        except Exception as e:
            print(f"Error testing stream {stream}: {e}")
    
    print("\n" + "="*60)
    print("Testing completed!")
    print("="*60)