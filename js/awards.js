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
    // 💡 嘗試抓取 JSON，如果抓不到請檢查控制台 (F12) 報錯
    const response = await fetch('../.json/gold_glove_data.json');
    if (!response.ok) {
      throw new Error(`找不到 JSON 檔案 (Status: ${response.status})`);
    }

    const data = await response.json();
    
    awardsData = data.awards || {};
    decadesData = data.decades || {};

    // 預設選擇第一個年代（即 2050s）
    const firstDecade = Object.keys(decadesData)[0] || '2050s';
    selectDecade(firstDecade);
  } catch (error) {
    console.error('無法載入金手套資料:', error);
  }
}

function getPlayerLink(playerObj) {
  if (!playerObj || typeof playerObj !== 'object') {
    return playerObj || '-';
  }

  const folder = COUNTRY_FOLDER_MAP[playerObj.country] || "../players/";
  return `<a href="${folder}${playerObj.name}.html" class="player-link">${playerObj.name}</a>`;
}

function selectDecade(decade) {
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

  // 自動渲染該年代的第一個年份
  if (yrs.length > 0) renderYear(yrs[0]);
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
