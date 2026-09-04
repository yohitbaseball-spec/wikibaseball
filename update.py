import os
import re
from urllib.parse import quote
import requests

SHEET_ID = os.environ.get("SHEET_ID")
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not SHEET_ID:
    print("❌ 錯誤：未設定 SHEET_ID")  
    exit(1)

if not API_KEY:
    print("❌ 錯誤：未設定 GOOGLE_API_KEY")
    exit(1)


def ip_to_outs(ip_str):
    """將投球局數 (IP) 轉為總出局數 (Outs)"""
    try:
        clean_ip = re.sub(r"[^\d.]", "", str(ip_str))
        if not clean_ip:
            return 0
        ip_float = float(clean_ip)
        i = int(ip_float)
        f = round(ip_float - i, 1)
        outs = i * 3
        if f == 0.1:
            outs += 1
        elif f == 0.2:
            outs += 2
        return outs
    except Exception:
        return 0


def outs_to_ip_str(outs):
    """將總出局數 (Outs) 轉回 IP 格式字串 (例如 2.1)"""
    i = outs // 3
    f = outs % 3
    if f == 0:
        return f"{i}"
    else:
        return f"{i}.{f}"


def fetch_sheet_data_with_styles(sheet_name):
    """透過 Google Sheets API v4 讀取資料與儲存格視覺樣式 (粗體/紅字)"""
    encoded_sheet_name = quote(sheet_name)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?ranges={encoded_sheet_name}&fields=sheets/data/rowData/values(formattedValue,effectiveFormat/textFormat)&key={API_KEY}"

    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"⚠️ 無法讀取分頁 [{sheet_name}]: {res.text}")
            return None

        data = res.json()
        sheets = data.get("sheets", [])
        if not sheets:
            return None

        row_data = sheets[0].get("data", [{}])[0].get("rowData", [])
        if not row_data:
            return None

        # 第一列為標題 Header
        header_cells = row_data[0].get("values", [])
        headers = [
            c.get("formattedValue", "").strip() for c in header_cells
        ]

        parsed_rows = []
        for row in row_data[1:]:
            cells = row.get("values", [])
            row_dict = {}
            for idx, cell in enumerate(cells):
                if idx < len(headers) and headers[idx]:
                    row_dict[headers[idx]] = cell
            parsed_rows.append(row_dict)

        return parsed_rows
    except Exception as e:
        print(f"⚠️ 讀取試算表失敗 [{sheet_name}]: {e}")
        return None


def parse_cell(cell):
    """解析儲存格，回傳 (純數字/字串, HTML套用樣式後結果)"""
    if not cell:
        return 0.0, "-"

    formatted_val = cell.get("formattedValue", "-").strip()
    if not formatted_val or formatted_val == "-" or formatted_val.lower() == "nan":
        return 0.0, "-"

    # 取得 Google 試算表內的文字格式
    text_format = cell.get("effectiveFormat", {}).get("textFormat", {})
    is_bold = text_format.get("bold", False)

    color = text_format.get("foregroundColor", {})
    r = color.get("red", 0)
    g = color.get("green", 0)
    b = color.get("blue", 0)

    # 判定文字是否為紅色 (Red 顯著高於 Green/Blue)
    is_red = r > 0.6 and g < 0.3 and b < 0.3

    # 自動套用 HTML 標籤
    if is_red:
        html_str = f'<b style="color: red;">{formatted_val}</b>'
    elif is_bold:
        html_str = f"<b>{formatted_val}</b>"
    else:
        html_str = formatted_val

    # 提煉純數值供運算（如通算計算）
    clean_num_str = "".join(
        [c for c in formatted_val if c.isdigit() or c == "."]
    )
    try:
        num = float(clean_num_str) if clean_num_str else 0.0
    except ValueError:
        num = 0.0

    return num, html_str


