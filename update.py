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

def outs_to_ip_str(outs):
    i = outs // 3
    f = outs % 3
    if f == 0: return f"{i}"
    else: return f"{i}.{f}"

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
        
        # 通算累計變數
        tot_g = tot_pa = tot_ab = tot_h = tot_2b = tot_3b = tot_hr = 0
        tot_rbi = tot_r = tot_sb = tot_tb = tot_so = tot_bb = tot_sac = tot_sf = 0

        for _, row in group.iterrows():
            year_str = parse_val(row.get('year', ''))[1]
            team_str = parse_val(row.get('team', ''))[1]

            g, _ = parse_val(row.get('G', '0'))
            pa, _ = parse_val(row.get('PA', '0'))
            ab, _ = parse_val(row.get('AB', '0'))
            h, _ = parse_val(row.get('H', '0'))
            b2, _ = parse_val(row.get('2B', '0'))
            b3, _ = parse_val(row.get('3B', '0'))
            hr, _ = parse_val(row.get('HR', '0'))
            rbi, _ = parse_val(row.get('RBI', '0'))
            r, _ = parse_val(row.get('R', '0'))
            sb, _ = parse_val(row.get('SB', '0'))
            so, _ = parse_val(row.get('SO', '0'))
            bb, _ = parse_val(row.get('BB', '0'))
            sac, _ = parse_val(row.get('SAC', '0'))
            sf, _ = parse_val(row.get('SF', '0'))

            raw_tb = str(row.get('TB', '')).strip()
            if raw_tb != "":
                tb, _ = parse_val(raw_tb)
            else:
                tb = h + b2 + (2 * b3) + (3 * hr)

            # 累加通算數據
            tot_g += g; tot_pa += pa; tot_ab += ab; tot_h += h
            tot_2b += b2; tot_3b += b3; tot_hr += hr; tot_rbi += rbi
            tot_r += r; tot_sb += sb; tot_tb += tb; tot_so += so
            tot_bb += bb; tot_sac += sac; tot_sf += sf

            avg_calc = (h / ab) if ab > 0 else 0.0
            obp_calc = ((h + bb) / (ab + bb + sf)) if (ab + bb + sf) > 0 else 0.0
            slg_calc = (tb / ab) if ab > 0 else 0.0
            ops_calc = obp_calc + slg_calc

            avg_str = fmt_stat(row.get('AVG', ''), avg_calc, 3)
            obp_str = fmt_stat(row.get('OBP', ''), obp_calc, 3)
            slg_str = fmt_stat(row.get('SLG', ''), slg_calc, 3)
            ops_str = fmt_stat(row.get('OPS', ''), ops_calc, 3)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{fmt_stat(row.get('G', ''), g)}</td>
            <td>{fmt_stat(row.get('PA', ''), pa)}</td>
            <td>{fmt_stat(row.get('AB', ''), ab)}</td>
            <td>{fmt_stat(row.get('H', ''), h)}</td>
            <td>{fmt_stat(row.get('2B', ''), b2)}</td>
            <td>{fmt_stat(row.get('3B', ''), b3)}</td>
            <td>{fmt_stat(row.get('HR', ''), hr)}</td>
            <td>{fmt_stat(row.get('RBI', ''), rbi)}</td>
            <td>{fmt_stat(row.get('R', ''), r)}</td>
            <td>{fmt_stat(row.get('SB', ''), sb)}</td>
            <td>{fmt_stat(row.get('TB', ''), tb)}</td>
            <td>{fmt_stat(row.get('SO', ''), so)}</td>
            <td>{fmt_stat(row.get('BB', ''), bb)}</td>
            <td>{fmt_stat(row.get('SAC', ''), sac)}</td>
            <td>{fmt_stat(row.get('SF', ''), sf)}</td>
            <td>{avg_str}</td>
            <td>{obp_str}</td>
            <td>{slg_str}</td>
            <td>{ops_str}</td>
          </tr>\n"""

        # 計算通算成績（至少需有 1 個年度）
        if len(group) > 0:
            tot_avg = (tot_h / tot_ab) if tot_ab > 0 else 0.0
            tot_obp = ((tot_h + tot_bb) / (tot_ab + tot_bb + tot_sf)) if (tot_ab + tot_bb + tot_sf) > 0 else 0.0
            tot_slg = (tot_tb / tot_ab) if tot_ab > 0 else 0.0
            tot_ops = tot_obp + tot_slg

            rows_html += f"""          <tr>
            <td><b>通算</b></td>
            <td>-</td>
            <td><b>{int(tot_g)}</b></td>
            <td><b>{int(tot_pa)}</b></td>
            <td><b>{int(tot_ab)}</b></td>
            <td><b>{int(tot_h)}</b></td>
            <td><b>{int(tot_2b)}</b></td>
            <td><b>{int(tot_3b)}</b></td>
            <td><b>{int(tot_hr)}</b></td>
            <td><b>{int(tot_rbi)}</b></td>
            <td><b>{int(tot_r)}</b></td>
            <td><b>{int(tot_sb)}</b></td>
            <td><b>{int(tot_tb)}</b></td>
            <td><b>{int(tot_so)}</b></td>
            <td><b>{int(tot_bb)}</b></td>
            <td><b>{int(tot_sac)}</b></td>
            <td><b>{int(tot_sf)}</b></td>
            <td><b>{tot_avg:.3f}</b></td>
            <td><b>{tot_obp:.3f}</b></td>
            <td><b>{tot_slg:.3f}</b></td>
            <td><b>{tot_ops:.3f}</b></td>
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
        
        tot_g = tot_gs = tot_w = tot_l = tot_hld = tot_sv = tot_outs = tot_qs = 0
        tot_bf = tot_bh = tot_bhr = tot_so = tot_bb = tot_r = tot_er = 0

        for _, row in group.iterrows():
            year_str = parse_val(row.get('year', ''))[1]
            team_str = parse_val(row.get('team', ''))[1]

            ip_val = row.get('IP', '0')
            outs = ip_to_outs(ip_val)
            ip_actual = outs / 3.0

            g, _ = parse_val(row.get('G', '0'))
            gs, _ = parse_val(row.get('GS', '0'))
            w, _ = parse_val(row.get('W', '0'))
            l, _ = parse_val(row.get('L', '0'))
            hld, _ = parse_val(row.get('HLD', '0'))
            sv, _ = parse_val(row.get('SV', '0'))
            qs, _ = parse_val(row.get('QS', '0'))
            bf, _ = parse_val(row.get('BF', '0'))
            bh, _ = parse_val(row.get('BH', '0'))
            bhr, _ = parse_val(row.get('BHR', '0'))
            so, _ = parse_val(row.get('SO', '0'))
            bb, _ = parse_val(row.get('BB', '0'))
            r, _ = parse_val(row.get('R', '0'))
            er, _ = parse_val(row.get('ER', '0'))

            tot_g += g; tot_gs += gs; tot_w += w; tot_l += l
            tot_hld += hld; tot_sv += sv; tot_outs += outs; tot_qs += qs
            tot_bf += bf; tot_bh += bh; tot_bhr += bhr; tot_so += so
            tot_bb += bb; tot_r += r; tot_er += er

            ab_against = bf - bb
            oavg_calc = (bh / ab_against) if ab_against > 0 else 0.0
            era_calc = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0
            whip_calc = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            oavg_str = fmt_stat(row.get('OAVG', ''), oavg_calc, 3)
            era_str = fmt_stat(row.get('ERA', ''), era_calc, 2)
            whip_str = fmt_stat(row.get('WHIP', ''), whip_calc, 2)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{fmt_stat(row.get('G', ''), g)}</td>
            <td>{fmt_stat(row.get('GS', ''), gs)}</td>
            <td>{fmt_stat(row.get('W', ''), w)}</td>
            <td>{fmt_stat(row.get('L', ''), l)}</td>
            <td>{fmt_stat(row.get('HLD', ''), hld)}</td>
            <td>{fmt_stat(row.get('SV', ''), sv)}</td>
            <td>{parse_val(ip_val)[1]}</td>
            <td>{fmt_stat(row.get('QS', ''), qs)}</td>
            <td>{fmt_stat(row.get('BF', ''), bf)}</td>
            <td>{fmt_stat(row.get('BH', ''), bh)}</td>
            <td>{fmt_stat(row.get('BHR', ''), bhr)}</td>
            <td>{oavg_str}</td>
            <td>{fmt_stat(row.get('SO', ''), so)}</td>
            <td>{fmt_stat(row.get('BB', ''), bb)}</td>
            <td>{fmt_stat(row.get('R', ''), r)}</td>
            <td>{fmt_stat(row.get('ER', ''), er)}</td>
            <td>{era_str}</td>
            <td>{whip_str}</td>
          </tr>\n"""

        if len(group) > 0:
            tot_ip_actual = tot_outs / 3.0
            tot_ab_against = tot_bf - tot_bb
            tot_oavg = (tot_bh / tot_ab_against) if tot_ab_against > 0 else 0.0
            tot_era = (tot_er * 9.0) / tot_ip_actual if tot_ip_actual > 0 else 0.0
            tot_whip = (tot_bb + tot_bh) / tot_ip_actual if tot_ip_actual > 0 else 0.0

            rows_html += f"""          <tr>
            <td><b>通算</b></td>
            <td>-</td>
            <td><b>{int(tot_g)}</b></td>
            <td><b>{int(tot_gs)}</b></td>
            <td><b>{int(tot_w)}</b></td>
            <td><b>{int(tot_l)}</b></td>
            <td><b>{int(tot_hld)}</b></td>
            <td><b>{int(tot_sv)}</b></td>
            <td><b>{outs_to_ip_str(tot_outs)}</b></td>
            <td><b>{int(tot_qs)}</b></td>
            <td><b>{int(tot_bf)}</b></td>
            <td><b>{int(tot_bh)}</b></td>
            <td><b>{int(tot_bhr)}</b></td>
            <td><b>{tot_oavg:.3f}</b></td>
            <td><b>{int(tot_so)}</b></td>
            <td><b>{int(tot_bb)}</b></td>
            <td><b>{int(tot_r)}</b></td>
            <td><b>{int(tot_er)}</b></td>
            <td><b>{tot_era:.2f}</b></td>
            <td><b>{tot_whip:.2f}</b></td>
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
