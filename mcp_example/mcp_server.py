import psutil
import httpx
from mcp.server.fastmcp import FastMCP

# "MCPAgentServer" という名前でMCPサーバーを初期化
mcp = FastMCP("MCPAgentServer")

@mcp.tool()
async def fetch_temperature() -> str:
    """現在の東京の気温を取得して返す関数です。"""
    # (緯度: 35.7, 経度: 139.7 は東京のおおよその値)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude=35.7&longitude=139.7&current_weather=true&"
        f"hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # ステータスコードが200以外なら例外を発生させる
            weather_data = response.json()
            current_weather = weather_data.get("current_weather", {})
            temperature = current_weather.get("temperature", "N/A")
            return f"MCP Server: 東京の現在の温度は {temperature}°C です"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


@mcp.tool()
def battery_status() -> str:
    """バッテリーの残量を返す"""
    battery = psutil.sensors_battery()
    if battery:
        return f"バッテリー残量は {battery.percent}%です。"
    return "バッテリー情報が取得できませんでした"


if __name__ == "__main__":
    mcp.run(transport='stdio')
