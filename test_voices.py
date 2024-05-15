import requests
import config

text = ""  # Текст для тестирования голоса

r = requests.post("https://zvukogram.com/index.php?r=api/text", data={
    "token": config.Zvukogram.token,
    "email": config.Zvukogram.email,
    "voice": config.Zvukogram.voice,
    "text": text,
    "speed": config.Zvukogram.speed
})
print(r.json()['file'])
