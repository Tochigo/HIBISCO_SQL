(function () {
  const toggleBtn = document.getElementById('toggle-answer');
  const answerPanel = document.getElementById('answer-panel');

  if (!toggleBtn || !answerPanel) return;

  toggleBtn.addEventListener('click', function () {
    const isVisible = answerPanel.classList.toggle('is-visible');
    toggleBtn.textContent = isVisible ? 'Ocultar respuesta' : 'Mostrar respuesta';
  });
})();
