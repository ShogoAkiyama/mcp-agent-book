import os
from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any, List

# MCP関連ライブラリ
from mcp.server.fastmcp import FastMCP

# GCP関連ラライブラリ
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_JSON_PATH = os.getenv("SERVICE_ACCOUNT_JSON_PATH")
SPREAD_SHEET_ID = os.getenv("SPREAD_SHEET_ID")

# # Google Drive APIクライアントを作成
CREDS = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_JSON_PATH,
    scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
)
DRIVE_SERVICE = build('drive', 'v3', credentials=CREDS)
SHEETS_SERVICE = build('sheets', 'v4', credentials=CREDS)

mcp = FastMCP("SheetMCPServer")

# --- ここから下にMCPツール関数を定義していきます ---
@mcp.tool()
def update_cells(sheet: str, range: str, data: List[List[Any]]) -> Dict[str, Any]:
    """
    Googleスプレッドシートのセルを更新します
    
    Args:
        sheet: シート名
        range: セル範囲 (A1表記、例: 'A1:C10')
        data: 更新する値の2次元配列
    
    Returns:
        更新操作の結果
    """
    
    # Sheets APIを呼び出して値を更新
    result = SHEETS_SERVICE.spreadsheets().values().update(
        spreadsheetId=SPREAD_SHEET_ID,    # 事前に定義されたスプレッドシートIDを使用
        range=f"{sheet}!{range}",
        body={'values': data},            # MCPツールのdata引数をAPIのbodyのvaluesに設定
        valueInputOption='USER_ENTERED',  # 入力値をユーザーが直接入力したかのように解釈
    ).execute()
    
    return result


@mcp.tool()
def create_sheet(title: str) -> Dict[str, Any]:
    """
    既存のGoogleスプレッドシートに新しいシートを作成します

    Args:
        title: 新しいシートのタイトル

    Returns:
        新しく作成されたシートに関する情報
    """
    
    # リクエストを実行
    result = SHEETS_SERVICE.spreadsheets().batchUpdate(
        spreadsheetId=SPREAD_SHEET_ID,
        body={
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title
                        }
                    }
                }
            ]
        }
    ).execute()

    return result['replies'][0]['addSheet']['properties']


@mcp.tool()
def get_sheet_metadata() -> Dict[str, Any]:
    """
    指定されたスプレッドシート全体のメタデータを取得します。
    これには、各シートの名前、ID、プロパティなどの情報が含まれます。

    Args:
        なし

    Returns:
        スプレッドシートのメタデータを含む辞書
    """

    sheet_metadata = SHEETS_SERVICE.spreadsheets().get(
        spreadsheetId=SPREAD_SHEET_ID
    ).execute()
    return sheet_metadata


@mcp.tool()
def get_sheet_data(sheet: str) -> Dict[str, Any]:
    """
    Googleスプレッドシートの特定のシートからデータを取得します。

    Args:
        sheet (str): シート名。

    Returns:
        シートのデータを含む辞書
    """

    result = SHEETS_SERVICE.spreadsheets().values().get(
        spreadsheetId=SPREAD_SHEET_ID,
        range=sheet,
    ).execute()

    return result


@mcp.tool()
def merge_cells(
    sheet_id: int, start_row: int, end_row: int, start_col: int, end_col: int
) -> Dict[str, Any]:
    """
    指定された範囲のセルを結合します。
    end_row, end_col はそのインデックスを含まない点に注意してください

    Args:
        sheet_id: シートID
        start_row: 結合範囲の開始行インデックス (0から開始)
        end_row: 結合範囲の終了行インデックス (この行を含まない)
        start_col: 結合範囲の開始列インデックス (0から開始)
        end_col: 結合範囲の終了列インデックス (この列を含まない)

    Returns:
        batchUpdateの結果、またはエラー情報
    """

    requests = [
        {
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col
                },
                "mergeType": "MERGE_ALL"
            }
        }
    ]


    result = SHEETS_SERVICE.spreadsheets().batchUpdate(
        spreadsheetId=SPREAD_SHEET_ID,
        body={"requests": requests}
    ).execute()
    return result


@mcp.tool()
def set_background_color(
    sheet_id: int,
    start_row: int,
    end_row: int,
    start_col: int,
    end_col: int,
    color: Dict[str, float],
) -> Dict[str, Any]:
    """
    指定された範囲のセルの背景色を設定します。範囲は0ベースのインデックスで指定します。
    色はRGB形式 (各要素0.0〜1.0) で指定します。例: {"red":1.0, "green":0.0, "blue":0.0}
    end_row, end_col はそのインデックスを含まない点に注意してください。

    Args:
        sheet: シート名
        start_row: 範囲の開始行インデックス (0から開始)
        end_row: 範囲の終了行インデックス (この行を含まない)
        start_col: 範囲の開始列インデックス (0から開始)
        end_col: 範囲の終了列インデックス (この列を含まない)
        color: 色指定 (必須キー: red, green, blue, 各値0～1)。例: {"red":0.8, "green":0.8, "blue":0.8}

    Returns:
        batchUpdateの結果、またはエラー情報
    """

    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColorStyle": {
                             "rgbColor": color
                         }
                    }
                },
                "fields": "userEnteredFormat.backgroundColorStyle.rgbColor"
            }
        }
    ]

    result = SHEETS_SERVICE.spreadsheets().batchUpdate(
        spreadsheetId=SPREAD_SHEET_ID,
        body={"requests": requests}
    ).execute()
    return result


if __name__ == "__main__":
    mcp.run(transport='stdio')
