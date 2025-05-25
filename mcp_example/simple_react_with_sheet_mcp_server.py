import asyncio
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


server_params = StdioServerParameters(
    command="uv",
    args=[
        # "--directory",
        # "{違うディレクトリにある場合はsheet_mcp_server.pyがあるパス}",
        "run",
        "sheet_mcp_server.py"
    ],
)


async def main():

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            print("\n===== MCPクライアント =====\n")
            await session.initialize()

            tools = await load_mcp_tools(session)
            print(f"利用可能なツール：{[x.name for x in tools]}")

            llm = ChatOpenAI(model="gpt-4.1-mini")
            agent = create_react_agent(llm, tools)

            while True:
                user_input = input("ユーザー入力: ")
                if user_input.lower() == "q":
                    break

                inputs = {"messages": [HumanMessage(content=user_input)]}
                async for state in agent.astream(inputs, stream_mode="values"):
                    message = state["messages"][-1]
                    message.pretty_print()

                print("\n===== 会話終了 =====\n")


if __name__ == "__main__":
    asyncio.run(main())
