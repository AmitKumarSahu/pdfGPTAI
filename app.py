import json
from tempfile import _TemporaryFileWrapper

import gradio as gr
from api import *

# List to store previous questions and answers
chat_history = []

def ask_api(
    url: str,
    file: _TemporaryFileWrapper,
    question: str,
    openAI_key: str,
) -> str:

    if url.strip() == '' and file is None:
        return '[ERROR]: Both URL and PDF are empty. Provide at least one.'

    if url.strip() != '' and file is not None:
        return '[ERROR]: Both URL and PDF are provided. Please provide only one (either URL or PDF).'

    if question.strip() == '':
        return '[ERROR]: Question field is empty'

    _data = {
        'question': question,
        'envs': {
            'OPENAI_API_KEY': openAI_key,
        },
    }

    if url.strip() != '':
        r = ask_url(url, question,openAI_key)
    else:
        with open(file.name, 'rb') as f:
            r = ask_file(file, question ,openAI_key)

    # Store the question and its answer in chat_history
    chat_history.append({'question': question, 'answer': r})

    return r


def chat_interface(openAI_key, pdf_url, file, question):
    if question.strip() == '':
        return '[ERROR]: Question field is empty'

    answer = ask_api(pdf_url, file, question, openAI_key)

    # Format the previous questions and answers for display
    chat_display = "\n".join(
        [f"<strong>User:</strong> {qa['question']}<br><strong>ChatGPT:</strong> {qa['answer']}<br>" for qa in chat_history]
    )

    return f"<strong>User:</strong> {question}<br><strong>ChatGPT:</strong> {answer}<br><br><strong>Chat History:</strong><br>{chat_display}"


title = 'PDF GPT - Chat Interface'
description = """PDF GPT allows you to chat with your PDF file using Universal Sentence Encoder and Open AI. It gives hallucination-free responses as the embeddings are better than OpenAI. The returned response can even cite the page number in square brackets([]) where the information is located, adding credibility to the responses and helping to locate pertinent information quickly."""

iface = gr.Interface(
    fn=chat_interface,
    inputs=[
        gr.Textbox(label='User:', placeholder='Enter your message here...', lines=2),
        gr.Textbox(label='ChatGPT:', readonly=True, placeholder='ChatGPT response...', lines=2),
        gr.Textbox(label='OpenAI API key:', type='password'),
        gr.Textbox(label='PDF URL:', placeholder='Enter PDF URL (optional)'),
        gr.File(label='Upload PDF:', file_types=['.pdf'], placeholder='Upload PDF file (optional)'),
    ],
    outputs=gr.HTML(label='Chat History and Answer:', html=True),
    title=title,
    description=description,
    examples=[
        ['What is the capital of France?'],
        ['Can you tell me about the history of artificial intelligence?'],
    ],
    allow_flagging=False,
    allow_screenshot=False,
)

iface.launch(share=True)
