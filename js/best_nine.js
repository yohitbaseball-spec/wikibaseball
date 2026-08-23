let bestNineData = {};
let decadesData = {};
let currentDecade = '';
let currentYear = '';
let currentTeam = '1st';

const COUNTRY_FOLDER_MAP = {
  "TW": "../players/",
  "KR": "../korplayers/",
  "JP": "../jpplayers/",
  "US": "../usplayers/"
};

async function initBestNineData() {
  try {
    const response = await fetch('../json/best_nine_data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    bestNineData = data.awards || {};
    decadesData = data.decades || {};

    // 渲染年代膠囊按鈕
    renderDecadePills();

    // 預設選擇第一個年代 (例如 2050s) 並自動開最大年份
    const firstDecade = Object.keys(decadesData)[0] || '2050s';
    selectDecade(firstDecade, true);
  } catch (error) {
    console.error('無法載入年度最佳陣容資料:', error);
  }
}

function getPlayerLink(playerObj) {
  if (!playerObj || typeof playerObj !== 'object') {
    return playerObj || '-';
  }

  const folder = COUNTRY_FOLDER_MAP[playerObj.country] || "../players/";
  return `<a href="${folder}${playerObj.name}.html" class="player-link">${playerObj.name}</a>`;
}

function renderDecadePills() {
  const container = document.querySelector('.decade-bar');
  if (!container) return;
  container.innerHTML = '';

  Object.keys(decadesData).forEach(decade => {
    const btn = document.createElement('button');
    btn.className = 'decade-pill';
    btn.innerText = decade;
    btn.onclick = () => selectDecade(decade, false);
    container.appendChild(btn);
  });
}

function selectDecade(decade, autoPickLatest = false) {
  currentDecade = decade;

  document.querySelectorAll('.decade-pill').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.trim() === decade);
  });

  const yearContainer = document.getElementById('yearButtons');
  const dropdown = document.getElementById('yearSelectDropdown');
  yearContainer.innerHTML = '';
  dropdown.innerHTML = '';

  const yrs = decadesData[decade] || [];

  yrs.forEach(yr => {
    const btn = document.createElement('button');
    btn.className = 'year-btn';
    btn.innerText = yr;
    btn.onclick = () => selectYear(yr);
    yearContainer.appendChild(btn);

    const opt = document.createElement('option');
    opt.value = yr;
    opt.innerText = `${yr} 年`;
    dropdown.appendChild(opt);
  });

  if (yrs.length > 0) {
    if (autoPickLatest) {
      // 💡 數字降冪排序，自動選擇最大年份 (例如 2054)
      const sortedYrs = [...yrs].sort((a, b) => Number(b) - Number(a));
      selectYear(sortedYrs[0]);
    } else {
      selectYear(yrs[0]);
    }
  }
}

function selectYear(year) {
  currentYear = year;

  document.getElementById('selectedYearDisplay').innerText = `${year} 年`;
  
  const dropdown = document.getElementById('yearSelectDropdown');
  if (dropdown) dropdown.value = year;

  document.querySelectorAll('.year-btn').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.trim() === year);
  });

  updateView();
}

function onYearDropdownChange(val) {
  selectYear(val);
}

function switchTeam(team) {
  currentTeam = team;
  document.getElementById('btnTeam1').classList.toggle('active', team === '1st');
  document.getElementById('btnTeam2').classList.toggle('active', team === '2nd');
  document.getElementById('selectedTeamDisplay').innerText = team === '1st' ? '第一隊獲獎名單' : '第二隊獲獎名單';
  updateView();
}

function updateView() {
  const yearData = bestNineData[currentYear] || {};
  const teamData = yearData[currentTeam] || {};
  const positions = ['P','C','1B','2B','3B','SS','OF1','OF2','OF3','DH'];

  // 1. 更新球場 PIN 點
  positions.forEach(pos => {
    const pin = document.getElementById(`pin-${pos}`);
    if (pin) {
      const pData = teamData[pos];
      pin.innerHTML = pData ? getPlayerLink(pData) : '-';
    }
  });

  // 2. 更新表格數據
  const tbody = document.getElementById('awardTableBody');
  tbody.innerHTML = '';

  positions.forEach(pos => {
    const displayPos = pos.startsWith('OF') ? 'OF' : pos;
    const pData = teamData[pos];
    const playerHtml = getPlayerLink(pData);
    const team = (teamData.teams && teamData.teams[pos]) ? teamData.teams[pos] : '-';

    tbody.innerHTML += `<tr>
      <td><b>${displayPos}</b></td>
      <td>${playerHtml}</td>
      <td>${team}</td>
    </tr>`;
  });
}

document.addEventListener('DOMContentLoaded', initBestNineData);
