import re

html = open('index.html', encoding='utf-8').read()

# 1. Add Checkbox to Create Modal
old_date = '''<input type="date" id="newServiceDate" required class="w-full px-3.5 py-2 rounded-xl bg-church-950 border border-church-800 text-white text-xs focus:outline-none focus:border-blue-500">
        </div>'''
new_date = '''<input type="date" id="newServiceDate" required class="w-full px-3.5 py-2 rounded-xl bg-church-950 border border-church-800 text-white text-xs focus:outline-none focus:border-blue-500">
        </div>

        <div class="mt-2">
          <label class="flex items-center gap-2.5 cursor-pointer">
            <input type="checkbox" id="newServiceSkipStudio" class="w-4 h-4 rounded text-blue-600 bg-church-950 border-church-800 focus:ring-blue-500 cursor-pointer">
            <span class="text-xs text-slate-300 font-medium select-none">Ignorar Edi&ccedil;&atilde;o (Usar apenas IA para Escolha de Fotos)</span>
          </label>
        </div>'''
html = html.replace(old_date, new_date)


# 2. Add flag to 
ewService in handleCreateServiceSubmit
old_new_service = '''presetName: activeTeam && activeTeam.presets && activeTeam.presets[0] ? activeTeam.presets[0].name : 'Luz Quente Natural',
        items: [],
        createdAt: new Date().toISOString()
      };'''
new_new_service = '''presetName: activeTeam && activeTeam.presets && activeTeam.presets[0] ? activeTeam.presets[0].name : 'Luz Quente Natural',
        items: [],
        createdAt: new Date().toISOString(),
        skipStudio: document.getElementById('newServiceSkipStudio') ? document.getElementById('newServiceSkipStudio').checked : false
      };'''
html = html.replace(old_new_service, new_new_service)


# 3. Change setFunnelStep(3) logic to skip studio if flag is set
old_step_3 = '''// Enviar para Fase 3 (Studio) apenas as selecionadas na Fase 2
        if (activeService && activeService.items) {
          activeService.items = activeService.items.filter(i => i.isTop20 !== false);
          dbSaveService(activeService);
          openServiceInStudio(activeService.id);
        } else {
          switchMainView('studio');
        }'''
new_step_3 = '''// Enviar para Fase 3 (Studio) apenas as selecionadas na Fase 2
        if (activeService && activeService.items) {
          activeService.items = activeService.items.filter(i => i.isTop20 !== false);
          dbSaveService(activeService);
          
          if (activeService.skipStudio) {
            showToast("Culto finalizado! Edicao pulada conforme configuracao.");
            switchMainView('services');
          } else {
            openServiceInStudio(activeService.id);
          }
        } else {
          if (activeService && activeService.skipStudio) switchMainView('services');
          else switchMainView('studio');
        }'''
html = html.replace(old_step_3, new_step_3)


# 4. Hide "Fase 3" tab in Funnel UI if skipStudio is true
old_b3 = '''b3.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all";
      });'''
new_b3 = '''b3.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all";
      });
      
      if (activeService && activeService.skipStudio) {
        if (b3) b3.style.display = 'none'; // Esconder tab do estudio
      } else {
        if (b3) b3.style.display = 'flex';
      }'''
html = html.replace(old_b3, new_b3)

# 5. Rename "Aprovar Galeria (Ir para Fase 3)" button if skipStudio is true.
old_s2 = '''s3.style.display = 'none'; s3.classList.add('hidden');
        b2.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold flex items-center gap-1.5 transition-all";
        renderTop20Grid();'''
new_s2 = '''s3.style.display = 'none'; s3.classList.add('hidden');
        b2.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold flex items-center gap-1.5 transition-all";
        
        // Mudar texto do botao final
        const btnNext = document.querySelector('#funnelStage2 button[onclick="setFunnelStep(3)"]');
        if (btnNext) {
          if (activeService && activeService.skipStudio) {
            btnNext.innerHTML = <i class="fa-solid fa-check"></i> Finalizar Galeria (Salvar);
            btnNext.className = "px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/30 cursor-pointer";
          } else {
            btnNext.innerHTML = Aprovar Galeria (Ir para Fase 3) <i class="fa-solid fa-arrow-right"></i>;
            btnNext.className = "px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/30 cursor-pointer";
          }
        }
        
        renderTop20Grid();'''
html = html.replace(old_s2, new_s2)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
