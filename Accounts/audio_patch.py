# import os
# import whisper.audio
# import subprocess

# # Save the original function
# original_load_audio = whisper.audio.load_audio


# def patched_load_audio(file, sr=16000):
   
#     if isinstance(file, str):
#         # Use explicit ffmpeg path for Windows
#         ffmpeg_path = r"D:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
#         cmd = [
#             ffmpeg_path,
#             "-nostdin",
#             "-threads", "0",
#             "-i", file,
#             "-f", "s16le",
#             "-ac", "1",
#             "-acodec", "pcm_s16le",
#             "-ar", str(sr),
#             "-"
#         ]
#         try:
#             out = subprocess.run(cmd, capture_output=True, check=True).stdout
#         except subprocess.CalledProcessError as e:
#             raise RuntimeError(
#                 f"Failed to load audio: {e.stderr.decode()}") from e

#         return whisper.audio.np.frombuffer(out, whisper.audio.np.int16).flatten().astype(whisper.audio.np.float32) / 32768.0
#     else:
      
#         return original_load_audio(file, sr)

# whisper.audio.load_audio = patched_load_audio
