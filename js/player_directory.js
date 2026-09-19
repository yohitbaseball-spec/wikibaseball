const GITHUB_USER = 'yohitbaseball-spec';
const REPO_NAME = 'wikibaseball';
const PLAYER_FOLDERS = ['players', 'jpplayers', 'korplayers', 'usaplayers'];

let allPlayers = [];
let currentFilter = {
  keyword: '',
  pos: 'ALL',
  bt: 'ALL',
  index: 'ALL'
};

document.addEventListener('DOMContentLoaded', async () => {
  try {
    // 改為只發送 1 次請求讀取 data/players.json
    const res = await fetch('../data/players.json');
    if (!res.ok) {
      throw new Error(`無法讀取 players.json (HTTP Status: ${res.status})`);
    }

    const rawData = await res.json();

    // 自動補充計算注音首字與守備分類
    allPlayers = rawData.map(p => ({
      ...p,
      initialIndex: getFirstCharIndex(p.name),
      posCategory: getPosCategory(p.position || '-'),
      honors: Array.isArray(p.honors) ? p.honors : []
    }));

    // 渲染畫面
    buildIndexBar(allPlayers);
    initFilterEvents();
    applyFilters();

  } catch (error) {
    console.error('載入失敗：', error);
    const tbody = document.getElementById('playerTableBody');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#e74c3c; padding:30px;">數據載入失敗，請確認 data/players.json 檔案已成功建立。</td></tr>';
    }
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

// 精確判斷姓名首字注音 (修正「鄭」被誤判問題)
function getFirstCharIndex(name) {
  if (!name || name.length === 0) return '其他';
  const char = name.charAt(0);
  
  if (/[a-zA-Z]/.test(char)) return char.toUpperCase();
  
  // 精密修正後的注音首字邊界對照表
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

  // 特殊姓氏/常見字校正表 (解決 Unicode/LocaleCompare 邊界問題)
  const specialMap = {
    '鄭': 'ㄓ', '張': 'ㄓ', '趙': 'ㄓ', '周': 'ㄓ', '朱': 'ㄓ', '莊': 'ㄓ', '鍾': 'ㄓ',
    '許': 'ㄒ', '謝': 'ㄒ', '席': 'ㄒ', '徐': 'ㄒ', '夏': 'ㄒ',
    '陳': 'ㄔ', '程': 'ㄔ', '蔡': 'ㄘ', '曹': 'ㄘ', '崔': 'ㄘ',
    '沈': 'ㄕ', '施': 'ㄕ', '孫': 'ㄙ', '蘇': 'ㄙ', '宋': 'ㄙ',
    '曾': 'ㄗ', '邱': 'ㄑ', '余': 'ㄩ', '黃': 'ㄏ'
  };

  if (specialMap[char]) {
    return specialMap[char];
  }

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
  
  // 標準注音順序
  const zhuyinOrder = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩABCDEFGHIJKLMNOPQRSTUVWXYZ其他";
  
  const sortedIndexes = Array.from(indexSet).sort((a, b) => {
    const idxA = zhuyinOrder.indexOf(a);
    const idxB = zhuyinOrder.indexOf(b);
    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
    return a.localeCompare(b, 'zh-TW');
  });
  
  const bar = document.getElementById('alphaIndexBar');
  // 保留「全部」按鈕
  bar.innerHTML = '<button class="filter-btn active" data-index="ALL">全部</button>';
  
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
  document.getElementById('searchInput')?.addEventListener('input', (e) => {
    currentFilter.keyword = e.target.value.toLowerCase();
    applyFilters();
  });

  const bindButtonGroup = (containerId, key) => {
    document.getElementById(containerId)?.addEventListener('click', (e) => {
      if (e.target.classList.contains('filter-btn')) {
        document.querySelectorAll(`#${containerId} .filter-btn`).forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter[key] = e.target.dataset[key] || e.target.getAttribute(`data-${key}`);
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
    const matchKey = !currentFilter.keyword || 
      p.name.toLowerCase().includes(currentFilter.keyword) ||
      p.team.toLowerCase().includes(currentFilter.keyword) ||
      p.number.includes(currentFilter.keyword) ||
      p.nationality.includes(currentFilter.keyword);

    const matchPos = currentFilter.pos === 'ALL' || p.posCategory === currentFilter.pos;
    const matchBt = currentFilter.bt === 'ALL' || p.batsThrows.includes(currentFilter.bt);
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
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted, #888); padding:30px;">未找到符合條件的球員</td></tr>';
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
