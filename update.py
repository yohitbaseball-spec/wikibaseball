import os
import pandas as pd
from urllib.parse import quote

SHEET_ID = os.environ.get("SHEET_ID")

if not SHEET_ID:
    print("❌ 錯誤：未設定 SHEET_ID")
    exit(1)

def ip_to_outs(ip):
    try:
        clean_ip = str(ip).replace('*', '').strip()
        ip_float = float(clean_ip)
        i = int(ip_float)
        f = round(ip_float - i, 1)
        outs = i * 3
        if f == 0.1: outs += 1
        elif f == 0.2: outs += 2
        return outs
    except:
        return 0

def parse_val(raw_val):
    s = str(raw_val).strip()
    if s.endswith('**'):
        clean_s = s[:-2].strip()
        try: num = float(clean_s)
        except: num = 0.0
        return num, f'<b style="color: red;">{clean_s}</b>'
    elif s.endswith('*'):
        clean_s = s[:-1].strip()
        try: num = float(clean_s)
        except: num = 0.0
        return num, f'<b>{clean_s}</b>'
    else:
        try: num = float(s)
        except: num = 0.0
        return num, s

def fmt_stat(raw_val, calc_num, precision=0):
    raw_str = str(raw_val).strip()
    if raw_str != "":
        num, _ = parse_val(raw_str)
        if precision == 3: formatted_num = f"{num:.3f}"
        elif precision == 2: formatted_num = f"{num:.2f}"
        else: formatted_num = f"{int(num)}" if num.is_integer() else f"{num}"
            
        if raw_str.endswith('**'): return f'<b style="color: red;">{formatted_num}</b>'
        elif raw_str.endswith('*'): return f'<b>{formatted_num}</b>'
        else: return formatted_num
    else:
        if precision == 3: return f"{calc_num:.3f}"
        elif precision == 2: return f"{calc_num:.2f}"
        else: return f"{int(calc_num)}" if calc_num.is_integer() else f"{calc_num}"

def fetch_sheet_data(sheet_name):
    encoded_sheet_name = quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    try:
        df = pd.read_csv(url, dtype=str, encoding='utf-8')
        df.columns = df.columns.str.strip()
        return df.fillna('')
    except Exception as e:
        print(f"⚠️ 無法讀取分頁 [{sheet_name}]: {e}")
        return None

def process_batting_stats():
    df = fetch_sheet_data("打擊成績")
    if df is None or df.empty or 'player_id' not in df.columns:
        return {}

    batting_by_player = {}
    for pid, group in df.groupby('player_id'):
        rows_html = ""
        for _, row in group.iterrows():
            ab, _ = parse_val(row.get('AB', '0'))
            h, _ = parse_val(row.get('H', '0'))
            bb, _ = parse_val(row.get('BB', '0'))
            sf, _ = parse_val(row.get('SF', '0'))
            tb, _ = parse_val(row.get('TB', '0'))

            avg_calc = (h / ab) if ab > 0 else 0.0
            obp_calc = ((h + bb) / (ab + bb + sf)) if (ab + bb + sf) > 0 else 0.0
            slg_calc = (tb / ab) if ab > 0 else 0.0
            ops_calc = obp_calc + slg_calc

            avg_str = fmt_stat(row.get('AVG', ''), avg_calc, 3)
            obp_str = fmt_stat(row.get('OBP', ''), obp_calc, 3)
            slg_str = fmt_stat(row.get('SLG', ''), slg_calc, 3)
            ops_str = fmt_stat(row.get('OPS', ''), ops_calc, 3)

            # 嚴格對齊表頭：年度 | 球隊 | G | PA | AB | H | 2B | 3B | HR | RBI | R | SB | TB | SO | BB | SAC | SF | AVG | OBP | SLG | OPS
            rows_html += f"""          <tr>
            <td>{parse_val(row.get('year', ''))[1]}</td>
            <td>{parse_val(row.get('team', ''))[1]}</td>
            <td>{fmt_stat(row.get('G', ''), 0)}</td>
            <td>{fmt_stat(row.get('PA', ''), 0)}</td>
            <td>{fmt_stat(row.get('AB', ''), 0)}</td>
            <td>{fmt_stat(row.get('H', ''), 0)}</td>
            <td>{fmt_stat(row.get('2B', ''), 0)}</td>
            <td>{fmt_stat(row.get('3B', ''), 0)}</td>
            <td>{fmt_stat(row.get('HR', ''), 0)}</td>
            <td>{fmt_stat(row.get('RBI', ''), 0)}</td>
            <td>{fmt_stat(row.get('R', ''), 0)}</td>
            <td>{fmt_stat(row.get('SB', ''), 0)}</td>
            <td>{fmt_stat(row.get('TB', ''), 0)}</td>
            <td>{fmt_stat(row.get('SO', ''), 0)}</td>
            <td>{fmt_stat(row.get('BB', ''), 0)}</td>
            <td>{fmt_stat(row.get('SAC', ''), 0)}</td>
            <td>{fmt_stat(row.get('SF', ''), 0)}</td>
            <td>{avg_str}</td>
            <td>{obp_str}</td>
            <td>{slg_str}</td>
            <td>{ops_str}</td>
          </tr>\n"""
        batting_by_player[str(pid).strip()] = rows_html
    return batting_by_player

