import os
import re
import pandas as pd

sheet_id = os.environ.get('SHEET_ID')
if not sheet_id:
    print('❌ 錯誤：未設定 GOOGLE_SHEET_ID Secrets！')
    exit(1)

url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
print(f'🔍 正在從試算表讀取數據 (ID: {sheet_id})...')

try:
    df = pd.read_csv(url)
    print('✅ 成功取得試算表數據！')
except Exception as e:
    print(f'❌ 讀取 Google 試算表失敗: {e}')
    exit(1)

df.columns = df.columns.str.strip()
print('📋 試算表包含欄位:', list(df.columns))

def fmt_rate(val):
    if pd.isna(val) or val == 0:
        return '.000'
    s = f'{val:.3f}'
    return s[1:] if s.startswith('0.') else s

group_col = 'player_name' if 'player_name' in df.columns else 'player_id'
if group_col not in df.columns:
    print(f'❌ 錯誤：試算表中未找到 player_name 或 player_id 欄位！現有欄位為: {list(df.columns)}')
    exit(1)

grouped = df.groupby(group_col)
print(f'👤 試算表中共找到 {len(grouped)} 位球員數據。')

for player_name, group in grouped:
    player_name = str(player_name).strip()
    if not player_name or player_name == 'nan':
        continue

    print(f'\n⚙️ 正在處理球員: [{player_name}]')
    group = group.copy()

    num_cols = ['year', 'G', 'PA', 'AB', 'H', '2B', '3B', 'HR', 'RBI', 'R', 'SB', 'SO', 'BB', 'SAC', 'SF']
    for col in num_cols:
        if col in group.columns:
            group[col] = pd.to_numeric(group[col], errors='coerce').fillna(0)

    group['1B'] = group['H'] - group['2B'] - group['3B'] - group['HR']
    group['TB'] = group['1B'] + group['2B']*2 + group['3B']*3 + group['HR']*4

    group['AVG'] = group['H'] / group['AB']
    group['OBP'] = (group['H'] + group['BB']) / (group['AB'] + group['BB'] + group['SF'])
    group['SLG'] = group['TB'] / group['AB']
    group['OPS'] = group['OBP'] + group['SLG']

    rows_html = []
    for _, r in group.iterrows():
        row = f'''    <tr>
        <td>{int(r["year"])}</td>
        <td>{r["team"]}</td>
        <td>{int(r["G"])}</td>
        <td>{int(r["PA"])}</td>
        <td>{int(r["AB"])}</td>
        <td>{int(r["H"])}</td>
        <td>{int(r["2B"])}</td>
        <td>{int(r["3B"])}</td>
        <td>{int(r["HR"])}</td>
        <td>{int(r["RBI"])}</td>
        <td>{int(r["R"])}</td>
        <td>{int(r["SB"])}</td>
        <td>{int(r["TB"])}</td>
        <td>{int(r["SO"])}</td>
        <td>{int(r["BB"])}</td>
        <td>{int(r["SAC"])}</td>
        <td>{int(r["SF"])}</td>
        <td>{fmt_rate(r["AVG"])}</td>
        <td>{fmt_rate(r["OBP"])}</td>
        <td>{fmt_rate(r["SLG"])}</td>
        <td>{fmt_rate(r["OPS"])}</td>
      </tr>'''
        rows_html.append(row)

    tot_G = group['G'].sum()
    tot_PA = group['PA'].sum()
    tot_AB = group['AB'].sum()
    tot_H = group['H'].sum()
    tot_2B = group['2B'].sum()
    tot_3B = group['3B'].sum()
    tot_HR = group['HR'].sum()
    tot_RBI = group['RBI'].sum()
    tot_R = group['R'].sum()
    tot_SB = group['SB'].sum()
    tot_TB = group['TB'].sum()
    tot_SO = group['SO'].sum()
    tot_BB = group['BB'].sum()
    tot_SAC = group['SAC'].sum()
    tot_SF = group['SF'].sum()

    tot_AVG = tot_H / tot_AB if tot_AB > 0 else 0
    tot_OBP = (tot_H + tot_BB) / (tot_AB + tot_BB + tot_SF) if (tot_AB + tot_BB + tot_SF) > 0 else 0
    tot_SLG = tot_TB / tot_AB if tot_AB > 0 else 0
    tot_OPS = tot_OBP + tot_SLG

    tot_row = f'''    <tr>
        <td colspan="2">通算成績</td>
        <td>{int(tot_G)}</td>
        <td>{int(tot_PA)}</td>
        <td>{int(tot_AB)}</td>
        <td>{int(tot_H)}</td>
        <td>{int(tot_2B)}</td>
        <td>{int(tot_3B)}</td>
        <td>{int(tot_HR)}</td>
        <td>{int(tot_RBI)}</td>
        <td>{int(tot_R)}</td>
        <td>{int(tot_SB)}</td>
        <td>{int(tot_TB)}</td>
        <td>{int(tot_SO)}</td>
        <td>{int(tot_BB)}</td>
        <td>{int(tot_SAC)}</td>
        <td>{int(tot_SF)}</td>
        <td>{fmt_rate(tot_AVG)}</td>
        <td>{fmt_rate(tot_OBP)}</td>
        <td>{fmt_rate(tot_SLG)}</td>
        <td>{fmt_rate(tot_OPS)}</td>
      </tr>'''
    rows_html.append(tot_row)

    new_tbody_content = '\n' + '\n'.join(rows_html) + '\n    '

    updated_any = False
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                has_name = player_name in html_content
                has_tag = '<!-- STATS_START -->' in html_content

                if has_name and has_tag:
                    pattern = r'(<!-- STATS_START -->)(.*?)(<!-- STATS_END -->)'
                    replacement = r'\1' + new_tbody_content + r'\3'
                    updated_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(updated_html)
                    print(f'  ✅ 成功更新檔案: {filepath}')
                    updated_any = True

    if not updated_any:
        print(f'  ⚠️ 找不到對應 [{player_name}] 名字且含有 <!-- STATS_START --> 的 HTML 檔案。')
