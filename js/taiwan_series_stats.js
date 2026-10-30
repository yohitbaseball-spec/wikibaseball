// 20 支球隊的數據資料庫
const teamStatsData = [
  { name: "新世紀恐龍隊", url: "../teams/新世紀恐龍隊.html", titles: 0, apps: 1, games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2047年", lastApp: "2048年", former: "—", note: "—" },
  { name: "北鐵狼隊", url: "../teams/北鐵狼隊.html", titles: 3, apps: "-", games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2050年", lastApp: "2050年", former: "—", note: "—" },
  { name: "微秒彗星隊", url: "../teams/微秒彗星隊.html", titles: "-", apps: "-", games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2049年", lastApp: "2051年", former: "-", note: "—" },
  { name: "NX星航者隊", url: "../teams/NX星航者隊.html", titles: "-", apps: "-", games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2044年", lastApp: "-", former: "-", note: "—" },
  { name: "高雄未來之鷹隊", url: "../teams/高雄未來之鷹隊.html", titles: "-", apps: "-", games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2046年", lastApp: "-", former: "-", note: "—" },
  { name: "阿里山小火車隊", url: "../teams/阿里山小火車隊.html", titles: 1, apps: "-", games: "-", wins: "-", losses: "-", ties: "-", winRate: "-", lastTitle: "2051年", lastApp: "2051年", former: "-", note: "—" },
  { name: "奇醫海燕隊", url: "../teams/奇醫海燕隊.html", titles: 1, apps: 3, games: 15, wins: 6, losses: 9, ties: 0, winRate: ".400", lastTitle: "2052年", lastApp: "2052年", former: "-", note: "—" },
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
