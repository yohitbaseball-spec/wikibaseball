const GITHUB_USER = 'yohitbaseball-spec';
const REPO_NAME = 'wikibaseball';
const PLAYER_FOLDERS = ['players', 'jpplayers'];

let allPlayers = [];
let currentFilter = {
  keyword: '',
  pos: 'ALL',
  bt: 'ALL',
  index: 'ALL'
};

document.addEventListener('DOMContentLoaded', async () => {
  try {
    // 1. 讀取 GitHub 檔案列表
    const folderRequests = PLAYER_FOLDERS.map(folder =>
      fetch(`https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/contents/${folder}`)
        .then(res => res.ok ? res.json() : [])
        .then(files => files.map(file => ({ ...file, folderName: folder })))
    );

    const nestedFiles = await Promise.all(folderRequests);
    const htmlFiles = nestedFiles.flat().filter(file => file.name.endsWith('.html') && file.name !== 'index.html');

    // 2. 解析球員 Meta 資料
    allPlayers = await Promise.all(htmlFiles.map(async (file) => {
      const htmlText = await fetch(file.download_url).then(res => res.text());
      const doc = new DOMParser().parseFromString(htmlText, 'text/html');
      
      const name = doc.querySelector('title')?.innerText.split('-')[0].trim() || file.name.replace('.html', '');
      const pos = doc.querySelector('meta[name="position"]')?.getAttribute('content') || '-';

      return {
        url: file.path,
        name: name,
        initialIndex: getFirstCharIndex(name), // 自動判斷注音或英文首字母
        team: doc.querySelector('meta[name="team"]')?.getAttribute('content') || '未指定',
        number: doc.querySelector('meta[name="number"]')?.getAttribute('content') || '-',
        position: pos,
        posCategory: getPosCategory(pos), // 歸類為 P, C, IF, OF
        nationality: file.folderName === 'jpplayers' ? '日本' : '台灣',
        batsThrows: doc.querySelector('meta[name="bats-throws"]')?.getAttribute('content') || '-',
        honors: doc.querySelector('meta[name="honors"]')?.getAttribute('content')?.split(',') || []
      };
    }));

    // 3. 自動渲染注音/字母索引軌道按鈕
    buildIndexBar(allPlayers);

    // 4. 初始化事件監聽
    initFilterEvents();

    // 5. 渲染表格
    applyFilters();

  } catch (error) {
    console.error('載入失敗：', error);
  }
});

// 判斷守備類別 (IF/OF/P/C)
function getPosCategory(pos) {
  if (pos.includes('P')) return 'P';
  if (pos.includes('C')) return 'C';
  if (['1B', '2B', '3B', 'SS', 'IF'].some(p => pos.includes(p))) return 'IF';
  if (['OF', 'LF', 'CF', 'RF'].some(p => pos.includes(p))) return 'OF';
  return 'OTHER';
}

// 判斷姓名首字 (注音/英文首字)
function getFirstCharIndex(name) {
  const char = name.charAt(0);
  if (/[a-zA-Z]/.test(char)) return char.toUpperCase();
  
  // 簡易注音聲母對應表
  const zhuyinBorders = [
    ['ㄅ', '八'], ['ㄆ', '勹'], ['ㄇ', '嘸'], ['ㄈ', '匚'], ['ㄉ', '怛'],
    ['ㄊ', '獺'], ['ㄋ', 'ㄋ'], ['ㄌ', '拉'], ['ㄍ', '圪'], ['ㄎ', '丂'],
    ['ㄏ', '呵'], ['ㄐ', '丩'], ['ㄑ', 'ㄑ'], ['ㄒ', '丅'], ['ㄓ', 'ㄓ'],
    ['ㄔ', '彳'], ['ㄕ', '尸'], ['ㄖ', 'ㄖ'], ['ㄗ', 'ㄗ'], ['ㄘ', 'ㄘ'],
    ['ㄙ', '厶'], ['ㄚ', '丫'], ['ㄛ', '喔'], ['ㄜ', '妸'], ['ㄝ', 'ㄝ'],
    ['ㄞ', '挨'], ['ㄟ', 'ㄟ'], ['ㄠ', 'ㄠ'], ['ㄡ', '歐'], ['ㄢ', 'ㄢ'],
    ['ㄣ', 'ㄣ'], ['ㄤ', 'ㄤ'], ['ㄥ', '鞥'], ['ㄦ', '兒'], ['ㄧ', '一'],
    ['ㄨ', '兀'], ['ㄩ', 'ㄩ']
  ];

  for (let i = zhuyinBorders.length - 1; i >= 0; i--) {
    if (char.localeCompare(zhuyinBorders[i][1], 'zh-TW-u-co-zhuyin') >= 0) {
      return zhuyinBorders[i][0];
    }
  }
  return '其他';
}

// 動態建立索引按鈕
function buildIndexBar(players) {
  const indexSet = new Set(players.map(p => p.initialIndex));
  const sortedIndexes = Array.from(indexSet).sort((a, b) => a.localeCompare(b, 'zh-TW'));
  
  const bar = document.getElementById('alphaIndexBar');
  sortedIndexes.forEach(idx => {
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.dataset.index = idx;
    btn.innerText = idx;
    bar.appendChild(btn);
  });
}

// 多維度交叉過濾與事件綁定
function initFilterEvents() {
  // 文字搜尋
  document.getElementById('searchInput')?.addEventListener('input', (e) => {
    currentFilter.keyword = e.target.value.toLowerCase();
    applyFilters();
  });

  // 通用按鈕點擊切換
  const bindButtonGroup = (containerId, key) => {
    document.getElementById(containerId)?.addEventListener('click', (e) => {
      if (e.target.classList.contains('filter-btn')) {
        document.querySelectorAll(`#${containerId} .filter-btn`).forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter[key] = e.target.dataset[key];
        applyFilters();
      }
    });
  };

  bindButtonGroup('posFilter', 'pos');
  bindButtonGroup('btFilter', 'bt');
  bindButtonGroup('alphaIndexBar', 'index');
}

// 執行多條件交叉過濾
function applyFilters() {
  const filtered = allPlayers.filter(p => {
    // 1. 關鍵字搜尋
    const matchKey = !currentFilter.keyword || 
      p.name.toLowerCase().includes(currentFilter.keyword) ||
      p.team.toLowerCase().includes(currentFilter.keyword) ||
      p.number.includes(currentFilter.keyword);

    // 2. 守位分類
    const matchPos = currentFilter.pos === 'ALL' || p.posCategory === currentFilter.pos;

    // 3. 投打習慣
    const matchBt = currentFilter.bt === 'ALL' || p.batsThrows.includes(currentFilter.bt);

    // 4. 首字索引
    const matchIndex = currentFilter.index === 'ALL' || p.initialIndex === currentFilter.index;

    return matchKey && matchPos && matchBt && matchIndex;
  });

  renderPlayers(filtered);
}

// 繪製表格
function renderPlayers(players) {
  const tbody = document.getElementById('playerTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (players.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:30px;">未找到符合條件的球員</td></tr>';
    return;
  }

  players.forEach(p => {
    const tr = document.createElement('tr');
    const honorsHtml = p.honors.filter(h => h.trim()).map(h => `<span class="honor-tag">${h.trim()}</span>`).join(' ');

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
