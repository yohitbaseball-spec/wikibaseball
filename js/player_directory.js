// 請替換成你的 GitHub 帳號與專案 Repository 名稱
const GITHUB_USER = 'yohitbaseball-spec';
const REPO_NAME = 'wikibaseball';

// 💡 只要在這裡新增資料夾名稱，程式就會自動去抓取！
const PLAYER_FOLDERS = ['players', 'jpplayers'];

let allPlayers = [];

document.addEventListener('DOMContentLoaded', async () => {
  try {
    // 1. 同時對所有指定的資料夾發送 GitHub API 請求
    const folderRequests = PLAYER_FOLDERS.map(folder =>
      fetch(`https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/contents/${folder}`)
        .then(res => res.ok ? res.json() : []) // 如果資料夾不存在則回傳空陣列，避免報錯
        .then(files => files.map(file => ({ ...file, folderName: folder }))) // 記錄該檔案來自哪個資料夾
    );

    // 等待所有資料夾的檔案列表回傳並合併為一個大陣列
    const nestedFiles = await Promise.all(folderRequests);
    const allFiles = nestedFiles.flat();

    // 2. 過濾出所有 .html 檔案（排除 index.html）
    const htmlFiles = allFiles.filter(file => file.name.endsWith('.html') && file.name !== 'index.html');

    // 3. 抓取每個 HTML 檔案的內容並解析 Meta 資料
    allPlayers = await Promise.all(htmlFiles.map(async (file) => {
      const htmlText = await fetch(file.download_url).then(res => res.text());
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlText, 'text/html');

      // 自動從 meta 標籤提取國籍/來源資料夾（可選）
      const nationalityMap = {
        'players': '台灣',
        'jpplayers': '日本'
      };

      return {
        url: file.path, // 檔案相對路徑（會自動包含資料夾名稱，如 players/xxx.html 或 jpplayers/ooo.html）
        name: doc.querySelector('title')?.innerText.split('-')[0].trim() || file.name.replace('.html', ''),
        team: doc.querySelector('meta[name="team"]')?.getAttribute('content') || '未指定',
        number: doc.querySelector('meta[name="number"]')?.getAttribute('content') || '-',
        position: doc.querySelector('meta[name="position"]')?.getAttribute('content') || '-',
        batsThrows: doc.querySelector('meta[name="bats-throws"]')?.getAttribute('content') || '-',
        // 國籍：優先抓取 HTML 內的 meta，若沒有就根據資料夾自動判斷
        nationality: doc.querySelector('meta[name="nationality"]')?.getAttribute('content') || nationalityMap[file.folderName] || '其他',
        honors: doc.querySelector('meta[name="honors"]')?.getAttribute('content')?.split(',') || []
      };
    }));

    // 4. 渲染表格
    renderPlayers(allPlayers);

    // 5. 綁定即時搜尋（支援搜尋國籍、姓名、球隊或背號）
    document.getElementById('searchInput')?.addEventListener('input', (e) => {
      const keyword = e.target.value.toLowerCase();
      const filtered = allPlayers.filter(p => 
        p.name.toLowerCase().includes(keyword) || 
        p.team.toLowerCase().includes(keyword) || 
        p.number.includes(keyword) ||
        p.nationality.toLowerCase().includes(keyword)
      );
      renderPlayers(filtered);
    });

  } catch (error) {
    console.error('自動載入球員失敗：', error);
  }
});

// 繪製球員名冊表格
function renderPlayers(players) {
  const tbody = document.getElementById('playerTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  players.forEach(p => {
    const tr = document.createElement('tr');
    
    const honorsHtml = p.honors
      .filter(h => h.trim() !== '')
      .map(h => `<span class="honor-tag">${h.trim()}</span>`).join(' ');

    tr.innerHTML = `
      <td><strong>#${p.number}</strong></td>
      <td><a href="../${p.url}" class="player-link">${p.name}</a></td>
      <td>${p.team}</td>
      <td>${p.position}</td>
      <td>${p.nationality}</td>
      <td>${p.batsThrows}</td>
      <td>${honorsHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}
