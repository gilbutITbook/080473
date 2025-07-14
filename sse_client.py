import asyncio  # 비동기 함수 실행을 위한 모듈
import sys      # 명령줄 인자 처리용
import json     # JSON 문자열 파싱

from mcp import ClientSession  # MCP 클라이언트 세션 객체
from mcp.client.sse import sse_client  # SSE 방식으로 MCP 서버와 통신하는 클라이언트

# 비동기 메인 함수 정의
async def main():
    # 명령줄 인자 확인 (서버 URL이 전달되었는지 검사)
    if len(sys.argv) < 2:
        print("Usage: python client.py http://127.0.0.1:3000/sse")  # 사용법 안내
        return

    url = sys.argv[1]  # 명령줄에서 전달된 서버 주소 사용
    print(f"[클라이언트] 서버에 SSE 연결 시도 중... ({url})")

    # SSE 클라이언트를 통해 서버에 연결
    async with sse_client(url) as (reader, writer):
        # MCP 프로토콜 세션 초기화
        async with ClientSession(reader, writer) as session:
            await session.initialize()  # 초기 MCP handshake 수행

            print("MCP Chat Client 시작됨. 'quit' 입력 시 종료됩니다.")
            
            # 사용자 입력 루프
            while True:
                user_input = input("\nQuery: ").strip()  # 사용자 질문 입력 받기
                if user_input.lower() == "quit":  # 'quit' 입력 시 종료
                    break

                try:
                    # MCP 서버에 "chat" 도구를 호출하고 사용자 입력 전달
                    response = await session.call_tool("chat", {"input": user_input})

                    # 응답의 content가 문자열인 경우 JSON인지 판별
                    if isinstance(response.content, str):
                        try:
                            data = json.loads(response.content)  # JSON 파싱 시도
                            print("\n GPT-4o 응답:\n" + data["content"])  # JSON 구조일 경우 content 필드 출력
                        except json.JSONDecodeError:
                            # 그냥 텍스트일 경우 그대로 출력
                            print("\n GPT-4o 응답:\n" + response.content)
                    # content가 dict 타입이면 content 필드 추출
                    elif isinstance(response.content, dict):
                        print("\n GPT-4o 응답:\n" + response.content.get("content", 
                                                            str(response.content)))
                    else:
                        # 그 외 타입은 문자열로 변환하여 출력
                        print("\n GPT-4o 응답:\n" + str(response.content))

                except Exception as e:
                    # 예외 발생 시 메시지 출력
                    print(f"오류 발생: {e}")

# 엔트리 포인트: main() 비동기 함수 실행
if __name__ == "__main__":
    asyncio.run(main())
