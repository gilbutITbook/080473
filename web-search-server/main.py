import logging  # 프로그램 실행 중 발생하는 정보, 경고, 오류 메시지를 기록하기 위한 모듈
from dotenv import load_dotenv  # .env 파일에 저장된 환경 변수들을 파이썬 환경으로 불러오는 데 사용
import requests  # 외부 HTTP API에 요청을 보내고 응답을 처리하는 데 사용하는 HTTP 클라이언트 라이브러리
from mcp.server.fastmcp import FastMCP  # LangChain 기반 MCP 서버를 쉽게 구성할 수 있게 해주는 클래스
from langchain_openai import ChatOpenAI  # OpenAI GPT 모델을 LangChain 인터페이스로 사용하는 클래스

# Tavily 웹 검색 API에서 사용할 키 설정 (실제로는 안전하게 환경 변수로 관리하는 것이 권장됨)
TAVILY_API_KEY = "tvly
# OpenAI GPT 모델 호출을 위한 키 설정 (LangChain에서 사용됨)
OPENAI_API_KEY = "sk"  # OpenAI API 키 (예시 문자열, 실제로는 유효한 API 키로 대체해야 함)

# OpenAI GPT 모델 인스턴스 초기화
# model="gpt-4"은 GPT-4 모델을 사용하겠다는 의미이고, api_key를 명시적으로 전달
llm = ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY)

# MCP 서버 생성 - 서버 이름은 "WebSearch"
# 이 이름은 도구 목록 조회 시 식별자 역할을 하며, 여러 MCP 서버를 구분하는 데 사용됨
mcp = FastMCP("WebSearch")

# Tavily 웹 검색 API를 호출하는 함수 정의
# 사용자로부터 입력받은 query(검색어)를 Tavily API에 전달하고, 그 결과를 정리해서 반환
def search_web_tavily(query: str) -> str:
    url = "https://api.tavily.com/search"  # Tavily API의 엔드포인트
    headers = {"Content-Type": "application/json"}  # 요청 헤더: JSON 형식의 데이터를 전송한다는 의미
    payload = {
        "api_key": TAVILY_API_KEY,  # 사용자 인증을 위한 키
        "query": query,  # 사용자가 검색하고자 하는 키워드 또는 문장
        "search_depth": "basic",  # 검색의 깊이 설정 (basic은 빠른 검색, deep은 더 정교한 검색)
        "include_answer": True,  # Tavily가 제공하는 요약 또는 해석 포함 여부
        "max_results": 5  # 검색 결과에서 최대 몇 개를 가져올지 지정
    }

    try:
        # POST 방식으로 Tavily API 호출
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTP 에러가 발생했을 경우 예외를 발생시킴

        # 응답 본문을 JSON으로 변환 후 "results" 항목 추출 (리스트 형태)
        results = response.json().get("results", [])

        # 결과가 없을 경우 사용자에게 안내
        if not results:
            return "검색 결과가 없습니다."

        # 각 결과 항목의 제목과 내용을 합쳐 하나의 문자열로 구성 (결과 여러 개를 줄 구분으로 연결)
        contents = "\n\n".join([f"{r['title']}\n{r['content']}" for r in results])
        return contents  # 완성된 검색 결과 문자열 반환

    except Exception as e:
        # 오류가 발생한 경우 로그에 에러 메시지 출력
        logging.error(f"Tavily 검색 오류: {e}")
        return "검색 중 오류가 발생했습니다."  # 사용자에게는 일반적인 오류 메시지를 반환

# MCP 도구로 등록 - GPT가 직접 호출할 수 있는 도구로 사용됨
# 외부 클라이언트(Cursor, Claude 등)에서 'web_search'라는 이름으로 호출 가능
@mcp.tool()
async def web_search(query: str) -> str:
    """웹에서 검색한 결과를 요약해 제공합니다."""  # LangChain 또는 클라이언트가 이 도구의 역할을 설명할 때 사용됨

    # 검색 요청이 들어왔음을 로그에 기록
    logging.info(f"검색 요청: {query}")

    # Tavily API를 통해 검색 실행
    content = search_web_tavily(query)

    # 검색 결과 내용을 기반으로 GPT-4가 요약문을 생성
    # ainvoke()는 비동기 GPT 호출 (LangChain에서 await를 지원)
    summary = await llm.ainvoke(f"다음 검색 결과를 한 문단으로 요약해줘:\n\n{content}")

    return summary  # 요약된 결과를 클라이언트에게 반환

# MCP 서버 실행 블록
# 이 파일이 단독 실행될 경우 MCP 서버를 stdio 방식으로 실행함
# stdio는 Cursor나 Claude Desktop에서 subprocess 방식으로 이 서버를 연결할 때 사용하는 통신 방식
if __name__ == "__main__":
    mcp.run(transport="stdio")
