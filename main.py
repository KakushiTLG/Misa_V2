import os
import time
import openai
import json
import requests
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam
from whisper_mic import WhisperMic
from pathlib import Path
import config

client = openai.Client(api_key=config.OpenAI.token)
speech_file_path = Path(__file__).parent / "answer.mp3"
mic = WhisperMic()

with open("preset.txt", "r", encoding="UTF-8") as preset_file:
    preset = preset_file.read()
conversation_history = [{"role": "system", "content": preset},]
preloaded_context = json.load(open("context.json", "r", encoding="UTF-8"))


class Speecher:

    @staticmethod
    def request_speech(text):
        r = requests.post("https://zvukogram.com/index.php?r=api/text", data={
            "token": config.Zvukogram.token,
            "email": config.Zvukogram.email,
            "voice": config.Zvukogram.voice,
            "text": text,
            "speed": config.Zvukogram.speed
        })
        return r.json()['file']


class Context:
    context = preloaded_context

    @staticmethod
    def save_context():
        json.dump(Context.context, open("context.json", "w", encoding="UTF-8"))

    @staticmethod
    def get_context():
        return Context.context[-10:]

    @staticmethod
    def update_context(new_obj):
        Context.context = new_obj
        Context.save_context()
        return

    @staticmethod
    def append_context(obj):
        Context.context.append(obj)
        Context.save_context()
        return


class Request:

    @staticmethod
    def set_request(text):
        new_context = []
        msgs = [ChatCompletionSystemMessageParam(role="system", content=preset)]
        for msg in Context.get_context():
            if msg['role'] == "user":
                msgs.append(ChatCompletionUserMessageParam(content=msg['content'], role='user'))
            else:
                msgs.append(ChatCompletionAssistantMessageParam(content=msg['content'], role='assistant'))
            new_context.append(msg)
        new_context.append({"role": "user", "content": text})
        msgs.append(ChatCompletionUserMessageParam(content=text, role='user'))
        Context.update_context(new_context)
        return Request.ask_gpt(msgs)

    @staticmethod
    def ask_gpt(request):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=request,
            max_tokens=100
        )
        assistant_response = response.choices[0].message.content
        Context.append_context({"role": "assistant", "content": assistant_response})
        return assistant_response


def action(text):
    answer = Request.set_request(text)
    print("Ответ:          " + answer)
    audio_answer_url = Speecher.request_speech(answer)
    os.system(f"ffplay -v 0 -nodisp -autoexit {audio_answer_url}")


def get_speech():
    result = mic.listen()
    print([x for x in config.Settings.triggers], [x in result.lower() for x in config.Settings.triggers])
    if any([x in result.lower() for x in config.Settings.triggers]):
        return result
    return False


while True:
    value = None
    try:
        value = get_speech()
    except:
        time.sleep(0.1)
    if value:
        action(value)
