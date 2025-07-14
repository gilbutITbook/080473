import os
from openai import OpenAI

# 방법 1: 코드 내에서 직접 키 입력
client = OpenAI(api_key="sk-") # OpenAI 키 입력

# Function Calling용 함수 정의
functions = [
    {
        "name": "get_current_weather",
        "description": "현재 날씨를 조회합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "날씨를 알고 싶은 도시 이름"
                }
            },
            "required": ["location"]
        }
    }
]

# 대화 메시지
messages = [
    {"role": "user", "content": "서울의 날씨 알려줘"}
]

# GPT 호출
response = client.chat.completions.create(
    model="gpt-4",  # 또는 gpt-3.5-turbo-1106 이상
    messages=messages,
    functions=functions,
    function_call="auto"
)

# 응답 출력
print(response.choices[0].message)
