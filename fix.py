import re
html = open('index.html', encoding='utf-8').read()
bad_code = '''    }        </div>
            ` : ''}
          </div>
        `;
      }).join('');
    }

    function setChampionPhoto(groupId, photoId) {
      showToast("Foto campeã da sequência atualizada!");
      renderDeduplicationGroups();
    }'''
html = html.replace(bad_code, '    }')
open('index.html', 'w', encoding='utf-8').write(html)
print('Fixed')
