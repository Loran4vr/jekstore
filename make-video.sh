#!/bin/bash
# Simple promo video generator for JekStore

# Colors
WHITE="ffffff"
BLACK="000000"
GOLD="FFD700"
BLUE="58a6ff"

# Create a simple text video
ffmpeg -f lavfi -i color=c=black:s=720x1280:d=5 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='jekstore':fontcolor=gold:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -t 5 -pix_fmt yuv420p /tmp/promo1.mp4

ffmpeg -f lavfi -i color=c=black:s=720x1280:d=5 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Digital Products':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -t 5 -pix_fmt yuv420p /tmp/promo2.mp4

ffmpeg -f lavfi -i color=c=black:s=720x1280:d=5 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Pay with Bitcoin':fontcolor=blue:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -t 5 -pix_fmt yuv420p /tmp/promo3.mp4

ffmpeg -f lavfi -i color=c=black:s=720x1280:d=5 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Link in bio!':fontcolor=gold:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -t 5 -pix_fmt yuv420p /tmp/promo4.mp4

# Combine all
ffmpeg -f concat -i <(echo "file '/tmp/promo1.mp4'"; echo "file '/tmp/promo2.mp4'"; echo "file '/tmp/promo3.mp4'"; echo "file '/tmp/promo4.mp4'") -c copy /tmp/jekstore-promo.mp4

echo "Video created: /tmp/jekstore-promo.mp4"
ls -la /tmp/jekstore-promo.mp4
