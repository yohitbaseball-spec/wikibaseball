import os
import re
import pandas as pd
from urllib.parse import quote

SHEET_ID = os.environ.get("SHEET_ID")

if not SHEET_ID:
    print("❌ 錯誤：未設定 SHEET_ID")
    exit(1)

def ip_to_outs(ip):
    try:
        clean_ip = re.sub(r'[^\d.]', '', str(ip))
        if not clean_ip: return 0
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

def parse_val_and_style(raw_val):
    s = str(raw_val).strip()
    if not s or s == '-' or s.lower() == 'nan':
        return 0.0, ''

    # 1. 判斷要不要變色 (只要有 r、R 或 '紅' 就抓)
    style_type = ''
    if 'r' in s.lower() or '紅' in s:
        style_type = 'red'
    elif 'b' in s.lower():
        style_type = 'bold'

    # 2. 剝離文字，只保留數字與小數點 (絕不歸零)
    clean_num_str = ''.join([c for c in s if c.isdigit() or c == '.'])
    
    try:
        num = float(clean_num_str) if clean_num_str else 0.0
    except ValueError:
        num = 0.0

    return num, style_type

def format_cell(num, style_type, precision=0):
    if precision == 3:
        formatted_num = f"{num:.3f}"
    elif precision == 2:
        formatted_num = f"{num:.2f}"
    elif precision == 1:
        formatted_num = f"{num:.1f}" if num % 1 != 0 else f"{int(num)}"
    else:
        formatted_num = f"{int(num)}" if float(num).is_integer() else f"{num}"

    if style_type == 'red':
        return f'<b style="color: red;">{formatted_num}</b>'
    elif style_type == 'bold':
        return f'<b>{formatted_num}</b>'
    else:
        return formatted_num

