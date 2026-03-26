#!/usr/bin/env python3
"""
Auto Video Generator - Creates viral videos with synced audio/text
"""

import subprocess
import os
import random
import json
from datetime import datetime

# Video settings
WIDTH = 720
HEIGHT = 1280
FPS = 30

# Color schemes
COLORS = {
    'blue': '#000033',
    'purple': '#1a0033', 
    'red': '#330000',
    'green': '#003300',
    'gold': '#332200',
    'cyan': '#003333'
}

# Fonts
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

class VideoEditor:
    def __init__(self, output_dir='/tmp'):
        self.output_dir = output_dir
        self.clips = []
        self.voiceovers = []
        
    def create_color_clip(self, color, duration, text=None, size=WIDTH):
        """Create solid color clip with optional text"""
        clip_path = f'{self.output_dir}/clip_{len(self.clips)}.mp4'
        color_hex = COLORS.get(color, '#000000')
        
        cmd = ['ffmpeg', '-f', 'lavfi', '-i', f'color=c={color_hex}:s={WIDTH}x{HEIGHT}:d={duration}',
               '-c:v', 'libx264', '-t', str(duration), '-y', clip_path]
        
        if text:
            cmd.extend(['-vf', f'drawtext=fontfile={FONT}:text={text}:fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2'])
        
        subprocess.run(cmd, capture_output=True)
        self.clips.append(clip_path)
        return clip_path
    
    def create_text_clip(self, color, duration, texts):
        """Create clip with multiple text overlays"""
        clip_path = f'{self.output_dir}/text_clip_{len(self.clips)}.mp4'
        color_hex = COLORS.get(color, '#000000')
        
        filter_str = f'color=c={color_hex}:s={WIDTH}x{HEIGHT}:d={duration}'
        
        for i, (text, start_time) in enumerate(texts):
            filter_str += f',drawtext=fontfile={FONT}:text={text}:fontcolor=white:fontsize=45:x=(w-text_w)/2:y=(h-text_h)/2+{i*30}:enable=between(t,{start_time},{start_time+3})'
        
        cmd = ['ffmpeg', '-f', 'lavfi', '-i', filter_str, '-c:v', 'libx264', '-t', str(duration), '-y', clip_path]
        subprocess.run(cmd, capture_output=True)
        return clip_path
    
    def generate_voiceover(self, text, output_path):
        """Generate voiceover using Google TTS"""
        text_clean = text.replace(' ', '%20')
        url = f'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={text_clean}&tl=en'
        subprocess.run(['curl', '-s', '-o', output_path, url], capture_output=True)
        return output_path
    
    def mix_audio(self, voice_path, music_path, voice_vol=0.7, music_vol=0.2):
        """Mix voiceover with background music"""
        output = voice_path.replace('.mp3', '_mixed.mp3')
        cmd = ['ffmpeg', '-i', voice_path, '-i', music_path, '-filter_complex',
               f'[0:a]volume={voice_vol}[v];[1:a]volume={music_vol}[m];[v][m]amix=inputs=2:duration=first',
               '-y', output]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def combine_clip_with_audio(self, clip_path, audio_path, output_path):
        """Combine video clip with audio"""
        cmd = ['ffmpeg', '-i', clip_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y', output_path]
        subprocess.run(cmd, capture_output=True)
        return output_path
    
    def concatenate(self, input_clips, output_path):
        """Concatenate multiple clips"""
        list_file = f'{self.output_dir}/concat_list.txt'
        with open(list_file, 'w') as f:
            for clip in input_clips:
                f.write(f"file '{clip}'\n")
        
        cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', '-y', output_path]
        subprocess.run(cmd, capture_output=True)
        return output_path
    
    def create_viral_fact_video(self, facts):
        """Create complete viral fact video"""
        print(f"Creating viral video with {len(facts)} facts...")
        
        # Create clips and audio
        final_clips = []
        
        for i, fact in enumerate(facts):
            # Create color background
            color = list(COLORS.keys())[i % len(COLORS)]
            clip = self.create_color_clip(color, fact['duration'])
            
            # Add text
            if 'main_text' in fact:
                clip = self.create_text_clip(color, fact['duration'], [(fact['main_text'], 0)])
            
            # Generate voiceover
            voice_path = f'{self.output_dir}/voice_{i}.mp3'
            self.generate_voiceover(fact['voiceover'], voice_path)
            
            # Combine
            final = f'{self.output_dir}/fact_{i}.mp4'
            self.combine_clip_with_audio(clip, voice_path, final)
            final_clips.append(final)
        
        # Combine all
        output = f'{self.output_dir}/viral_output.mp4'
        self.concatenate(final_clips, output)
        
        print(f"Video created: {output}")
        return output


if __name__ == '__main__':
    # Test
    editor = VideoEditor()
    
    facts = [
        {'duration': 3, 'main_text': '🧠 YOUR BRAIN', 'voiceover': 'Did you know your brain is absolutely incredible'},
        {'duration': 4, 'main_text': '37000 GB', 'voiceover': 'It processes 37000 gigabytes of information every single day'},
        {'duration': 3, 'main_text': '🤯 AMAZING', 'voiceover': 'Follow for more mind blowing facts'}
    ]
    
    result = editor.create_viral_fact_video(facts)
    print(f"Result: {result}")
