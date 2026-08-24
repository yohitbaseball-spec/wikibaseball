    /**
     * 賽事聯盟頁籤切換函式
     * @param {string} leagueKey - 聯盟 ID ('ibl', 'mlb', 'npb', 'kbo')
     * @param {HTMLElement} btnElement - 被點擊的按鈕
     */
    function switchLeague(leagueKey, btnElement) {
      // 1. 切換按鈕高亮 active 狀態
      const tabs = document.querySelectorAll('.league-tab');
      tabs.forEach(tab => tab.classList.remove('active'));
      btnElement.classList.add('active');

      // 2. 切換聯盟內容區塊顯示
      const contents = document.querySelectorAll('.league-content');
      contents.forEach(content => content.classList.remove('active'));

      const targetContent = document.getElementById(`league-${leagueKey}`);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    }
