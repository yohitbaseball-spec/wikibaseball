import os
import pandas as pd

# 取得環境變數中的 SHEET_ID
SHEET_ID = os.environ.get("SHEET_ID")

if not SHEET_ID:
    print("❌ 錯誤：未設定 SHEET_ID")
    exit(1)

def ip_to_outs(ip):
    """將 baseball 局數 (例如 5.2) 轉換為總出局數 (Outs)"""
    try:
        ip_float = float(ip)
        i = int(ip_float)
        f = round(ip_float - i, 1)
        outs = i * 3
        if f == 0.1:
            outs += 1
        elif f == 0.2:
            outs += 2
        return outs
    except:
        return 0

def fetch_sheet_data(sheet_name):
    """從 Google Sheet 讀取指定分頁資料"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip() # 去除表頭前後空白
        return df
    except Exception as e:
        print(f"⚠️ 無法讀取分頁 [{sheet_name}]: {e}")
        return None

def process_batting_stats():
    """處理打者成績 (使用 player_id 作為姓名配對)"""
    df = fetch_sheet_data("打擊成績")
    if df is None or df.empty or 'player_id' not in df.columns:
        return {}

    cols = ['PA', 'AB', 'H', '2B', '3B', 'HR', 'RBI', 'R', 'SB', 'TB', 'SO', 'BB', 'SAC', 'SF', 'G']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df['AVG'] = df.apply(lambda r: r['H'] / r['AB'] if r['AB'] > 0 else 0, axis=1)
    df['OBP'] = df.apply(lambda r: (r['H'] + r['BB']) / (r['AB'] + r['BB'] + r['SF']) if (r['AB'] + r['BB'] + r['SF']) > 0 else 0, axis=1)
    df['SLG'] = df.apply(lambda r: r['TB'] / r['AB'] if r['AB'] > 0 else 0, axis=1)
    df['OPS'] = df['OBP'] + df['SLG']

    batting_by_player = {}
    for pid, group in df.groupby('player_id'):
        rows_html = ""
        for _, row in group.iterrows():
            rows_html += f"""          <tr>
            <td>{row.get('player_id', '')}</td>
            <td>{row.get('year', '')}</td>
            <td>{row.get('team', '')}</td>
            <td>{row.get('G', 0)}</td>
            <td>{row.get('PA', 0)}</td>
            <td>{row.get('AB', 0)}</td>
            <td>{row.get('H', 0)}</td>
            <td>{row.get('2B', 0)}</td>
            <td>{row.get('3B', 0)}</td>
            <td>{row.get('HR', 0)}</td>
            <td>{row.get('RBI', 0)}</td>
            <td>{row.get('R', 0)}</td>
            <td>{row.get('SB', 0)}</td>
            <td>{row.get('TB', 0)}</td>
            <td>{row.get('SO', 0)}</td>
            <td>{row.get('BB', 0)}</td>
            <td>{row.get('SAC', 0)}</td>
            <td>{row.get('SF', 0)}</td>
            <td>{row['AVG']:.3f}</td>
            <td>{row['OBP']:.3f}</td>
            <td>{row['SLG']:.3f}</td>
            <td>{row['OPS']:.3f}</td>
          </tr>\n"""
        batting_by_player[str(pid).strip()] = rows_html
    return batting_by_player

def process_pitching_stats():
    """處理投手成績 (順序：姓名/year/team/G/GS/W/L/HLD/SV/IP/QS/BF/BH/BHR/OAVG/SO/BB/R/ER/era/WHIP)"""
    df = fetch_sheet_data("投手成績")
    if df is None or df.empty or 'player_id' not in df.columns:
        return {}

    cols = ['G', 'GS', 'W', 'L', 'HLD', 'SV', 'QS', 'BF', 'BH', 'BHR', 'SO', 'BB', 'R', 'ER']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    pitching_by_player = {}
    for pid, group in df.groupby('player_id'):
        rows_html = ""
        for _, row in group.iterrows():
            ip_val = row.get('IP', 0)
            outs = ip_to_outs(ip_val)
            ip_actual = outs / 3.0

            bf = row.get('BF', 0)
            bb = row.get('BB', 0)
            bh = row.get('BH', 0)
            er = row.get('ER', 0)

            # OAVG 被打擊率
            ab_against = bf - bb
            oavg = (bh / ab_against) if ab_against > 0 else 0.0

            # ERA 防禦率
            era = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0

            # WHIP 每局被上壘率
            whip = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            rows_html += f"""          <tr>
            <td>{row.get('player_id', '')}</td>
            <td>{row.get('year', '')}</td>
            <td>{row.get('team', '')}</td>
            <td>{row.get('G', 0)}</td>
            <td>{row.get('GS', 0)}</td>
            <td>{row.get('W', 0)}</td>
            <td>{row.get('L', 0)}</td>
            <td>{row.get('HLD', 0)}</td>
            <td>{row.get('SV', 0)}</td>
            <td>{ip_val}</td>
            <td>{row.get('QS', 0)}</td>
            <td>{bf}</td>
            <td>{bh}</td>
            <td>{row.get('BHR', 0)}</td>
            <td>{oavg:.3f}</td>
            <td>{row.get('SO', 0)}</td>
            <td>{bb}</td>
            <td>{row.get('R', 0)}</td>
            <td>{er}</td>
            <td>{era:.2f}</td>
            <td>{whip:.2f}</td>
          </tr>\n"""
        pitching_by_player[str(pid).strip()] = rows_html
    return pitching_by_player

def update_html_files():
    batting_data = process_batting_stats()
    pitching_data = process_pitching_stats()

    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                updated = False

                # 1. 依 player_id 名字匹配打擊成績
                for pid, html_rows in batting_data.items():
                    if pid in content and "<!-- STATS_START -->" in content:
                        start_tag = "<!-- STATS_START -->"
                        end_tag = "<!-- STATS_END -->"
                        idx1 = content.find(start_tag) + len(start_tag)
                        idx2 = content.find(end_tag)
                        if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                            content = content[:idx1] + "\n" + html_rows + "        " + content[idx2:]
                            updated = True

                # 2. 依 player_id 名字匹配投手成績
                for pid, html_rows in pitching_data.items():
                    if pid in content and "<!-- PITCHER_STATS_START -->" in content:
                        start_tag = "<!-- PITCHER_STATS_START -->"
                        end_tag = "<!-- PITCHER_STATS_END -->"
                        idx1 = content.find(start_tag) + len(start_tag)
                        idx2 = content.find(end_tag)
                        if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                            content = content[:idx1] + "\n" + html_rows + "        " + content[idx2:]
                            updated = True

                if updated:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ 已成功更新球員網頁: {filepath}")

if __name__ == "__main__":
    update_html_files()
