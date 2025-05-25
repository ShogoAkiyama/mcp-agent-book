import os
from dotenv import load_dotenv
import openai
import psutil

# .env を読み込む
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


@tool
def disk_status() -> str:
    """ディスクの空き容量を返す"""
    dsk = psutil.disk_usage('/')
    return f"ディスク使用量は{dsk.free / (1024**3):.1f}GBです"


@tool()
def battery_status() -> str:
    """バッテリーの残量を返す"""
    battery = psutil.sensors_battery()
    if battery:
        return f"バッテリー残量は {battery.percent}%です。"
    return "バッテリー情報が取得できませんでした"


def main():
    tools = [disk_status, battery_status]
    llm = ChatOpenAI(model="gpt-4.1-mini")
    agent = create_react_agent(llm, tools)

    while True:
        user_input = input("ユーザー入力: ")
        if user_input.lower() == "q":
            break

        inputs = {"messages": [HumanMessage(content=user_input)]}
        for state in agent.stream(inputs, stream_mode="values"):
            message = state["messages"][-1]
            message.pretty_print()

        print("\n===== 会話終了 =====\n")


if __name__ == "__main__":
    main()
