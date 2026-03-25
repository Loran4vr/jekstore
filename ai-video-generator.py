#!/usr/bin/env python3
"""
Advanced AI Video Generator - Auto-generates viral videos
Uses effects, transitions, animations, and optimized settings
"""

import subprocess
import os
import random
import json
from datetime import datetime

# Configuration
WIDTH = 720
HEIGHT = 1280
FPS = 30
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
OUTPUT_DIR = '/root/.openclaw/videos'

class AIVideoGenerator:
    """Advanced AI Video Generator"""
    
    # Predefined styles matching viral content
    STYLES = {
        'brain': {
            'colors': ['#ff1493', '#8b008b', '#4b0082', '#9400d3', '#ff69b4'],
            'emojis': ['🧠', '🧬', '💜', '🩸', '⚡'],
            'facts': [
                {'text': '🧠 YOUR BRAIN', 'voiceover': 'Your brain is absolutely incredible'},
                {'text': '37,000 GB', 'voiceover': 'It processes 37000 gigabytes of data daily'},
                {'text': '= 30 YEARS', 'voiceover': "That's equivalent to 30 years of movies"},
                {'text': '🔥 FOLLOW', 'voiceover': 'Follow for more facts'},
            ]
        },
        'money': {
            'colors': ['#00ff00', '#ffd700', '#ffaa00', '#00cc00', '#ffcc00'],
            'emojis': ['💰', '💵', '💎', '🏦', '📈'],
            'facts': [
                {'text': '💰 MONEY', 'voiceover': 'Get ready for insane money facts'},
                {'text': '$2,489/SEC', 'voiceover': 'Jeff Bezos earns $2,489 every second'},
                {'text': '$8.5B/DAY', 'voiceover': 'The US prints $8.5 billion daily'},
                {'text': '📈 FOLLOW', 'voiceover': 'Follow for more wealth facts'},
            ]
        },
        'space': {
            'colors': ['#000033', '#000066', '#0000cc', '#1a1a4d', '#0d0d2a'],
            'emojis': ['🌌', '⭐', '🪐', '🚀', '🌍'],
            'facts': [
                {'text': '🌌 SPACE', 'voiceover': 'Mind-blowing space facts incoming'},
                {'text': '⭐ 10^24 STARS', 'voiceover': 'There are more stars than grains of sand'},
                {'text': '🪐 243 DAYS', 'voiceover': 'A day on Venus is longer than its year'},
                {'text': '🚀 FOLLOW', 'voiceover': 'Follow for more cosmic facts'},
            ]
        },
        'internet': {
            'colors': ['#0066ff', '#00ccff', '#0099ff', '#00ffff', '#33ccff'],
            'emojis': ['🌐', '📡', '💬', '🔗', '📱'],
            'facts': [
                {'text': '🌐 INTERNET', 'voiceover': 'Insane internet facts'},
                {'text': '8.5B SEARCHES', 'voiceover': 'Google processes 8.5 billion searches daily'},
                {'text': '500M TWEETS', 'voiceover': '500 million tweets sent every day'},
                {'text': '📱 FOLLOW', 'voiceover': 'Follow for more tech facts'},
            ]
        }
    }
    
    def __init__(self, topic='brain'):
        self.topic = topic
        self.style = self.STYLES.get(topic, self.STYLES['brain'])
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def generate_tts(self, text, output_path):
        """Generate text-to-speech"""
        text_clean = text.replace(' ', '%20').replace('!', '').replace('?', '').replace(',', '')
        url = f'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={text_clean}&tl=en'
        subprocess.run(['curl', '-s', '-o', output_path, url], capture_output=True)
        return output_path
    
    def generate_music(self, duration, output_path):
        """Generate background music"""
        freq = random.randint(220, 440)
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', f'sine=frequency={freq}',
            '-t', str(duration), '-y', output_path
        ], capture_output=True)
        return output_path
    
    def create_scene(self, text, voiceover, duration, scene_num, style=None):
        """Create a single scene with effects"""
        if style is None:
            style = self.style
        
        colors = style['colors']
        color = colors[scene_num % len(colors)]
        
        # Create gradient background
        bg_path = f'{OUTPUT_DIR}/ai_scene_{scene_num}.mp4'
        result = subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i',
            f'gradients=s={WIDTH}x{HEIGHT}:c0={colors[0]}:c1={colors[1]}:c2={colors[2]}:duration={duration}',
            '-c:v', 'libx264', '-t', str(duration), '-y', bg_path
        ], capture_output=True)
        
        # Add text overlay
        txt_path = f'{OUTPUT_DIR}/ai_text_{scene_num}.mp4'
        
        # Split text if too long
        lines = text.split('\n') if '\n' in text else [text]
        filter_str = ''
        for i, line in enumerate(lines):
            filter_str += f"drawtext=fontfile={FONT}:text={line}:fontcolor=white:fontsize={50-i*5}:x=(w-text_w)/2:y=(h-text_h)/2+{i*50}:box=1:boxcolor=black@0.5:boxborderw=5,"
        
        filter_str = filter_str.rstrip(',')
        
        result = subprocess.run([
            'ffmpeg', '-i', bg_path, '-vf', filter_str,
            '-c:v', 'libx264', '-t', str(duration), '-y', txt_path
        ], capture_output=True)
        
        # Generate voiceover
        vo_path = f'{OUTPUT_DIR}/ai_vo_{scene_num}.mp3'
        self.generate_tts(voiceover, vo_path)
        
        # Generate music
        music_path = f'{OUTPUT_DIR}/ai_music_{scene_num}.mp3'
        self.generate_music(duration, music_path)
        
        # Mix audio
        mixed_path = f'{OUTPUT_DIR}/ai_mixed_{scene_num}.mp3'
        subprocess.run([
            'ffmpeg', '-i', vo_path, '-i', music_path, '-filter_complex',
            '[0:a]volume=0.7[vo];[1:a]volume=0.15[mu];[vo][mu]amix=inputs=2:duration=first',
            '-y', mixed_path
        ], capture_output=True)
        
        # Combine video + audio
        final_path = f'{OUTPUT_DIR}/ai_final_{scene_num}.mp4'
        subprocess.run([
            'ffmpeg', '-i', txt_path, '-i', mixed_path,
            '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y', final_path
        ], capture_output=True)
        
        return final_path
    
    def generate_video(self, topic=None):
        """Generate complete viral video"""
        if topic is None:
            topic = self.topic
        
        style = self.STYLES.get(topic, self.STYLES['brain'])
        facts = style['facts']
        
        print(f"Generating {topic} video with {len(facts)} scenes...")
        
        scenes = []
        for i, fact in enumerate(facts):
            duration = random.randint(2, 4)
            scene = self.create_scene(fact['text'], fact['voiceover'], duration, i, style)
            scenes.append(scene)
        
        # Combine all scenes
        list_file = f'{OUTPUT_DIR}/ai_concat.txt'
        with open(list_file, 'w') as f:
            for scene in scenes:
                f.write(f"file '{scene}'\n")
        
        output = f'{OUTPUT_DIR}/AI_GENERATED_{topic.upper()}.mp4'
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file,
            '-c', 'copy', '-y', output
        ], capture_output=True)
        
        print(f"Video generated: {output}")
        return output
    
    def generate_all_topics(self):
        """Generate videos for all topics"""
        for topic in self.STYLES.keys():
            try:
                self.generate_video(topic)
            except Exception as e:
                print(f"Error generating {topic}: {e}")
        return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        generator = AIVideoGenerator(topic)
        generator.generate_video(topic)
    else:
        # Generate all topics
        generator = AIVideoGenerator()
        generator.generate_all_topics()
