from mcp.server.fastmcp import FastMCP  # FastMCP는 MCP 서버를 빠르게 설정할 수 있는 클래스
import logging                          # 로깅 모듈: 실행 정보를 출력하기 위해 사용
import asyncio                          # 비동기 서버 실행을 위해 사용

# 로깅 설정: INFO 레벨 이상의 메시지를 콘솔에 출력
logging.basicConfig(level=logging.INFO)

# MCP 서버 초기화: "Math"는 서버 이름으로, 클라이언트에 노출됨
mcp = FastMCP("Math")

# 더하기 도구 정의 및 MCP에 등록
@mcp.tool()
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    logging.info(f"Adding {a} + {b}")  # 로그에 연산 내용 출력
    return a + b                       # 두 수를 더한 값을 반환

# 빼기 도구 정의 및 MCP에 등록
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """두 숫자를 뺍니다."""
    logging.info(f"Subtracting {a} - {b}")  # 로그에 연산 내용 출력
    return a - b                            # 두 수를 뺀 값을 반환

# MCP 서버 실행
if __name__ == "__main__":
    asyncio.run(mcp.run(transport="stdio"))  # MCP 서버를 stdio 방식으로 실행 (ex. Cursor나 Claude Desktop에서 연결 가능)
