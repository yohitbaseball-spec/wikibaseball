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

def parse_num_and_star(raw_val):
    """
    強健解析函數：利用正則表達式拆解數字與星號
    避免隱藏字元導致數值歸零
    """
    s = str(raw_val).strip()
    if not s or s == '-':
        return 0.0, ''

    # 判斷星號種類
    star_type = ''
    if '**' in s:
        star_type = '**'
    elif '*' in s:
        star_type = '*'

    # 精準擷取數字部分 (包含負號和小數點)
    match = re.search(r'[-+]?\d*\.?\d+', s)
    if match:
        try:
            num = float(match.group())
        except:
            num = 0.0
    else:
        num = 0.0

    return num, star_type

def format_cell(num, star_type, precision=0):
    """
    根據數字與星號種類格式化 HTML 輸出
    """
    if precision == 3:
        formatted_num = f"{num:.3f}"
    elif precision == 2:
        formatted_num = f"{num:.2f}"
    else:
        formatted_num = f"{int(num)}" if float(num).is_integer() else f"{num}"

    if star_type == '**':
        return f'<b style="color: red;">{formatted_num}</b>'
    elif star_type == '*':
        return f'<b>{formatted_num}</b>'
    else:
        return formatted_num

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
        
        tot_g = tot_pa = tot_ab = tot_h = tot_2b = tot_3b = tot_hr = 0.0
        tot_rbi = tot_r = tot_sb = tot_tb = tot_so = tot_bb = tot_sac = tot_sf = 0.0

        for _, row in group.iterrows():
            year_val, y_star = parse_num_and_star(row.get('year', ''))
            year_str = format_cell(year_val, y_star, 0) if str(row.get('year', '')).strip() != '' else ''
            team_str = str(row.get('team', '')).strip()

            g, g_star = parse_num_and_star(row.get('G', '0'))
            pa, pa_star = parse_num_and_star(row.get('PA', '0'))
            ab, ab_star = parse_num_and_star(row.get('AB', '0'))
            h, h_star = parse_num_and_star(row.get('H', '0'))
            b2, b2_star = parse_num_and_star(row.get('2B', '0'))
            b3, b3_star = parse_num_and_star(row.get('3B', '0'))
            hr, hr_star = parse_num_and_star(row.get('HR', '0'))
            rbi, rbi_star = parse_num_and_star(row.get('RBI', '0'))
            r, r_star = parse_num_and_star(row.get('R', '0'))
            sb, sb_star = parse_num_and_star(row.get('SB', '0'))
            so, so_star = parse_num_and_star(row.get('SO', '0'))
            bb, bb_star = parse_num_and_star(row.get('BB', '0'))
            sac, sac_star = parse_num_and_star(row.get('SAC', '0'))
            sf, sf_star = parse_num_and_star(row.get('SF', '0'))

            raw_tb = str(row.get('TB', '')).strip()
            if raw_tb != "":
                tb, tb_star = parse_num_and_star(raw_tb)
            else:
                tb = h + b2 + (2 * b3) + (3 * hr)
                tb_star = ''

            # 通算數字累加
            tot_g += g; tot_pa += pa; tot_ab += ab; tot_h += h
            tot_2b += b2; tot_3b += b3; tot_hr += hr; tot_rbi += rbi
            tot_r += r; tot_sb += sb; tot_tb += tb; tot_so += so
            tot_bb += bb; tot_sac += sac; tot_sf += sf

            avg_calc = (h / ab) if ab > 0 else 0.0
            obp_calc = ((h + bb) / (ab + bb + sf)) if (ab + bb + sf) > 0 else 0.0
            slg_calc = (tb / ab) if ab > 0 else 0.0
            ops_calc = obp_calc + slg_calc

            avg_val, avg_star = parse_num_and_star(row.get('AVG', ''))
            obp_val, obp_star = parse_num_and_star(row.get('OBP', ''))
            slg_val, slg_star = parse_num_and_star(row.get('SLG', ''))
            ops_val, ops_star = parse_num_and_star(row.get('OPS', ''))

            avg_final = format_cell(avg_val if str(row.get('AVG', '')).strip() != '' else avg_calc, avg_star, 3)
            obp_final = format_cell(obp_val if str(row.get('OBP', '')).strip() != '' else obp_calc, obp_star, 3)
            slg_final = format_cell(slg_val if str(row.get('SLG', '')).strip() != '' else slg_calc, slg_star, 3)
            ops_final = format_cell(ops_val if str(row.get('OPS', '')).strip() != '' else ops_calc, ops_star, 3)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{format_cell(g, g_star)}</td>
            <td>{format_cell(pa, pa_star)}</td>
            <td>{format_cell(ab, ab_star)}</td>
            <td>{format_cell(h, h_star)}</td>
            <td>{format_cell(b2, b2_star)}</td>
            <td>{format_cell(b3, b3_star)}</td>
            <td>{format_cell(hr, hr_star)}</td>
            <td>{format_cell(rbi, rbi_star)}</td>
            <td>{format_cell(r, r_star)}</td>
            <td>{format_cell(sb, sb_star)}</td>
            <td>{format_cell(tb, tb_star)}</td>
            <td>{format_cell(so, so_star)}</td>
            <td>{format_cell(bb, bb_star)}</td>
            <td>{format_cell(sac, sac_star)}</td>
            <td>{format_cell(sf, sf_star)}</td>
            <td>{avg_final}</td>
            <td>{obp_final}</td>
            <td>{slg_final}</td>
            <td>{ops_final}</td>
          </tr>\n"""

        # 通算行
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
        
        tot_g = tot_gs = tot_w = tot_l = tot_hld = tot_sv = tot_outs = tot_qs = 0.0
        tot_bf = tot_bh = tot_bhr = tot_so = tot_bb = tot_r = tot_er = 0.0

        for _, row in group.iterrows():
            year_val, y_star = parse_num_and_star(row.get('year', ''))
            year_str = format_cell(year_val, y_star, 0) if str(row.get('year', '')).strip() != '' else ''
            team_str = str(row.get('team', '')).strip()

            ip_val_raw = row.get('IP', '0')
            ip_num, ip_star = parse_num_and_star(ip_val_raw)
            outs = ip_to_outs(ip_val_raw)
            ip_actual = outs / 3.0

            g, g_star = parse_num_and_star(row.get('G', '0'))
            gs, gs_star = parse_num_and_star(row.get('GS', '0'))
            w, w_star = parse_num_and_star(row.get('W', '0'))
            l, l_star = parse_num_and_star(row.get('L', '0'))
            hld, hld_star = parse_num_and_star(row.get('HLD', '0'))
            sv, sv_star = parse_num_and_star(row.get('SV', '0'))
            qs, qs_star = parse_num_and_star(row.get('QS', '0'))
            bf, bf_star = parse_num_and_star(row.get('BF', '0'))
            bh, bh_star = parse_num_and_star(row.get('BH', '0'))
            bhr, bhr_star = parse_num_and_star(row.get('BHR', '0'))
            so, so_star = parse_num_and_star(row.get('SO', '0'))
            bb, bb_star = parse_num_and_star(row.get('BB', '0'))
            r, r_star = parse_num_and_star(row.get('R', '0'))
            er, er_star = parse_num_and_star(row.get('ER', '0'))

            tot_g += g; tot_gs += gs; tot_w += w; tot_l += l
            tot_hld += hld; tot_sv += sv; tot_outs += outs; tot_qs += qs
            tot_bf += bf; tot_bh += bh; tot_bhr += bhr; tot_so += so
            tot_bb += bb; tot_r += r; tot_er += er

            ab_against = bf - bb
            oavg_calc = (bh / ab_against) if ab_against > 0 else 0.0
            era_calc = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0
            whip_calc = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            oavg_val, oavg_star = parse_num_and_star(row.get('OAVG', ''))
            era_val, era_star = parse_num_and_star(row.get('ERA', ''))
            whip_val, whip_star = parse_num_and_star(row.get('WHIP', ''))

            oavg_final = format_cell(oavg_val if str(row.get('OAVG', '')).strip() != '' else oavg_calc, oavg_star, 3)
            era_final = format_cell(era_val if str(row.get('ERA', '')).strip() != '' else era_calc, era_star, 2)
            whip_final = format_cell(whip_val if str(row.get('WHIP', '')).strip() != '' else whip_calc, whip_star, 2)

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{format_cell(g, g_star)}</td>
            <td>{format_cell(gs, gs_star)}</td>
            <td>{format_cell(w, w_star)}</td>
            <td>{format_cell(l, l_star)}</td>
            <td>{format_cell(hld, hld_star)}</td>
            <td>{format_cell(sv, sv_star)}</td>
            <td>{format_cell(ip_num, ip_star, 1 if ip_num % 1 != 0 else 0)}</td>
            <td>{format_cell(qs, qs_star)}</td>
            <td>{format_cell(bf, bf_star)}</td>
            <td>{format_cell(bh, bh_star)}</td>
            <td>{format_cell(bhr, bhr_star)}</td>
            <td>{oavg_final}</td>
            <td>{format_cell(so, so_star)}</td>
            <td>{format_cell(bb, bb_star)}</td>
            <td>{format_cell(r, r_star)}</td>
            <td>{format_cell(er, er_star)}</td>
            <td>{era_final}</td>
            <td>{whip_final}</td>
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