def fetch_sheet_data(sheet_name):
    encoded_sheet_name = quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    try:
        df = pd.read_csv(url, dtype=str, keep_default_na=False, encoding='utf-8')
        df.columns = df.columns.str.strip()
        return df
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
        
        tot_g = tot_pa = tot_ab = tot_h = tot_2b = tot_3b = tot_hr = 0.0
        tot_rbi = tot_r = tot_sb = tot_tb = tot_so = tot_bb = tot_sac = tot_sf = 0.0

        for _, row in group.iterrows():
            year_val, y_style = parse_val_and_style(row.get('year', ''))
            year_str = format_cell(year_val, y_style, 0) if str(row.get('year', '')).strip() != '' else ''
            team_str = str(row.get('team', '')).strip()

            g, g_style = parse_val_and_style(row.get('G', '0'))
            pa, pa_style = parse_val_and_style(row.get('PA', '0'))
            ab, ab_style = parse_val_and_style(row.get('AB', '0'))
            h, h_style = parse_val_and_style(row.get('H', '0'))
            b2, b2_style = parse_val_and_style(row.get('2B', '0'))
            b3, b3_style = parse_val_and_style(row.get('3B', '0'))
            hr, hr_style = parse_val_and_style(row.get('HR', '0'))
            rbi, rbi_style = parse_val_and_style(row.get('RBI', '0'))
            r, r_style = parse_val_and_style(row.get('R', '0'))
            sb, sb_style = parse_val_and_style(row.get('SB', '0'))
            so, so_style = parse_val_and_style(row.get('SO', '0'))
            bb, bb_style = parse_val_and_style(row.get('BB', '0'))
            sac, sac_style = parse_val_and_style(row.get('SAC', '0'))
            sf, sf_style = parse_val_and_style(row.get('SF', '0'))

            raw_tb = str(row.get('TB', '')).strip()
            if raw_tb != "":
                tb, tb_style = parse_val_and_style(raw_tb)
            else:
                tb = h + b2 + (2 * b3) + (3 * hr)
                tb_style = ''

            tot_g += g; tot_pa += pa; tot_ab += ab; tot_h += h
            tot_2b += b2; tot_3b += b3; tot_hr += hr; tot_rbi += rbi
            tot_r += r; tot_sb += sb; tot_tb += tb; tot_so += so
            tot_bb += bb; tot_sac += sac; tot_sf += sf

            avg_calc = (h / ab) if ab > 0 else 0.0
            obp_calc = ((h + bb) / (ab + bb + sf)) if (ab + bb + sf) > 0 else 0.0
            slg_calc = (tb / ab) if ab > 0 else 0.0
            ops_calc = obp_calc + slg_calc

            avg_val, avg_style = parse_val_and_style(row.get('AVG', ''))
            obp_val, obp_style = parse_val_and_style(row.get('OBP', ''))
            slg_val, slg_style = parse_val_and_style(row.get('SLG', ''))
            ops_val, ops_style = parse_val_and_style(row.get('OPS', ''))

            avg_final = format_cell(avg_val if str(row.get('AVG', '')).strip() != '' else avg_calc, avg_style, 3)
            obp_final = format_cell(obp_val if str(row.get('OBP', '')).strip() != '' else obp_calc, obp_style, 3)
            slg_final = format_cell(slg_val if str(row.get('SLG', '')).strip() != '' else slg_calc, slg_style, 3)
            ops_final = format_cell(ops_val if str(row.get('OPS', '')).strip() != '' else ops_calc, ops_style, 3)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{format_cell(g, g_style)}</td>
            <td>{format_cell(pa, pa_style)}</td>
            <td>{format_cell(ab, ab_style)}</td>
            <td>{format_cell(h, h_style)}</td>
            <td>{format_cell(b2, b2_style)}</td>
            <td>{format_cell(b3, b3_style)}</td>
            <td>{format_cell(hr, hr_style)}</td>
            <td>{format_cell(rbi, rbi_style)}</td>
            <td>{format_cell(r, r_style)}</td>
            <td>{format_cell(sb, sb_style)}</td>
            <td>{format_cell(tb, tb_style)}</td>
            <td>{format_cell(so, so_style)}</td>
            <td>{format_cell(bb, bb_style)}</td>
            <td>{format_cell(sac, sac_style)}</td>
            <td>{format_cell(sf, sf_style)}</td>
            <td>{avg_final}</td>
            <td>{obp_final}</td>
            <td>{slg_final}</td>
            <td>{ops_final}</td>
          </tr>\n"""

        # 通算行 (無粗體)
        if len(group) > 0:
            tot_avg = (tot_h / tot_ab) if tot_ab > 0 else 0.0
            tot_obp = ((tot_h + tot_bb) / (tot_ab + tot_bb + tot_sf)) if (tot_ab + tot_bb + tot_sf) > 0 else 0.0
            tot_slg = (tot_tb / tot_ab) if tot_ab > 0 else 0.0
            tot_ops = tot_obp + tot_slg

            rows_html += f"""          <tr>
            <td>通算</td>
            <td>-</td>
            <td>{int(tot_g)}</td>
            <td>{int(tot_pa)}</td>
            <td>{int(tot_ab)}</td>
            <td>{int(tot_h)}</td>
            <td>{int(tot_2b)}</td>
            <td>{int(tot_3b)}</td>
            <td>{int(tot_hr)}</td>
            <td>{int(tot_rbi)}</td>
            <td>{int(tot_r)}</td>
            <td>{int(tot_sb)}</td>
            <td>{int(tot_tb)}</td>
            <td>{int(tot_so)}</td>
            <td>{int(tot_bb)}</td>
            <td>{int(tot_sac)}</td>
            <td>{int(tot_sf)}</td>
            <td>{tot_avg:.3f}</td>
            <td>{tot_obp:.3f}</td>
            <td>{tot_slg:.3f}</td>
            <td>{tot_ops:.3f}</td>
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
        
        tot_g = tot_gs = tot_w = tot_l = tot_hld = tot_sv = tot_outs = tot_qs = 0.0
        tot_bf = tot_bh = tot_bhr = tot_so = tot_bb = tot_r = tot_er = 0.0

        for _, row in group.iterrows():
            year_val, y_style = parse_val_and_style(row.get('year', ''))
            year_str = format_cell(year_val, y_style, 0) if str(row.get('year', '')).strip() != '' else ''
            team_str = str(row.get('team', '')).strip()

            ip_val_raw = row.get('IP', '0')
            ip_num, ip_style = parse_val_and_style(ip_val_raw)
            outs = ip_to_outs(ip_val_raw)
            ip_actual = outs / 3.0

            g, g_style = parse_val_and_style(row.get('G', '0'))
            gs, gs_style = parse_val_and_style(row.get('GS', '0'))
            w, w_style = parse_val_and_style(row.get('W', '0'))
            l, l_style = parse_val_and_style(row.get('L', '0'))
            hld, hld_style = parse_val_and_style(row.get('HLD', '0'))
            sv, sv_style = parse_val_and_style(row.get('SV', '0'))
            qs, qs_style = parse_val_and_style(row.get('QS', '0'))
            bf, bf_style = parse_val_and_style(row.get('BF', '0'))
            bh, bh_style = parse_val_and_style(row.get('BH', '0'))
            bhr, bhr_style = parse_val_and_style(row.get('BHR', '0'))
            so, so_style = parse_val_and_style(row.get('SO', '0'))
            bb, bb_style = parse_val_and_style(row.get('BB', '0'))
            r, r_style = parse_val_and_style(row.get('R', '0'))
            er, er_style = parse_val_and_style(row.get('ER', '0'))

            tot_g += g; tot_gs += gs; tot_w += w; tot_l += l
            tot_hld += hld; tot_sv += sv; tot_outs += outs; tot_qs += qs
            tot_bf += bf; tot_bh += bh; tot_bhr += bhr; tot_so += so
            tot_bb += bb; tot_r += r; tot_er += er

            ab_against = bf - bb
            oavg_calc = (bh / ab_against) if ab_against > 0 else 0.0
            era_calc = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0
            whip_calc = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            oavg_val, oavg_style = parse_val_and_style(row.get('OAVG', ''))
            era_val, era_style = parse_val_and_style(row.get('ERA', ''))
            whip_val, whip_style = parse_val_and_style(row.get('WHIP', ''))

            oavg_final = format_cell(oavg_val if str(row.get('OAVG', '')).strip() != '' else oavg_calc, oavg_style, 3)
            era_final = format_cell(era_val if str(row.get('ERA', '')).strip() != '' else era_calc, era_style, 2)
            whip_final = format_cell(whip_val if str(row.get('WHIP', '')).strip() != '' else whip_calc, whip_style, 2)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{format_cell(g, g_style)}</td>
            <td>{format_cell(gs, gs_style)}</td>
            <td>{format_cell(w, w_style)}</td>
            <td>{format_cell(l, l_style)}</td>
            <td>{format_cell(hld, hld_style)}</td>
            <td>{format_cell(sv, sv_style)}</td>
            <td>{format_cell(ip_num, ip_style, 1)}</td>
            <td>{format_cell(qs, qs_style)}</td>
            <td>{format_cell(bf, bf_style)}</td>
            <td>{format_cell(bh, bh_style)}</td>
            <td>{format_cell(bhr, bhr_style)}</td>
            <td>{oavg_final}</td>
            <td>{format_cell(so, so_style)}</td>
            <td>{format_cell(bb, bb_style)}</td>
            <td>{format_cell(r, r_style)}</td>
            <td>{format_cell(er, er_style)}</td>
            <td>{era_final}</td>
            <td>{whip_final}</td>
          </tr>\n"""

        # 通算行 (無粗體)
        if len(group) > 0:
            tot_ip_actual = tot_outs / 3.0
            tot_ab_against = tot_bf - tot_bb
            tot_oavg = (tot_bh / tot_ab_against) if tot_ab_against > 0 else 0.0
            tot_era = (tot_er * 9.0) / tot_ip_actual if tot_ip_actual > 0 else 0.0
            tot_whip = (tot_bb + tot_bh) / tot_ip_actual if tot_ip_actual > 0 else 0.0

            rows_html += f"""          <tr>
            <td>通算</td>
            <td>-</td>
            <td>{int(tot_g)}</td>
            <td>{int(tot_gs)}</td>
            <td>{int(tot_w)}</td>
            <td>{int(tot_l)}</td>
            <td>{int(tot_hld)}</td>
            <td>{int(tot_sv)}</td>
            <td>{outs_to_ip_str(tot_outs)}</td>
            <td>{int(tot_qs)}</td>
            <td>{int(tot_bf)}</td>
            <td>{int(tot_bh)}</td>
            <td>{int(tot_bhr)}</td>
            <td>{tot_oavg:.3f}</td>
            <td>{int(tot_so)}</td>
            <td>{int(tot_bb)}</td>
            <td>{int(tot_r)}</td>
            <td>{int(tot_er)}</td>
            <td>{tot_era:.2f}</td>
            <td>{tot_whip:.2f}</td>
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
