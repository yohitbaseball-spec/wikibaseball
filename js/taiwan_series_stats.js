// 20 支球隊的數據資料庫
const teamStatsData = [
  { name: "新世紀恐龍隊", url: "../teams/新世紀恐龍隊.html", titles: 0, apps: 1, games: -, wins: -, losses: -, ties: -, winRate: "-", lastTitle: "2047年", lastApp: "2050年", former: "—", note: "—" },
  { name: "北鐵狼隊", url: "../teams/北鐵狼隊.html", titles: 3, apps: -, games: -, wins: -, losses: -, ties: -, winRate: "-", lastTitle: "2050年", lastApp: "2051年", former: "—", note: "—" },
  { name: "微秒彗星隊", url: "../teams/微秒彗星隊.html", titles: 0, apps: 2, games: 13, wins: 5, losses: 8, ties: 0, winRate: ".385", lastTitle: "2049年", lastApp: "2052年", former: "和信鯨隊", note: "—" },
  { name: "台北飛鷹隊", url: "", titles: 0, apps: 1, games: 6, wins: 2, losses: 4, ties: 0, winRate: ".333", lastTitle: "—", lastApp: "2045年", former: "—", note: "聯盟初期解散球隊", defunct: true }
];

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('teamStatsBody');
  if (!tbody) return;

  tbody.innerHTML = teamStatsData.map(t => {
    const isDefunct = t.defunct ? 'class="defunct-row"' : '';
    const nameCell = t.url ? `<a href="${t.url}">${t.name}</a>` : t.name;

    return `
      <tr ${isDefunct}>
        <td>${nameCell}</td>
        <td>${t.titles}</td>
        <td>${t.apps}</td>
        <td>${t.games}</td>
        <td>${t.wins}</td>
        <td>${t.losses}</td>
        <td>${t.ties}</td>
        <td><strong>${t.winRate}</strong></td>
        <td>${t.lastTitle}</td>
        <td>${t.lastApp}</td>
        <td>${t.former}</td>
        <td>${t.note}</td>
      </tr>
    `;
  }).join('');
});
