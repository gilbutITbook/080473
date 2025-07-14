import os  # 파일 경로 생성, 디렉터리 순회, 파일 정보 조회 등 운영체제 관련 작업을 위한 표준 모듈
import logging  # 코드 실행 도중 발생하는 정보, 경고, 오류 등을 로그로 기록할 수 있는 모듈
from datetime import datetime  # 유닉스 타임스탬프를 사람이 읽을 수 있는 날짜/시간 형식으로 변환하는 데 사용하는 모듈
from mcp.server.fastmcp import FastMCP  # LangChain 기반 MCP 서버 생성을 위한 핵심 클래스

# 로그 출력 형식 설정: 로그 수준이 INFO 이상인 로그를 출력하도록 설정
# 로그는 검색 시작, 오류 발생 등 주요 이벤트를 기록하는 데 사용됨
logging.basicConfig(level=logging.INFO)

# MCP 서버 인스턴스 생성 (이름은 "File-Search"로 설정됨, 클라이언트에서 이 이름으로 도구를 식별 가능)
mcp = FastMCP("File-Search")

# 검색의 기준이 될 최상위 디렉터리 설정 (Windows의 D 드라이브 전체를 대상으로 검색함)
ROOT_DIR = "D:/"

# 파일 검색 함수 정의
# 입력한 키워드가 포함된 파일명을 ROOT_DIR 아래에서 찾아 목록을 반환함
# 결과는 최대 max_results 개수까지만 수집함
def search_files(keyword: str, base_path: str = ROOT_DIR, max_results: int = 20) -> list[dict]:
    results = []  # 검색 결과(딕셔너리 형태)를 저장할 리스트 초기화

    # os.walk()를 통해 base_path 하위의 모든 폴더 및 파일들을 순회
    for dirpath, _, filenames in os.walk(base_path):
        # 현재 폴더에 있는 모든 파일 이름을 확인
        for fname in filenames:
            # 파일 이름에 키워드가 포함되어 있는지 확인 (대소문자 구분 없이 검색)
            if keyword.lower() in fname.lower():
                # 전체 파일 경로 생성
                fpath = os.path.join(dirpath, fname)
                try:
                    # 파일의 크기, 생성일 등 메타데이터 가져오기
                    stat = os.stat(fpath)
                    # 결과 리스트에 정보 추가
                    results.append({
                        "파일명": fname,  # 파일 이름
                        "경로": fpath,  # 전체 파일 경로
                        "크기(Bytes)": stat.st_size,  # 파일 크기 (바이트 단위)
                        "생성일": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),  # 생성일(사람이 읽을 수 있는 형식)
                    })
                    # 결과가 최대 개수에 도달했으면 즉시 반환
                    if len(results) >= max_results:
                        return results
                except Exception as e:
                    # 파일 접근 중 오류가 발생하면 경고 로그에 기록하고 무시함
                    logging.warning(f"파일 접근 오류: {fpath} - {e}")
    # 모든 파일 탐색을 마친 후 결과 리스트를 반환
    return results

# 위에서 정의한 search_files 함수를 MCP 도구로 등록
# 클라이언트(GPT 또는 외부 MCP 클라이언트)에서 이 함수를 호출할 수 있게 됨
@mcp.tool()
def find_file(keyword: str) -> str:
    """D 드라이브에서 파일명을 기준으로 키워드에 해당하는 파일을 검색합니다."""
    # 검색 시작 로그 출력
    logging.info(f"🔍 '{keyword}' 키워드로 파일 검색 시작")
    
    # 검색 함수 호출
    found = search_files(keyword)

    # 검색 결과가 없을 경우 사용자에게 안내 메시지 반환
    if not found:
        return f"'{keyword}'에 해당하는 파일을 찾을 수 없습니다."

    # 검색된 파일 리스트를 보기 좋은 문자열 형태로 변환하여 반환
    # 각 파일에 대해: 파일명, 크기, 경로를 포함한 줄을 생성
    return "\n".join([f"📄 {f['파일명']} ({f['크기(Bytes)']} Bytes) - {f['경로']}" for f in found])

# 메인 프로그램 블록
# 이 파일이 직접 실행되는 경우 MCP 서버를 stdio 기반으로 실행함
# Cursor, Claude Desktop, Smithery 등에서 subprocess로 연결 가능
if __name__ == "__main__":
    mcp.run(transport="stdio")
