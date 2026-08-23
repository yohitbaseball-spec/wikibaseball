let awardsData = {};
let decadesData = {};

// 國籍與資料夾路徑的對映表
const COUNTRY_FOLDER_MAP = {
  "TW": "../players/",
  "KR": "../korplayers/",
  "JP": "../jpplayers/",
  "US": "../usplayers/"
};

async function initAwardsData() {
  try {
    const response = await fetch('../json/gold_glove_data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    awardsData = data.awards || {};
    decadesData = data.decades || {};

    // 取得 JSON 裡的第一個年代 (例如 '2050s')
    const firstDecade = Object.keys(decadesData)[0] || '2050s';
    
    // 初始化選擇第一個年代，並傳入 true 代表要自動選最大年份
    selectDecade(firstDecade, true);
  } catch (error) {
    console.error('無法載入金手套資料:', error);
  }
}

function selectDecade(decade, autoPickLatest = false) {
  // 切換年代按鈕 active 狀態
  document.querySelectorAll('.decade-btn').forEach(b => {
    b.classList.toggle('active', b.innerText.trim() === decade);
  });

  const yearContainer = document.getElementById('yearButtons');
  yearContainer.innerHTML = '';
  
  const yrs = decadesData[decade] || [];
  yrs.forEach(yr => {
    const btn = document.createElement('button');
    btn.className = 'year-btn';
    btn.innerText = yr;
    btn.onclick = () => renderYear(yr);
    yearContainer.appendChild(btn);
  });

  if (yrs.length > 0) {
    if (autoPickLatest) {
      // 💡 尋找該年代中的最大年份 (數字由大到小排序後取第一個)
      const sortedYrs = [...yrs].sort((a, b) => Number(b) - Number(a));
      renderYear(sortedYrs[0]);
    } else {
      // 手動點選年代按鈕時，預設顯示第一個年份
      renderYear(yrs[0]);
    }
  }
}

function getPlayerLink(playerObj) {
  if (!playerObj || typeof playerObj !== 'object') {
    return playerObj || '-';
  }

  const folder = COUNTRY_FOLDER_MAP[playerObj.country] || "../players/";
  return `<a href="${folder}${playerObj.name}.html" class="player-link">${playerObj.name}</a>`;
}

function renderYear(year) {
  // 切換年份按鈕 active 狀態
  document.querySelectorAll('.year-btn').forEach(b => {
    b.classList.toggle('active', b.innerText.trim() === year);
  });

  const data = awardsData[year] || {};
  const positions = ['P','C','1B','2B','3B','SS','OF1','OF2','OF3','UTL'];

  // 更新球場 PIN 標籤
  positions.forEach(pos => {
    const pin = document.getElementById(`pin-${pos}`);
    if (pin) {
      const pData = data[pos];
      pin.innerHTML = pData ? getPlayerLink(pData) : '-';
    }
  });

  // 更新獲獎表格
  const tbody = document.getElementById('awardTableBody');
  tbody.innerHTML = '';
  positions.forEach(pos => {
    const displayPos = pos.startsWith('OF') ? 'OF' : pos;
    const pData = data[pos];
    const playerHtml = getPlayerLink(pData);
    const team = data.teams ? (data.teams[pos] || '-') : '-';
    
    tbody.innerHTML += `<tr>
      <td><b>${displayPos}</b></td>
      <td>${playerHtml}</td>
      <td>${team}</td>
    </tr>`;
  });
}

document.addEventListener('DOMContentLoaded', initAwardsData);
