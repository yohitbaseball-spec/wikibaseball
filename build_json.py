import os
import json
import re

# 定義要掃描的資料夾與對應國籍
folders = {
    'players': '台灣',
    'jpplayers': '日本',
    'korplayers': '韓國',
    'usaplayers': '美國'
}

all_players = []

for folder, nat in folders.items():
    if not os.path.exists(folder):
        continue
        
    for fname in os.listdir(folder):
        if fname.endswith('.html') and fname != 'index.html':
            filepath = os.path.join(folder, fname)
            try:
                # 使用 utf-8-sig 自動處理 UTF-8 BOM 隱形字元
                with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                
                # 1. 自動抓取 <title>
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                title_text = title_match.group(1).strip() if title_match else fname.replace('.html', '')
                name = title_text.split('-')[0].split('|')[0].strip()
                
                # 2. 強效版 get_meta：支援 content/name 任意順序、換行與單雙引號
                def get_meta(attr_name):
                    # 匹配 pattern A: name="..." content="..."
                    pattern1 = rf'<meta\s+[^>]*?name=["\']{attr_name}["\']\s+[^>]*?content=["\'](.*?)["\']'
                    # 匹配 pattern B: content="..." name="..."
                    pattern2 = rf'<meta\s+[^>]*?content=["\'](.*?)["\']\s+[^>]*?name=["\']{attr_name}["\']'
                    
                    match = re.search(pattern1, content, re.IGNORECASE | re.DOTALL) or \
                            re.search(pattern2, content, re.IGNORECASE | re.DOTALL)
                    
                    return match.group(1).strip() if match else '-'

                honors_raw = get_meta('honors')
                honors = [h.strip() for h in honors_raw.split(',') if h.strip() and h.strip() != '-']

                player = {
                    "url": f"{folder}/{fname}",
                    "name": name,
                    "team": get_meta('team'),
                    "number": get_meta('number'),
                    "position": get_meta('position'),
                    "nationality": nat,
                    "batsThrows": get_meta('bats-throws'),
                    "honors": honors
                }
                all_players.append(player)
                print(f"✔️ 成功讀取：{name} ({folder}/{fname})")
                
            except Exception as e:
                print(f"⚠️ 讀取 {filepath} 失敗: {e}")

# 自動建立 data 資料夾並寫入 players.json
os.makedirs('data', exist_ok=True)
with open('data/players.json', 'w', encoding='utf-8') as f:
    json.dump(all_players, f, ensure_ascii=False, indent=2)

print(f"\n✅ 成功！已自動掃描並將 {len(all_players)} 位球員資料寫入 data/players.json！")
