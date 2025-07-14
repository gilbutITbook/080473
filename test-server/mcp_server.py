from mcp.server.fastmcp import FastMCP, Context  # MCP 서버 및 도구 실행 시 context 정보 처리
from langchain_openai import ChatOpenAI          # OpenAI의 LLM을 LangChain 인터페이스로 사용하기 위한 클래스

import os
os.environ["OPENAI_API_KEY"] = "sk"  # OpenAI API 키를 환경변수에 저장 (발급 받았던 sk로 시작하는 키 입력)

# MCP 서버 초기화 ("GPT-4o MCP"는 서버 식별 이름이며, 클라이언트에 표시됨)
mcp = FastMCP("GPT-4o MCP")

# GPT-4o에 질문을 보내는 도구 정의
@mcp.tool()
async def ask_gpt(ctx: Context, question: str) -> str:
    # GPT-4o 모델 인스턴스 생성 (온도는 창의성 조절, 0.3은 약간의 다양성 허용)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    # 사용자의 질문을 모델에 전달하고 결과를 반환
    return llm.invoke(question)

# MCP 서버 실행 (stdio 표준 입출력 기반으로 통신)
if __name__ == "__main__":
    mcp.run(transport="stdio")
