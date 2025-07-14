from fastmcp import FastMCP  # FastMCP: 간단한 MCP 서버를 빠르게 생성하기 위한 클래스

# MCP 서버 인스턴스를 생성 ("더하기"는 서버의 이름이며 클라이언트에서 식별용으로 사용됨)
mcp = FastMCP("더하기")

# MCP 도구(tool)로 등록된 함수 정의
@mcp.tool()
def add(a: int, b: int) -> int:
    """a와 b를 더하기"""
    return a + b  # 두 숫자를 더한 결과를 반환

# 메인 진입점: 이 파일이 직접 실행될 경우 MCP 서버 시작
if __name__ == "__main__":
    mcp.run()  # MCP 서버를 실행 (기본 transport는 stdio 또는 서버 설정에 따름)
