import os
import subprocess
import whisper
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from pytube import YouTube  

class SubtitleView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        video_url = request.data.get('video_url')
        language = request.data.get('language', 'en')
        word_to_find = request.data.get('word', '')

        if not file and not video_url:
            return Response({"error": "No file or URL provided"}, status=status.HTTP_400_BAD_REQUEST)

        #media directory exists
        media_dir = 'media'
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        if file:
            video_path = os.path.join(media_dir, file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        else:
            try:
                yt = YouTube(video_url)
                video_stream = yt.streams.filter(file_extension='mp4').first()
                video_path = video_stream.download(output_path=media_dir)
            except Exception as e:
                return Response({"error": f"Could not download video from URL: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        audio_path = f"{video_path[:-4]}.wav"
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", audio_path], check=True)

        try:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language=language)

            #timestamps for the word
            word_to_find_lower = word_to_find.lower()
            timestamps = []
            for segment in result["segments"]:
                text = segment["text"].lower()
                start_time = segment["start"]
                end_time = segment["end"]
                if word_to_find_lower in text:
                    timestamps.append({
                        "start": start_time,
                        "end": end_time,
                        "text": segment["text"]
                    })

            return Response(timestamps, status=status.HTTP_200_OK)

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(video_path):
                os.remove(video_path)






'''

import os
import subprocess
import whisper
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

class SubtitleView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        video_url = request.data.get('video_url')
        language = request.data.get('language', 'en')
        word_to_find = request.data.get('word', '')

        if not file and not video_url:
            return Response({"error": "No file or URL provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the media directory exists
        media_dir = 'media'
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        if file:
            video_path = os.path.join(media_dir, file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        else:
            video_response = requests.get(video_url)
            if video_response.status_code != 200:
                return Response({"error": "Could not download video from URL"}, status=status.HTTP_400_BAD_REQUEST)
            video_path = os.path.join(media_dir, 'temp_video.mp4')
            with open(video_path, 'wb') as destination:
                destination.write(video_response.content)

        # Extract audio using ffmpeg
        audio_path = f"{video_path[:-4]}.wav"
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", audio_path], check=True)

        try:
            # Perform speech recognition using Whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language=language)

            # Parse Whisper results and collect timestamps for the word
            word_to_find_lower = word_to_find.lower()
            timestamps = []
            for segment in result["segments"]:
                text = segment["text"].lower()
                start_time = segment["start"]
                end_time = segment["end"]
                if word_to_find_lower in text:
                    timestamps.append({
                        "start": start_time,
                        "end": end_time,
                        "text": segment["text"]
                    })

            return Response(timestamps, status=status.HTTP_200_OK)

        finally:
            # Clean up the audio and video files
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(video_path):
                os.remove(video_path)


'''