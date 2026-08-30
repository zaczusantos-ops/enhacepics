import re

html = open('index.html', encoding='utf-8').read()

old_config = '''  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            church: {
              950: '#07090E',
              900: '#0E131F',
              850: '#151C2C',
              800: '#1D263B',
              750: '#232E47',
              700: '#2A3753',
              600: '#3D4F75',
              accent: '#3B82F6',
              gold: '#F59E0B',
            }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
          }
        }
      }
    }
  </script>
  <style>
    * { -webkit-tap-highlight-color: transparent; }
    body { background-color: #07090E; color: #F1F5F9; font-family: 'Inter', sans-serif; }'''

new_config = '''  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            church: {
              950: 'var(--c-950)',
              900: 'var(--c-900)',
              850: 'var(--c-850)',
              800: 'var(--c-800)',
              750: 'var(--c-750)',
              700: 'var(--c-700)',
              600: 'var(--c-600)',
              accent: '#3B82F6',
              gold: '#F59E0B',
            }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
          }
        }
      }
    }
  </script>
  <style>
    :root {
      --c-950: #ffffff;
      --c-900: #f8fafc;
      --c-850: #f1f5f9;
      --c-800: #e2e8f0;
      --c-750: #cbd5e1;
      --c-700: #94a3b8;
      --c-600: #64748b;
      --t-main: #0f172a;
      --t-muted: #334155;
      --t-subtle: #64748b;
    }
    
    .dark {
      --c-950: #07090E;
      --c-900: #0E131F;
      --c-850: #151C2C;
      --c-800: #1D263B;
      --c-750: #232E47;
      --c-700: #2A3753;
      --c-600: #3D4F75;
      --t-main: #ffffff;
      --t-muted: #cbd5e1;
      --t-subtle: #94a3b8;
    }

    * { -webkit-tap-highlight-color: transparent; }
    body { background-color: var(--c-950); color: var(--t-main); font-family: 'Inter', sans-serif; transition: background-color 0.2s; }
    
    .text-white { color: var(--t-main) !important; }
    .text-slate-300 { color: var(--t-muted) !important; }
    .text-slate-400 { color: var(--t-subtle) !important; }
    
    /* Preserve solid colors for primary buttons */
    .bg-blue-600, .bg-emerald-600, .bg-amber-600, .bg-purple-600, .bg-red-600, 
    .bg-indigo-600, .bg-teal-600, .bg-rose-600 {
      color: #ffffff !important;
    }
    .bg-blue-600 .text-slate-300, .bg-blue-600 .text-slate-400,
    .bg-emerald-600 .text-slate-300, .bg-emerald-600 .text-slate-400,
    .bg-amber-600 .text-slate-300, .bg-amber-600 .text-slate-400,
    .bg-purple-600 .text-slate-300, .bg-purple-600 .text-slate-400 {
       color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Ensure inputs have correct text */
    input, select, textarea { color: var(--t-main) !important; }'''

html = html.replace(old_config, new_config)

# Add theme toggle button to sidebar
old_sidebar_end = '''<div class="mt-2.5 text-center flex justify-center opacity-70">
        <span class="text-[9px] text-slate-500 font-mono tracking-widest uppercase border border-slate-700/50 bg-church-900/50 px-2 py-0.5 rounded-full">v2.5.0 (skip-studio)</span>
      </div>'''

new_sidebar_end = '''<div class="mt-2 text-center flex justify-center">
        <button onclick="toggleTheme()" class="px-3 py-1.5 rounded-lg border border-church-800 bg-church-900 hover:bg-church-850 text-slate-400 text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all">
          <i class="fa-solid fa-moon" id="themeIcon"></i> <span id="themeText">Modo Escuro</span>
        </button>
      </div>

      <div class="mt-2 text-center flex justify-center opacity-70">
        <span class="text-[9px] text-slate-500 font-mono tracking-widest uppercase border border-slate-700/50 bg-church-900/50 px-2 py-0.5 rounded-full">v2.5.1 (minimal-light)</span>
      </div>'''
html = html.replace(old_sidebar_end, new_sidebar_end)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done configuring theme')