def process_batting_stats():
    rows = fetch_sheet_data_with_styles("打擊成績")
    if not rows:
        return {}

    # 按 player_id 分組
    player_groups = {}
    for row in rows:
        pid = row.get("player_id", {}).get("formattedValue", "").strip()
        if not pid:
            continue
        player_groups.setdefault(pid, []).append(row)

    batting_by_player = {}
    for pid, group in player_groups.items():
        rows_html = ""
        tot_g = tot_pa = tot_ab = tot_h = tot_2b = tot_3b = tot_hr = 0.0
        tot_rbi = tot_r = tot_sb = tot_tb = tot_so = tot_bb = tot_sac = (
            tot_sf
        ) = 0.0

        for row in group:
            _, year_str = parse_cell(row.get("year"))
            team_str = row.get("team", {}).get("formattedValue", "").strip()

            g, g_html = parse_cell(row.get("G"))
            pa, pa_html = parse_cell(row.get("PA"))
            ab, ab_html = parse_cell(row.get("AB"))
            h, h_html = parse_cell(row.get("H"))
            b2, b2_html = parse_cell(row.get("2B"))
            b3, b3_html = parse_cell(row.get("3B"))
            hr, hr_html = parse_cell(row.get("HR"))
            rbi, rbi_html = parse_cell(row.get("RBI"))
            r, r_html = parse_cell(row.get("R"))
            sb, sb_html = parse_cell(row.get("SB"))
            so, so_html = parse_cell(row.get("SO"))
            bb, bb_html = parse_cell(row.get("BB"))
            sac, sac_html = parse_cell(row.get("SAC"))
            sf, sf_html = parse_cell(row.get("SF"))

            tb, tb_html = parse_cell(row.get("TB"))
            if tb_html == "-":
                tb = h + b2 + (2 * b3) + (3 * hr)
                tb_html = f"{int(tb)}"

            # 計算率項（若 Excel 無自訂樣式則用算出的，若有樣式以 Excel 呈現為主）
            avg_calc = (h / ab) if ab > 0 else 0.0
            obp_calc = ((h + bb) / (ab + bb + sf)) if (ab + bb + sf) > 0 else 0.0
            slg_calc = (tb / ab) if ab > 0 else 0.0
            ops_calc = obp_calc + slg_calc

            _, avg_html = parse_cell(row.get("AVG"))
            _, obp_html = parse_cell(row.get("OBP"))
            _, slg_html = parse_cell(row.get("SLG"))
            _, ops_html = parse_cell(row.get("OPS"))

            avg_final = avg_html if avg_html != "-" else f"{avg_calc:.3f}"
            obp_final = obp_html if obp_html != "-" else f"{obp_calc:.3f}"
            slg_final = slg_html if slg_html != "-" else f"{slg_calc:.3f}"
            ops_final = ops_html if ops_html != "-" else f"{ops_calc:.3f}"

            tot_g += g
            tot_pa += pa
            tot_ab += ab
            tot_h += h
            tot_2b += b2
            tot_3b += b3
            tot_hr += hr
            tot_rbi += rbi
            tot_r += r
            tot_sb += sb
            tot_tb += tb
            tot_so += so
            tot_bb += bb
            tot_sac += sac
            tot_sf += sf

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{g_html}</td>
            <td>{pa_html}</td>
            <td>{ab_html}</td>
            <td>{h_html}</td>
            <td>{b2_html}</td>
            <td>{b3_html}</td>
            <td>{hr_html}</td>
            <td>{rbi_html}</td>
            <td>{r_html}</td>
            <td>{sb_html}</td>
            <td>{tb_html}</td>
            <td>{so_html}</td>
            <td>{bb_html}</td>
            <td>{sac_html}</td>
            <td>{sf_html}</td>
            <td>{avg_final}</td>
            <td>{obp_final}</td>
            <td>{slg_final}</td>
            <td>{ops_final}</td>
          </tr>\n"""

        # 通算列
        if len(group) > 0:
            tot_avg = (tot_h / tot_ab) if tot_ab > 0 else 0.0
            tot_obp = (
                ((tot_h + tot_bb) / (tot_ab + tot_bb + tot_sf))
                if (tot_ab + tot_bb + tot_sf) > 0
                else 0.0
            )
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

        batting_by_player[pid] = rows_html

    return batting_by_player


def process_pitching_stats():
    rows = fetch_sheet_data_with_styles("投手成績")
    if not rows:
        return {}

    player_groups = {}
    for row in rows:
        pid = row.get("player_id", {}).get("formattedValue", "").strip()
        if not pid:
            continue
        player_groups.setdefault(pid, []).append(row)

    pitching_by_player = {}
    for pid, group in player_groups.items():
        rows_html = ""
        tot_g = tot_gs = tot_w = tot_l = tot_hld = tot_sv = tot_outs = (
            tot_qs
        ) = 0.0
        tot_bf = tot_bh = tot_bhr = tot_so = tot_bb = tot_r = tot_er = 0.0

        for row in group:
            _, year_str = parse_cell(row.get("year"))
            team_str = row.get("team", {}).get("formattedValue", "").strip()

            # 局數與出局數處理
            raw_ip_val = row.get("IP", {}).get("formattedValue", "0")
            outs = ip_to_outs(raw_ip_val)
            _, ip_html = parse_cell(row.get("IP"))
            ip_actual = outs / 3.0

            g, g_html = parse_cell(row.get("G"))
            gs, gs_html = parse_cell(row.get("GS"))
            w, w_html = parse_cell(row.get("W"))
            l, l_html = parse_cell(row.get("L"))
            hld, hld_html = parse_cell(row.get("HLD"))
            sv, sv_html = parse_cell(row.get("SV"))
            qs, qs_html = parse_cell(row.get("QS"))
            bf, bf_html = parse_cell(row.get("BF"))
            bh, bh_html = parse_cell(row.get("BH"))
            bhr, bhr_html = parse_cell(row.get("BHR"))
            so, so_html = parse_cell(row.get("SO"))
            bb, bb_html = parse_cell(row.get("BB"))
            r, r_html = parse_cell(row.get("R"))
            er, er_html = parse_cell(row.get("ER"))

            tot_g += g
            tot_gs += gs
            tot_w += w
            tot_l += l
            tot_hld += hld
            tot_sv += sv
            tot_outs += outs
            tot_qs += qs
            tot_bf += bf
            tot_bh += bh
            tot_bhr += bhr
            tot_so += so
            tot_bb += bb
            tot_r += r
            tot_er += er

            ab_against = bf - bb
            oavg_calc = (bh / ab_against) if ab_against > 0 else 0.0
            era_calc = (er * 9.0) / ip_actual if ip_actual > 0 else 0.0
            whip_calc = (bb + bh) / ip_actual if ip_actual > 0 else 0.0

            _, oavg_html = parse_cell(row.get("OAVG"))
            _, era_html = parse_cell(row.get("ERA"))
            _, whip_html = parse_cell(row.get("WHIP"))

            oavg_final = oavg_html if oavg_html != "-" else f"{oavg_calc:.3f}"
            era_final = era_html if era_html != "-" else f"{era_calc:.2f}"
            whip_final = whip_html if whip_html != "-" else f"{whip_calc:.2f}"

            rows_html += f"""          <tr>
            <td>{year_str}</td>
            <td>{team_str}</td>
            <td>{g_html}</td>
            <td>{gs_html}</td>
            <td>{w_html}</td>
            <td>{l_html}</td>
            <td>{hld_html}</td>
            <td>{sv_html}</td>
            <td>{ip_html}</td>
            <td>{qs_html}</td>
            <td>{bf_html}</td>
            <td>{bh_html}</td>
            <td>{bhr_html}</td>
            <td>{oavg_final}</td>
            <td>{so_html}</td>
            <td>{bb_html}</td>
            <td>{r_html}</td>
            <td>{er_html}</td>
            <td>{era_final}</td>
            <td>{whip_final}</td>
          </tr>\n"""

        # 通算列
        if len(group) > 0:
            tot_ip_actual = tot_outs / 3.0
            tot_ab_against = tot_bf - tot_bb
            tot_oavg = (
                (tot_bh / tot_ab_against) if tot_ab_against > 0 else 0.0
            )
            tot_era = (
                (tot_er * 9.0) / tot_ip_actual if tot_ip_actual > 0 else 0.0
            )
            tot_whip = (
                (tot_bb + tot_bh) / tot_ip_actual if tot_ip_actual > 0 else 0.0
            )

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

        pitching_by_player[pid] = rows_html

    return pitching_by_player


def update_html_files():
    batting_data = process_batting_stats()
    pitching_data = process_pitching_stats()

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                updated = False

                for pid, html_rows in batting_data.items():
                    if pid in content and "<!-- STATS_START -->" in content:
                        start_tag = "<!-- STATS_START -->"
                        end_tag = "<!-- STATS_END -->"
                        idx1 = content.find(start_tag) + len(start_tag)
                        idx2 = content.find(end_tag)
                        if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                            content = (
                                content[:idx1]
                                + "\n"
                                + html_rows
                                + "        "
                                + content[idx2:]
                            )
                            updated = True

                for pid, html_rows in pitching_data.items():
                    if (
                        pid in content
                        and "<!-- PITCHER_STATS_START -->" in content
                    ):
                        start_tag = "<!-- PITCHER_STATS_START -->"
                        end_tag = "<!-- PITCHER_STATS_END -->"
                        idx1 = content.find(start_tag) + len(start_tag)
                        idx2 = content.find(end_tag)
                        if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                            content = (
                                content[:idx1]
                                + "\n"
                                + html_rows
                                + "        "
                                + content[idx2:]
                            )
                            updated = True

                if updated:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ 已成功更新球員網頁: {filepath}")


if __name__ == "__main__":
    update_html_files()
