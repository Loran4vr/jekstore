#!/usr/bin/env python3
"""
Auto Video Generator - Complete Video Creation System
Creates viral videos with properly related visuals, audio, and text
"""

import os
import subprocess
import json
from datetime import datetime

# Configuration
WIDTH = 720
HEIGHT = 1280
FPS = 30
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
OUTPUT_DIR = '/root/.openclaw/videos'

class VideoGenerator:
    """Complete video generation system"""
    
    # Related color schemes for different topics
    TOPICS = {
        'brain': {
            'colors': ['pink', 'red', 'purple', 'magenta'],
            'emojis': ['🧠', '🧬', '🩸', '💜'],
            'keywords': ['brain', 'neural', 'thought', 'memory']
        },
        'tech': {
            'colors': ['blue', 'cyan', 'purple', 'navy'],
            'emojis': ['💻', '🤖', '📱', '💡'],
            'keywords': ['data', 'tech', 'digital', 'code']
        },
        'money': {
            'colors': ['green', 'gold', 'yellow', 'darkgreen'],
            'emojis': ['💰', '💵', '💎', '🏦'],
            'keywords': ['money', 'dollar', 'rich', 'wealth']
        },
        'space': {
            'colors': ['black', 'navy', 'darkblue', 'purple'],
            'emojis': ['🌌', '⭐', '🪐', '🚀'],
            'keywords': ['star', 'planet', 'universe', 'galaxy']
        },
        'internet': {
            'colors': ['blue', 'cyan', 'lightblue', 'teal'],
            'emojis': ['🌐', '📡', '💬', '🔗'],
            'keywords': ['internet', 'web', 'online', 'network']
        }
    }
    
    def __init__(self, topic='brain'):
        self.topic = topic
        self.topic_data = self.TOPICS.get(topic, self.TOPICS['brain'])
        self.scenes = []
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def create_gradient_background(self, colors, duration, output):
        """Create animated gradient background"""
        color_str = ':'.join(colors[:3])
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i',
            f'gradients=s={WIDTH}x{HEIGHT}:c0={colors[0]}:c1={colors[1]}:c2={colors[2]}:duration={duration}',
            '-c:v', 'libx264', '-t', str(duration), '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def add_text_overlay(self, input_video, text, output, fontsize=50, color='white', y_offset=0):
        """Add text to video"""
        cmd = [
            'ffmpeg', '-i', input_video, '-vf',
            f'drawtext=fontfile={FONT}:text={text}:fontcolor={color}:fontsize={fontsize}:x=(w-text_w)/2:y=(h-text_h)/2+{y_offset}',
            '-c:v', 'libx264', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def generate_voiceover(self, text, output):
        """Generate voiceover using TTS"""
        text_clean = text.replace(' ', '%20').replace('!', '').replace('?', '')
        url = f'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={text_clean}&tl=en'
        subprocess.run(['curl', '-s', '-o', output, url], capture_output=True)
        return output
    
    def create_background_music(self, duration, output):
        """Create background music"""
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'sine=frequency={220+int(duration*10)}',
            '-t', str(duration), '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def mix_audio(self, voice_path, music_path, voice_vol=0.7, music_vol=0.2, output=None):
        """Mix voiceover with background music"""
        if output is None:
            output = voice_path.replace('.mp3', '_mixed.mp3')
        cmd = [
            'ffmpeg', '-i', voice_path, '-i', music_path, '-filter_complex',
            f'[0:a]volume={voice_vol}[v];[1:a]volume={music_vol}[m];[v][m]amix=inputs=2:duration=first',
            '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def combine_video_audio(self, video_path, audio_path, output):
        """Combine video with audio"""
        cmd = [
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    
    def create_scene(self, text, voiceover, duration, scene_num, emoji=None):
        """Create a single scene"""
        colors = self.topic_data['colors']
        color = colors[scene_num % len(colors)]
        
        # Create background
        bg_path = f'{OUTPUT_DIR}/scene_{scene_num}_bg.mp4'
        self.create_gradient_background(colors, duration, bg_path)
        
        # Add text
        txt_path = f'{OUTPUT_DIR}/scene_{scene_num}_txt.mp4'
        
        if emoji:
            full_text = f'{emoji} {text}'
        else:
            full_text = text
            
        cmd = [
            'ffmpeg', '-i', bg_path, '-vf',
            f'drawtext=fontfile={FONT}:text={full_text}:fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264', '-t', str(duration), '-y', txt_path
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Generate voiceover
        vo_path = f'{OUTPUT_DIR}/scene_{scene_num}_vo.mp3'
        self.generate_voiceover(voiceover, vo_path)
        
        # Create background music
        music_path = f'{OUTPUT_DIR}/scene_{scene_num}_music.mp3'
        self.create_background_music(duration, music_path)
        
        # Mix audio
        mixed_audio = self.mix_audio(vo_path, music_path, output=f'{OUTPUT_DIR}/scene_{scene_num}_audio.mp3')
        
        # Combine
        final_path = f'{OUTPUT_DIR}/scene_{scene_num}_final.mp4'
        self.combine_video_audio(txt_path, mixed_audio, final_path)
        
        return final_path
    
    def create_viral_video(self, facts, title="MIND BLOWING FACTS"):
        """Create complete viral video from facts"""
        print(f"Creating {self.topic} video with {len(facts)} facts...")
        
        scenes = []
        
        # Create intro
        intro_scene = self.create_scene(
            title, 
            f"Get ready for {self.topic} facts that will blow your mind!",
            3, 0, '🔥'
        )
        scenes.append(intro_scene)
        
        # Create fact scenes
        for i, fact in enumerate(facts):
            emoji = self.topic_data['emojis'][i % len(self.topic_data['emojis'])]
            scene = self.create_scene(
                fact['text'],
                fact['voiceover'],
                fact['duration'],
                i + 1,
                emoji
            )
            scenes.append(scene)
        
        # Create outro
        outro_scene = self.create_scene(
            "FOLLOW FOR MORE",
            "Follow for more incredible facts!",
            2, len(facts) + 1, '❤️'
        )
        scenes.append(outro_scene)
        
        # Combine all scenes
        self.concatenate_scenes(scenes, f'{OUTPUT_DIR}/FINAL_{self.topic}_video.mp4')
        
        return f'{OUTPUT_DIR}/FINAL_{self.topic}_video.mp4'
    
    def concatenate_scenes(self, scenes, output):
        """Combine multiple scenes into one video"""
        list_file = f'{OUTPUT_DIR}/concat_list.txt'
        with open(list_file, 'w') as f:
            for scene in scenes:
                f.write(f"file '{scene}'\n")
        
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file,
            '-c', 'copy', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        return output


# Example usage
if __name__ == '__main__':
    # Create brain facts video
    generator = VideoGenerator(topic='brain')
    
    facts = [
        {'text': '37,000 GB', 'voiceover': 'Your brain processes 37000 gigabytes of data every single day', 'duration': 4},
        {'text': '= 30 YEARS', 'voiceover': "That's equivalent to watching 30 years of movies in one day", 'duration': 3},
        {'text': '100 BILLION', 'voiceover': 'Your brain has 100 billion neurons', 'duration': 3},
    ]
    
    result = generator.create_viral_video(facts)
    print(f"Video created: {result}")
