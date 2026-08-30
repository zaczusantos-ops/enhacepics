import re

html = open('index.html', encoding='utf-8').read()

replacements = {
    'bg-gradient-to-tr from-blue-600 to-indigo-600': 'bg-blue-600',
    'bg-gradient-to-r from-blue-600 to-indigo-600': 'bg-blue-600',
    'hover:from-blue-500 hover:to-indigo-500': 'hover:bg-blue-500',
    'bg-gradient-to-tr from-emerald-600 to-teal-600': 'bg-emerald-600',
    'bg-gradient-to-r from-emerald-600 to-teal-600': 'bg-emerald-600',
    'hover:from-emerald-500 hover:to-teal-500': 'hover:bg-emerald-500',
    'bg-gradient-to-b from-church-900 to-church-950': 'bg-church-900',
    'shadow-lg shadow-blue-600/30': '',
    'shadow-xl shadow-blue-600/30': '',
    'shadow-lg shadow-emerald-600/30': '',
    'shadow-lg shadow-emerald-600/25': '',
    'shadow-2xl': 'shadow-sm',
    'shadow-xl': 'shadow-sm',
    'shadow-lg': 'shadow-sm',
    'shadow-md': 'shadow-sm',
    '<div class="absolute -top-16 -right-16 w-36 h-36 bg-blue-500/20 blur-3xl pointer-events-none"></div>': '',
    '<div class="absolute -bottom-16 -left-16 w-36 h-36 bg-emerald-500/20 blur-3xl pointer-events-none"></div>': '',
    '<div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-500/10 blur-3xl pointer-events-none"></div>': ''
}

for old, new in replacements.items():
    html = html.replace(old, new)

# Cleanup any stray 'shadow-blue-600/30' etc.
html = re.sub(r'\bshadow-\w+-\d+/\d+\b', '', html)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done flattening')
