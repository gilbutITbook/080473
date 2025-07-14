import os  # 운영체제와 상호작용하기 위한 표준 모듈로, 파일 및 디렉터리 경로 구성, 파일 탐색, 파일 정보 조회 등에 사용
import logging  # 코드 실행 중에 발생하는 정보, 경고, 오류 등의 메시지를 기록하거나 출력하는 데 사용되는 로깅 모듈
import sys  # 시스템 관련 기능을 제공하는 모듈로, 여기서는 표준 에러 출력(sys.stderr)에 디버그 메시지를 출력하는 데 사용
from datetime import datetime  # 유닉스 타임스탬프를 사람이 읽을 수 있는 날짜와 시간 형식으로 변환할 때 사용되는 모듈
from typing import List, Dict  # 함수의 입력값과 반환값에 타입 힌트를 제공하기 위한 모듈
from mcp.server.fastmcp import FastMCP  # 랭체인 기반 MCP 서버를 간단하게 구성하고, 사용자 정의 도구(tool)를 등록할 수 있는 클래스.
import asyncio  # 비동기 처리를 위한 표준 모듈

# MCP 서버 인스턴스를 생성, 서버의 이름은 "File-Search"로 설정되어 있으며,
# 이는 MCP 클라이언트에서 도구 목록을 조회하거나 호출할 때 식별자로 사용됨
mcp = FastMCP("File-Search")

# 로깅 레벨을 INFO로 설정하여, info 이상의 로그 메시지를 출력
# 이 설정을 통해 이후 logging.info(), warning(), error() 등의 메시지가 콘솔에 출력
logging.basicConfig(level=logging.INFO)

# MCP 서버가 시작되었음을 알리는 디버그 메시지를 표준 에러(stderr)로 출력
# 표준 출력(stdout)이 아닌 에러 스트림을 사용하면, 결과 출력과 디버깅 로그를 구분할 수 있어 개발 및 테스트에 유용
print("[DEBUG] MCP server starting...", file=sys.stderr)

# 파일 검색의 기준이 될 루트 경로를 설정
# 여기서는 D 드라이브 전체 대신, 사용자의 "Documents" 폴더로 범위를 제한하여
# 보안상 안전하고 검색 속도도 빠르게 할 수 있도록 구성
# 해당 경로는 본인이 검색하고자 하는 위치로 변경
ROOT_DIR = "C:/Users/JYSEO/Documents"

# 키워드가 포함된 파일을 찾는 동기 방식의 함수
# base_path 하위 폴더를 재귀적으로 순회하며, 파일명에 주어진 keyword가 포함된 파일들을 찾아 리스트로 반환
# 최대 결과 개수는 max_results로 제한되며, 기본값은 20
def search_files(keyword: str, base_path: str = ROOT_DIR, max_results: int = 20) -> List[Dict]:
    results = []  # 검색된 파일 정보를 저장할 리스트

    # os.walk()는 지정된 경로의 모든 하위 디렉터리를 포함하여 순회하며
    # 현재 경로(dirpath), 하위 디렉터리 리스트(_), 그리고 파일 리스트(filenames)를 반환
    for dirpath, _, filenames in os.walk(base_path):
        for fname in filenames:  # 해당 경로에 존재하는 모든 파일을 하나씩 확인
            if keyword.lower() in fname.lower():  # 파일명에 키워드가 포함되어 있는지 대소문자를 무시하고 검사
                fpath = os.path.abspath(os.path.join(dirpath, fname))  # 상대 경로를 절대 경로로 변환하여 전체 경로를 구성
                try:
                    stat = os.stat(fpath)  # os.stat()을 통해 파일의 메타정보(크기, 생성시간 등)를 가져옴
                    results.append({
                        "파일명": fname,
                        "경로": fpath,
                        "크기(Bytes)": stat.st_size,
                        "생성일": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
                    })  # 파일명, 경로, 크기, 생성일을 딕셔너리 형태로 정리하여 리스트에 추가

                    if len(results) >= max_results:  # 결과 개수가 지정한 최대값에 도달하면 바로 리스트를 반환
                        return results
                except Exception as e:
                    # 파일에 접근할 수 없는 경우(예: 권한 문제, 손상된 파일 등) 경고 메시지를 로그로 남기고 해당 파일은 건너뜀
                    logging.warning(f"파일 접근 오류: {fpath} - {e}")
    return results  # 전체 검색이 끝난 뒤 결과 리스트를 반환

# MCP에 등록할 도구(tool)를 정의, 랭체인 또는 Cursor, Claude 등에서 호출 가능한 외부 호출형 
@mcp.tool()
async def find_file(keyword: str) -> str:
    """Documents 폴더에서 키워드에 해당하는 파일을 검색합니다."""  # 도구 설명으로, 사용자 인터페이스나 로그에 표시

    logging.info(f"'{keyword}' 키워드로 파일 검색 시작")  # 검색 시작 로그를 출력

    loop = asyncio.get_event_loop()  # 현재 실행 중인 이벤트 루프를 가져옴
    found = await loop.run_in_executor(None, search_files, keyword)  # search_files 함수는 동기 함수이므로, run_in_executor를 사용해 별도 스레드에서 실행

    if not found:  # 검색 결과가 비어 있다면
        return f"'{keyword}'에 해당하는 파일을 찾을 수 없습니다."  # 사용자에게 파일이 없음을 알리는 메시지를 반환

    # 검색된 파일 리스트를 문자열로 변환
    # 각 항목은 파일명, 파일 크기, 경로를 포함하며 보기 좋게 줄바꿈하여 구성
    return "\n".join([f"{f['파일명']} ({f['크기(Bytes)']} Bytes) - {f['경로']}" for f in found])

# 이 Python 파일이 직접 실행되는 경우에만 MCP 서버를 실행
# transport="stdio"는 MCP 서버와 클라이언트(Cursor, Claude 등)가 표준 입력/출력을 통해 통신할 수 있도록 설정하는 방식
if __name__ == "__main__":
    asyncio.run(mcp.run(transport="stdio"))  # MCP 서버를 비동기적으로 실행
