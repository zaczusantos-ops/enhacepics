from html.parser import HTMLParser
class P(HTMLParser):
  def __init__(self):
    super().__init__()
    self.stack = []
  def handle_starttag(self, tag, attrs):
    if tag not in ['input','img','br','hr','link','meta','source']: self.stack.append(tag)
  def handle_endtag(self, tag):
    if tag in ['input','img','br','hr','link','meta','source']: return
    if not self.stack: print(f'Unmatched closing {tag}'); return
    if self.stack[-1] == tag: self.stack.pop()
    else: print(f'Mismatched tag: expected {self.stack[-1]}, got {tag}'); self.stack.pop()
P().feed(open('index.html', encoding='utf-8', errors='ignore').read())
print('Done')