def process_pitching_stats():
    df = fetch_sheet_data("投手成績")
    if df is None or df.empty or 'player_id' not in df.columns:
        return {}

    pitching_by_player = {}
    for pid, group in df.groupby('player_id'):
        rows_html = ""
        for _, row in group.iterrows():
            ip_val = row.get('IP', '0')
            outs = ip_to_outs(ip_val)
            ip_actual = outs / 3.0

            bf, _ = parse_val(row.get('BF', '0'))
            bb, _ = parse_val(row.get('BB', '0'))
            bh, _ = parse_val(row.get('BH', '0'))
            er, _ = parse_val(row.get('ER', '0'))

            ab_against = bf - bb
            oavg_calc = (bh / ab_against) if ab_against > 0 else 0.0
            era_calc = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0
            whip_calc = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            oavg_str = fmt_stat(row.get('OAVG', ''), oavg_calc, 3)
            era_str = fmt_stat(row.get('ERA', ''), era_calc, 2)
            whip_str = fmt_stat(row.get('WHIP', ''), whip_calc, 2)

            rows_html += f"""          <tr>
            <td>{parse_val(row.get('year', ''))[1]}</td>
            <td>{parse_val(row.get('team', ''))[1]}</td>
            <td>{fmt_stat(row.get('G', ''), 0)}</td>
            <td>{fmt_stat(row.get('GS', ''), 0)}</td>
            <td>{fmt_stat(row.get('W', ''), 0)}</td>
            <td>{fmt_stat(row.get('L', ''), 0)}</td>
            <td>{fmt_stat(row.get('HLD', ''), 0)}</td>
            <td>{fmt_stat(row.get('SV', ''), 0)}</td>
            <td>{parse_val(ip_val)[1]}</td>
            <td>{fmt_stat(row.get('QS', ''), 0)}</td>
            <td>{fmt_stat(row.get('BF', ''), 0)}</td>
            <td>{fmt_stat(row.get('BH', ''), 0)}</td>
            <td>{fmt_stat(row.get('BHR', ''), 0)}</td>
            <td>{oavg_str}</td>
            <td>{fmt_stat(row.get('SO', ''), 0)}</td>
            <td>{fmt_stat(row.get('BB', ''), 0)}</td>
            <td>{fmt_stat(row.get('R', ''), 0)}</td>
            <td>{fmt_stat(row.get('ER', ''), 0)}</td>
            <td>{era_str}</td>
            <td>{whip_str}</td>
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

                for pid, html_rows in batting_data.items():
                    if pid in content and "<!-- STATS_START -->" in content:
                        start_tag = "<!-- STATS_START -->"
                        end_tag = "<!-- STATS_END -->"
                        idx1 = content.find(start_tag) + len(start_tag)
                        idx2 = content.find(end_tag)
                        if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                            content = content[:idx1] + "\n" + html_rows + "        " + content[idx2:]
                            updated = True

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
