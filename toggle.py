import re

html = open('index.html', encoding='utf-8').read()

old_dom = '''    window.addEventListener('DOMContentLoaded', async () => {
      const dateInp = document.getElementById('newServiceDate');'''

new_dom = '''    function toggleTheme() {
      const htmlEl = document.documentElement;
      const isDark = htmlEl.classList.contains('dark');
      if (isDark) {
        htmlEl.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        document.getElementById('themeIcon').className = 'fa-solid fa-sun text-amber-500';
        document.getElementById('themeText').textContent = 'Modo Claro';
      } else {
        htmlEl.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        document.getElementById('themeIcon').className = 'fa-solid fa-moon text-blue-400';
        document.getElementById('themeText').textContent = 'Modo Escuro';
      }
    }

    function initTheme() {
      const storedTheme = localStorage.getItem('theme');
      const htmlEl = document.documentElement;
      if (storedTheme === 'light') {
        htmlEl.classList.remove('dark');
        const ti = document.getElementById('themeIcon');
        const tt = document.getElementById('themeText');
        if (ti) ti.className = 'fa-solid fa-sun text-amber-500';
        if (tt) tt.textContent = 'Modo Claro';
      }
    }

    window.addEventListener('DOMContentLoaded', async () => {
      initTheme();
      const dateInp = document.getElementById('newServiceDate');'''

html = html.replace(old_dom, new_dom)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done toggle logic')
