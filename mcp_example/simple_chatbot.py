import os
from dotenv import load_dotenv
from openai import OpenAI

# .env を読み込む
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

MODEL_NAME = "gpt-4.1-mini"

SYSTEM_PROMPT = "あなたはチャットボットシステムです。日本語で答えてください。"

def main():
    print("チャットボットを起動しました。'q'と入力すると終了します。")
    while True:
        user_input = input("ユーザー入力: ")
        if user_input.lower() == "q":
            break

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        print("アシスタント:", response.choices[0].message.content)
        print("\n===== 会話終了 =====\n")


if __name__ == "__main__":
    main()
