import os
import pandas as pd
from urllib.parse import quote

SHEET_ID = os.environ.get("SHEET_ID")

if not SHEET_ID:
    print("❌ 錯誤：未設定 SHEET_ID")
    exit(1)

def check_sheet(sheet_name):
    encoded_sheet_name = quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    print(f"\n================ 正在抓取 [{sheet_name}] ================")
    try:
        # 完全不作任何處理，直接讀取原始 CSV
        df = pd.read_csv(url, dtype=str, keep_default_na=False, encoding='utf-8')
        df.columns = df.columns.str.strip()
        
        print("✅ 成功連線！抓到的所有欄位名稱為：")
        print(list(df.columns))
        
        print("\n🔍 前 5 行的原始資料（看看你的 40r 到底有沒有傳過來）：")
        # 印出前 5 行資料
        for idx, row in df.head(5).iterrows():
            print(f"--- 第 {idx+1} 行 ---")
            for col in df.columns:
                val = row[col]
                # 只要欄位值裡面有非純數字的字元就印出來印證
                if val:
                    print(f"  [{col}]: '{val}'")
                    
    except Exception as e:
        print(f"❌ 抓取失敗，錯誤訊息：{e}")

if __name__ == "__main__":
    check_sheet("打擊成績")
