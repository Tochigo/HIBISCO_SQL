(function () {
  const body = document.body;
  const themeToggleBtn = document.getElementById('themeToggle');
  const moonIcon = document.getElementById('moonIcon');
  const sunIcon = document.getElementById('sunIcon');

  function notifyThemeChange(isDark) {
    document.dispatchEvent(new CustomEvent('hibisco:theme-change', {
      detail: { isDark }
    }));
  }

  function applyTheme(isDark) {
    body.className = isDark ? 'dark' : 'light';
    if (moonIcon) moonIcon.classList.toggle('hidden', isDark);
    if (sunIcon) sunIcon.classList.toggle('hidden', !isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    notifyThemeChange(isDark);
  }

  const savedTheme = localStorage.getItem('theme');
  applyTheme(savedTheme ? savedTheme === 'dark' : true);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const nextIsDark = !body.classList.contains('dark');
      applyTheme(nextIsDark);
    });
  }
})();
