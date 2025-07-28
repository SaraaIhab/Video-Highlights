import gradio as gr 
from backend import transcribe, summarize, videoCreation

def generate(number,video):
    text = transcribe(video)
    summary=summarize(text, number) 
    outpath=videoCreation(summary, video)
    return outpath


demo = gr.Interface(
    fn=generate,
    inputs=[
        gr.Slider(minimum=0, maximum=10, label="Number (unused)"),
        gr.Video(label="Upload video")
    ],
    outputs=gr.Gallery(label="Highlight Clips")
)
demo.launch()
