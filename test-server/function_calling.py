import os
os.environ["OPENAI_API_KEY"] = "sk-"  # OpenAI API 키를 환경 변수로 설정 (보안상 실제 키는 'sk-...' 형태로 입력해야 함)

from langchain_core.tools import tool  # 랭체인인에서 툴(도구)을 만들기 위한 데코레이터 임포트
from langchain_openai import ChatOpenAI  # OpenAI LLM을 랭체인인에서 사용하기 위한 클래스
from langchain.agents import initialize_agent, AgentType, Tool  # 에이전트 초기화 및 도구 구성에 필요한 클래스들

# 간단한 덧셈 함수를 정의하고 랭체인 툴로 등록
@tool
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    return a + b

# 간단한 뺄셈 함수를 정의하고 랭체인 툴로 등록
@tool
def subtract(a: int, b: int) -> int:
    """두 숫자를 뺍니다."""
    return a - b

# 위에서 정의한 툴들을 리스트로 구성
tools = [add, subtract]

# GPT-4o 모델을 기반으로 하는 OpenAI LLM을 생성 (온도=0은 일관된 응답을 유도)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 랭체인의 Function Calling 기반 에이전트를 초기화
# LLM이 사용자 입력을 분석해 적절한 툴(add/subtract)을 자동으로 선택해 호출
agent = initialize_agent(
    tools=tools,                      # 사용할 툴 목록
    llm=llm,                          # 사용할 LLM (GPT-4o)
    agent=AgentType.OPENAI_FUNCTIONS,  # Function Calling 기반 에이전트 사용
    verbose=True                      # 실행 과정을 출력
)

# 사용자 질의 입력에 대해해 에이전트가 적절한 툴(subtract)을 선택하여 실행
response = agent.invoke("7에서 3을 빼줘")

# 결과 출력
print("응답:", response)
