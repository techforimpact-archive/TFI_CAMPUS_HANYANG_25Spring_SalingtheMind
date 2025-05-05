##openai 잘 실행 되는지 확인용 코드인데... 결제를 안해서 안돌아가요 으악악

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "너는 위로하는 말 잘하는 AI야."},
        {"role": "user", "content": "슬프고 우울한 하루를 보냈어. 짧게 위로해줘."}
    ]
)

print(response.choices[0].message.content)
