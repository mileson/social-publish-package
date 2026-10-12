#!/usr/bin/env python3
"""Create tiny synthetic media and a local workbench; never upload or publish."""
from pathlib import Path
import argparse
import json
import subprocess
from PIL import Image, ImageDraw
from extract_first_frame_cover import resolve_ffmpeg
from build_publish_review import build_html

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'output' / 'demo')
    args = parser.parse_args()
    dest = args.output_dir.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    payload = json.loads((ROOT / 'examples/demo-input.json').read_text())
    covers = []
    for role, name, size in [('cover', 'demo-3x4.png', (300, 400)), ('bilibiliCover', 'demo-4x3.png', (400, 300)), ('horizontalCover', 'demo-16x9.png', (640, 360))]:
        image = Image.new('RGB', size, '#e8f2fb')
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((24, 60, size[0]-24, size[1]-40), radius=16, fill='#ffffff', outline='#3a83f7', width=3)
        draw.text((36, 86), 'SYNTHETIC DEMO', fill='#173553')
        draw.text((36, 112), 'Sort / Place / Review', fill='#173553')
        path = dest / name
        image.save(path)
        covers.append({'id':role,'label':name,'path':str(path),'role':role,'source':'provided'})
    video = dest / 'demo.mp4'
    # One second, one encoder thread; input is our own synthetic cover image.
    subprocess.run([resolve_ffmpeg(), '-hide_banner', '-loglevel', 'error', '-y', '-loop', '1', '-i', str(dest / 'demo-16x9.png'), '-t', '1', '-r', '12', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-threads', '1', str(video)], check=True)
    payload['video']['cover_candidates'] = covers
    payload['video']['selected_cover_ids'] = {item['role']:item['id'] for item in covers}
    (dest / 'review-input.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    result = build_html(payload, video_path=video, output_path=dest / 'review.html')
    print(json.dumps({'ok':result['ok'],'output':result['output'],'published':False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
