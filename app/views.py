from transformers import pipeline
from django.shortcuts import render
import os
from django.shortcuts import render   # ✅ ye hona chahiye
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage

# ⚠️ model load ek baar hi hona chahiye (global)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    if not text or len(text.strip()) < 30:
        return "Text too short to summarize"

    # 🔥 chunking (important for long text)
    max_chunk = 500
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]

    final_summary = []

    for chunk in chunks:
        result = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        final_summary.append(result[0]['summary_text'])

    return " ".join(final_summary)


# ✅ OPTIONAL: Whisper (abhi OFF rakha hai for speed)
def speech_to_text(file_path):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]


# ✅ MAIN VIEW (FINAL)
def index(request):
    # 🔥 FEEDBACK FETCH KAR
    feedbacks = Feedback.objects.order_by('-created_at')[:4]

    # 👉 POST request → AJAX call
    if request.method == "POST":
        text_input = request.POST.get("text_input")
        file = request.FILES.get("file")

        try:
            if text_input:
                summary = summarize_text(text_input)
                return JsonResponse({"summary": summary})

            elif file:
                fs = FileSystemStorage(location="media/")
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)

                if file_path.endswith(".mp4"):
                    import moviepy.editor as mp
                    video = mp.VideoFileClip(file_path)
                    audio_path = file_path.replace(".mp4", ".wav")
                    video.audio.write_audiofile(audio_path)
                    file_path = audio_path

                transcript = speech_to_text(file_path)
                summary = summarize_text(transcript)

                return JsonResponse({"summary": summary})

            return JsonResponse({"summary": "Please provide text or file"})

        except Exception as e:
            return JsonResponse({"summary": f"Error: {str(e)}"})

    # 🔥 IMPORTANT: feedbacks pass kar
    return render(request, "index.html", {
        "feedbacks": feedbacks
    })
from django.shortcuts import render, redirect
from .models import Feedback

def feedback_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")

        if name and message:
            Feedback.objects.create(name=name, message=message)

        return redirect("/")  # submit ke baad home

    return render(request, "feedback.html")