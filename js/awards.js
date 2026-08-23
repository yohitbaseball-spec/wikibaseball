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
    // 💡 從 js/ 跳出上一層 (../) 後，進入 .json/ 資料夾讀取 JSON 檔
    const response = await fetch('../.json/gold_glove_data.json');
    const data = await response.json();
    
    awardsData = data.awards || {};
    decadesData = data.decades || {};

    const firstDecade = Object.keys(decadesData)[0] || '2020s';
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
  document.querySelectorAll('.decade-btn').forEach(b => {
    b.classList.toggle('active', b.innerText === decade);
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

  if (yrs.length > 0) renderYear(yrs[0]);
}

function renderYear(year) {
  document.querySelectorAll('.year-btn').forEach(b => {
    b.classList.toggle('active', b.innerText === year);
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
