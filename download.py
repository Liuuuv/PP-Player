import yt_dlp
from pydub import AudioSegment

url = "https://youtu.be/-NKaXqLhN3c?feature=shared"  # Remplacez par l'URL de votre vidéo
output_path = "D:/YTDownloads"
output_format = "wav"  # Choisissez "mp3" ou "wav"

# Étape 1 : Télécharger l'audio en format original
ydl_opts = {
    'format': 'bestaudio/best',                     # Télécharger la meilleure qualité audio
    'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Modèle de nom de fichier
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    downloaded_file = ydl.prepare_filename(info)  # Récupère le nom du fichier téléchargé

# Étape 2 : Convertir le fichier dans le format souhaité
output_file = downloaded_file.rsplit('.', 1)[0] + f".{output_format}"  # Nom du fichier de sortie
audio = AudioSegment.from_file(downloaded_file)       # Charger le fichier téléchargé

if output_format == "mp3":
    audio.export(output_file, format="mp3", bitrate="192k")  # Exporter en MP3 avec un bitrate de 192kbps
elif output_format == "wav":
    audio.export(output_file, format="wav")  # Exporter en WAV (qualité non compressée)

print(f"Conversion terminée. Le fichier {output_format.upper()} est disponible ici : {output_file}")
