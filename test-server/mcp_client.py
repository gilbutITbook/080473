import asyncio
from mcp_server import ask_gpt  # MCP 도구로 정의된 ask_gpt 함수를 직접 가져옴

# 클라이언트 함수: 질문을 보내고 응답을 출력
async def client():
    question = "mcp와 agent의 관계는?"
    result = await ask_gpt(None, question)  # MCP context는 사용되지 않으므로 None 전달
    print("답변:", result)

# 비동기 함수 실행
asyncio.run(client())
