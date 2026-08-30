import re

html = open('index.html', encoding='utf-8').read()

# 1. Flatten the design
# Remove all shadow classes
html = re.sub(r'\bshadow-\[.*?\]\b', '', html)
html = re.sub(r'\bshadow-[a-z]+-\d+/\d+\b', '', html)
html = re.sub(r'\bshadow-2xl\b', 'shadow-sm', html)
html = re.sub(r'\bshadow-lg\b', 'shadow-sm', html)
html = re.sub(r'\bshadow-xl\b', 'shadow-sm', html)

# Remove all gradient backgrounds
html = re.sub(r'\bbg-gradient-to-[a-z]{1,2}\b', '', html)
html = re.sub(r'\bfrom-[a-z]+-\d+\b', '', html)
html = re.sub(r'\bto-[a-z]+-\d+\b', '', html)

# If a div was using bg-gradient for a button, it now has NO background! 
# Let's add a solid background to them if they had from-blue-600.
# Actually, let's just replace the gradients with solid colors explicitly.
