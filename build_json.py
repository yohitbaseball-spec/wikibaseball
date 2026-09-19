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
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 自動抓取 <title>
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                title_text = title_match.group(1).strip() if title_match else fname.replace('.html', '')
                name = title_text.split('-')[0].strip()
                
                # 自動抓取 <meta> 標籤
                def get_meta(attr_name):
                    pattern = rf'<meta\s+name=["\']{attr_name}["\']\s+content=["\'](.*?)["\']'
                    match = re.search(pattern, content, re.IGNORECASE)
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
            except Exception as e:
                print(f"⚠️ 讀取 {filepath} 失敗: {e}")

# 自動建立 data 資料夾並寫入 players.json
os.makedirs('data', exist_ok=True)
with open('data/players.json', 'w', encoding='utf-8') as f:
    json.dump(all_players, f, ensure_ascii=False, indent=2)

print(f"✅ 成功！已自動掃描並將 {len(all_players)} 位球員資料寫入 data/players.json！")
