import re

html = open('index.html', encoding='utf-8').read()

# 1. Flatten the design (Remove shadows, gradients, and glowing orbs)
html = re.sub(r'\bshadow-lg\b', 'shadow-sm', html)
html = re.sub(r'\bshadow-xl\b', 'shadow-sm', html)
html = re.sub(r'\bshadow-2xl\b', 'shadow-md', html)
html = re.sub(r'\bshadow-\[.*?\]\b', '', html) # Remove custom drop shadows
html = re.sub(r'\bshadow-\w+-\d+/\d+\b', '', html) # Remove colored shadows like shadow-blue-600/30
html = re.sub(r'\bbg-gradient-to-\w+\b', '', html) # Remove gradients
html = re.sub(r'\bfrom-\w+-\d+\b', '', html)
html = re.sub(r'\bto-\w+-\d+\b', '', html)
# Remove the decorative glowing blurred orbs
html = re.sub(r'<div class="absolute[^>]*?blur-3xl[^>]*?></div>', '', html)

# 2. Convert to Light/Dark Mode via CSS variables inside Tailwind config
# Wait! Instead of changing HTML classes which is risky, let's redefine the Tailwind config!
# We can tell Tailwind that church-950 uses a CSS variable!
