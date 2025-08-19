"""
Utilitaires audio pour la visualisation et le traitement
"""
import numpy as np
from pydub import AudioSegment
import os


class AudioUtils:
    """Utilitaires pour le traitement audio"""
    
    @staticmethod
    def load_waveform_data(filepath):
        """Charge les données de forme d'onde d'un fichier audio"""
        try:
            # Charger le fichier audio
            audio = AudioSegment.from_file(filepath)
            
            # Convertir en mono pour simplifier
            audio = audio.set_channels(1)
            
            # Obtenir les données brutes
            raw_data = audio.raw_data
            
            # Convertir en numpy array
            if audio.sample_width == 1:
                dtype = np.uint8
            elif audio.sample_width == 2:
                dtype = np.int16
            elif audio.sample_width == 4:
                dtype = np.int32
            else:
                dtype = np.float32
            
            samples = np.frombuffer(raw_data, dtype=dtype)
            
            # Normaliser entre -1 et 1
            if dtype != np.float32:
                max_val = np.iinfo(dtype).max
                samples = samples.astype(np.float32) / max_val
            
            return samples, audio.frame_rate
            
        except Exception as e:
            print(f"Erreur chargement waveform: {e}")
            return None, None
    
    @staticmethod
    def downsample_waveform(samples, target_points=1000):
        """Réduit le nombre de points de la forme d'onde pour l'affichage"""
        if samples is None or len(samples) == 0:
            return None
        
        if len(samples) <= target_points:
            return samples
        
        # Calculer le facteur de réduction
        factor = len(samples) // target_points
        
        # Redimensionner en prenant des moyennes
        downsampled = []
        for i in range(0, len(samples) - factor, factor):
            chunk = samples[i:i + factor]
            downsampled.append(np.mean(np.abs(chunk)))
        
        return np.array(downsampled)
    
    @staticmethod
    def get_audio_peaks(samples, num_peaks=100):
        """Extrait les pics audio pour la visualisation"""
        if samples is None or len(samples) == 0:
            return None
        
        # Diviser en segments
        segment_size = len(samples) // num_peaks
        if segment_size == 0:
            return np.abs(samples)
        
        peaks = []
        for i in range(0, len(samples), segment_size):
            segment = samples[i:i + segment_size]
            if len(segment) > 0:
                peak = np.max(np.abs(segment))
                peaks.append(peak)
        
        return np.array(peaks)
    
    @staticmethod
    def format_duration(seconds):
        """Formate une durée en secondes au format mm:ss"""
        if seconds < 0:
            seconds = 0
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def get_audio_info(filepath):
        """Récupère les informations d'un fichier audio"""
        try:
            audio = AudioSegment.from_file(filepath)
            
            return {
                'duration': len(audio) / 1000.0,  # en secondes
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'bitrate': audio.frame_rate * audio.channels * audio.sample_width * 8
            }
            
        except Exception as e:
            print(f"Erreur info audio: {e}")
            return None
    
    @staticmethod
    def normalize_audio_level(samples, target_level=0.8):
        """Normalise le niveau audio"""
        if samples is None or len(samples) == 0:
            return samples
        
        max_val = np.max(np.abs(samples))
        if max_val == 0:
            return samples
        
        # Calculer le facteur de normalisation
        factor = target_level / max_val
        
        return samples * factor
    
    @staticmethod
    def apply_fade(samples, fade_in_ms=100, fade_out_ms=100, sample_rate=44100):
        """Applique un fade in/out aux échantillons"""
        if samples is None or len(samples) == 0:
            return samples
        
        samples = samples.copy()
        
        # Convertir ms en échantillons
        fade_in_samples = int(fade_in_ms * sample_rate / 1000)
        fade_out_samples = int(fade_out_ms * sample_rate / 1000)
        
        # Fade in
        if fade_in_samples > 0 and fade_in_samples < len(samples):
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            samples[:fade_in_samples] *= fade_in_curve
        
        # Fade out
        if fade_out_samples > 0 and fade_out_samples < len(samples):
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            samples[-fade_out_samples:] *= fade_out_curve
        
        return samples
    
    @staticmethod
    def detect_silence(samples, threshold=0.01, min_silence_ms=500, sample_rate=44100):
        """Détecte les zones de silence dans l'audio"""
        if samples is None or len(samples) == 0:
            return []
        
        # Convertir le seuil et la durée minimale
        min_silence_samples = int(min_silence_ms * sample_rate / 1000)
        
        # Trouver les échantillons sous le seuil
        below_threshold = np.abs(samples) < threshold
        
        # Trouver les zones de silence continues
        silence_zones = []
        start = None
        
        for i, is_silent in enumerate(below_threshold):
            if is_silent and start is None:
                start = i
            elif not is_silent and start is not None:
                if i - start >= min_silence_samples:
                    silence_zones.append((start / sample_rate, i / sample_rate))
                start = None
        
        # Vérifier la dernière zone
        if start is not None and len(samples) - start >= min_silence_samples:
            silence_zones.append((start / sample_rate, len(samples) / sample_rate))
        
        return silence_zones


class WaveformVisualizer:
    """Visualiseur de forme d'onde"""
    
    def __init__(self, width=800, height=100):
        self.width = width
        self.height = height
        self.waveform_data = None
        self.current_position = 0
        self.total_duration = 0
    
    def load_audio(self, filepath):
        """Charge un fichier audio pour la visualisation"""
        self.waveform_data, sample_rate = AudioUtils.load_waveform_data(filepath)
        
        if self.waveform_data is not None:
            # Réduire les données pour l'affichage
            self.waveform_data = AudioUtils.downsample_waveform(
                self.waveform_data, 
                target_points=self.width
            )
            
            # Calculer la durée totale
            audio_info = AudioUtils.get_audio_info(filepath)
            if audio_info:
                self.total_duration = audio_info['duration']
    
    def draw_waveform(self, canvas, show_position=True):
        """Dessine la forme d'onde sur un canvas"""
        if self.waveform_data is None:
            return
        
        canvas.delete("waveform")
        
        # Calculer les dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        center_y = canvas_height // 2
        
        # Dessiner la forme d'onde
        points = []
        for i, amplitude in enumerate(self.waveform_data):
            x = (i / len(self.waveform_data)) * canvas_width
            y = center_y - (amplitude * center_y * 0.8)
            points.extend([x, y])
        
        if len(points) >= 4:
            canvas.create_line(points, fill="#4a8fe7", width=1, tags="waveform")
        
        # Dessiner la position actuelle
        if show_position and self.total_duration > 0:
            position_x = (self.current_position / self.total_duration) * canvas_width
            canvas.create_line(
                position_x, 0, position_x, canvas_height,
                fill="#ff4444", width=2, tags="waveform"
            )
    
    def update_position(self, current_time):
        """Met à jour la position actuelle"""
        self.current_position = current_time
    
    def get_time_from_position(self, x_position, canvas_width):
        """Convertit une position X en temps"""
        if self.total_duration > 0 and canvas_width > 0:
            return (x_position / canvas_width) * self.total_duration
        return 0