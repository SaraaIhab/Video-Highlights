import getpass
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from moviepy import * 
import json


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
mode =  OpenAI(api_key=api_key)

if not api_key:
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

tools=[
    {
        "type": "function",
        "function": {
            "name": "highlights",
            "description": "Get the highlights of the video",
            "parameters": {
                "type": "object",
                "properties": {
                    "highlights":{
                        "type": "array",
                        "items":{
                            "type": "object",
                            "properties": {
                                "start": {"type": "number", "description": "The start time of the highlight"},
                                "end": {"type": "number", "description": "The end time of the highlight"},
                                "summary": {"type": "string", "description": "The summary of the highlight"}
                            }
                        },
                        "required": ["start", "end", "summary"]
                    }
                },
                "required": ["highlights"]
            }
        }
    }
]


def transcribe(audio_file_path):
    with open(audio_file_path, "rb") as f:
        transcript = mode.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json"
        )
        return transcript.segments

def summarize(segments, number):
    transcript_str = "\n".join([f"[{s.start:.1f}-{s.end:.1f}] {s.text}" for s in segments])
    summarization= mode.chat.completions.create(
        model="gpt-4.1-mini",
     messages=[
        {
            "role": "system",
            "content": "You're a helpful assistant that summarizes video transcripts and selects key moments."
        },
        {
            "role": "user",
            "content": f"""
Here is a transcript of a video. Find the {number} most impactful or useful moments in the video. 
Return their start and end times (in seconds), and write a short title/summary for each.

Transcript:
{transcript_str}
"""}],
tools=tools,
tool_choice={"type": "function", "function": {"name": "highlights"}}
)
    arguments = json.loads(summarization.choices[0].message.tool_calls[0].function.arguments)
    return arguments["highlights"]

def videoCreation(summary, video):
    outpath=[]
    id=0
    video_clip = VideoFileClip(video)
    for i in summary:
        id+=1
        out_path = f"highlight_{id+1}.mp4"
        section=video_clip.subclipped(i['start'], i['end']).write_videofile(out_path)
        outpath.append(out_path)
    return outpath


    
