import logging  # 프로그램 실행 중 정보, 경고, 오류 등의 메시지를 기록하거나 콘솔에 출력하기 위한 표준 파이썬 모듈
import asyncio  # 비동기 처리를 위한 표준 모듈로, MCP 서버를 실행할 때 이벤트 루프 기반으로 동작
from mcp.server.fastmcp import FastMCP  # MCP 서버를 간단하게 생성하고 도구(tool)를 등록할 수 있는 LangChain 기반의 클래스

logging.basicConfig(level=logging.INFO)  # 로깅 레벨을 INFO로 설정하여 정보, 경고, 에러 메시지를 출력 
 
mcp = FastMCP("Math")  # MCP 서버 인스턴스를 생성합니다. 이름은 "Math"로 설정되어 있으며, 이 이름은 도구 식별자 역할을 함, 예를 들어 Cursor에서 연결된 MCP 서버 목록 중 "Math"라는 이름으로 표시될 수 있음

@mcp.tool()  # 이 데코레이터는 아래의 add 함수를 MCP 서버에 도구(tool)로 등록
def add(a, b) -> int:
    """더하기"""  # 도구 설명
    try:
        a = int(a)  # 입력값 a를 정수형으로 변환,. 문자열로 입력된 숫자도 처리할 수 있도록 함
        b = int(b)  # 입력값 b도 정수형으로 변환
        logging.info(f"Adding {a} and {b}")  # 어떤 값을 더하는지 로그로 기록
        return a + b  # 두 값을 더한 결과를 반환
    except Exception as e:  # 변환 오류 또는 연산 중 에러가 발생했을 경우
        logging.error(f"Invalid input in add: {a}, {b} - {e}")  # 에러 내용을 로그에 출력
        raise  # 에러를 다시 발생시켜 호출한 쪽에서 예외를 인식할 수 있게 함

@mcp.tool()  # Subtract 함수도 MCP 도구로 등록
def Subtract(a, b) -> int:
    """빼기"""  # 이 도구는 두 숫자의 차를 계산
    try:
        a = int(a)  # 입력값 a를 정수로 변환
        b = int(b)  # 입력값 b를 정수로 변환
        logging.info(f"Subtracting {a} and {b}")  # 어떤 값을 빼는지 로그에 기록
        return a - b  # 두 수의 차를 반환
    except Exception as e:  # 에러가 발생한 경우
        logging.error(f"Invalid input in subtract: {a}, {b} - {e}")  # 에러 내용을 로그로 남김
        raise  # 예외를 다시 발생시켜 오류 처리 흐름이 유지되도록 함

if __name__ == "__main__":  # 이 파일이 메인으로 실행될 때만 아래 코드가 실행
    asyncio.run(mcp.run(transport="stdio"))  # MCP 서버를 asyncio 기반으로 실행
