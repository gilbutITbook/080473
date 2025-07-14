import os
import json
import requests
from openai import OpenAI

# 환경 변수 또는 직접 키 입력
openai_api_key = "sk-" # OpenAI 키 입력
weather_api_key = "" # OpenWeather 키 입력

client = OpenAI(api_key=openai_api_key)

# Function 정의 (OpenAI에 알려줄 함수 명세)
functions = [
    {
        "name": "get_current_weather",
        "description": "현재 날씨를 조회합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "도시 이름"},
            },
            "required": ["location"],
        },
    }
]

# 사용자 질문
messages = [
    {"role": "user", "content": "서울 날씨 어때?"}
]

# Step 1: GPT에게 함수 호출 요청 생성시킴
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    functions=functions,
    function_call="auto"
)
message = response.choices[0].message

if message.function_call:
    function_name = message.function_call.name
    arguments = json.loads(message.function_call.arguments)
    location = arguments["location"]

    # OpenWeatherMap은 영어 도시명을 더 잘 인식함 → 한글일 경우 영문 변환 권장
    # 간단한 매핑 예시
    korean_to_english = {
        "서울": "Seoul",
        "부산": "Busan",
        "대구": "Daegu",
        "인천": "Incheon",
        "광주": "Gwangju",
        "대전": "Daejeon",
        "울산": "Ulsan",
        "제주": "Jeju"
    }
    location_eng = korean_to_english.get(location, location)  # 기본은 그대로

    # Step 3: 실제 날씨 API 호출
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location_eng,
        "appid": weather_api_key,
        "units": "metric",  # 섭씨 온도
        "lang": "kr"
    }

    weather_response = requests.get(weather_url, params=params)
    weather_data = weather_response.json()

    # Step 4: 실패 시 처리
    if "main" not in weather_data:
        print("❌ 날씨 정보를 가져오는 데 실패했습니다.")
        print("에러 메시지:", weather_data.get("message", "알 수 없는 오류"))
        print("전체 응답:", weather_data)
        exit()

    # Step 5: 결과 구성
    weather_result = {
        "location": location_eng,
        "temperature": weather_data["main"]["temp"],
        "condition": weather_data["weather"][0]["description"]
    }

    # Step 6: GPT에게 도구 실행 결과 전달
    messages.append(message)  # GPT가 만든 function_call 메시지
    messages.append({
        "role": "function",
        "name": function_name,
        "content": json.dumps(weather_result)
    })

    final_response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    print("\n 최종 응답:")
    print(final_response.choices[0].message.content)

else:
    print("GPT가 함수 호출을 요청하지 않았습니다.")





