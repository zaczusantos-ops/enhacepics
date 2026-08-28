html = open('index.html', encoding='utf-8').read()

old_func = '''    function applyPresetObj(presetId) {
      const p = (activeTeam.presets || []).find(x => x.id === presetId);
      if (!p || !activeItem) return;
      
      activeItem.currentParams = { ...p.params };
      const par = p.params;

      const setVal = (id, val, suffix = '') => {
        const el = document.getElementById(param_);
        const valEl = document.getElementById(al_);
        if (el && val !== undefined) {
          el.value = val;
          if (valEl) valEl.textContent = ${val};
        }
      };

      setVal('exposure', par.exposure_compensation, '');
      setVal('kelvin', par.temperature_kelvin, 'K');
      setVal('tint', par.tint, '');
      setVal('contrast', par.contrast, 'x');
      setVal('highlights', par.highlights !== undefined ? Math.round(par.highlights*100) : 0, '%');
      setVal('shadows', par.shadows !== undefined ? Math.round(par.shadows*100) : 0, '%');
      setVal('whites', par.whites !== undefined ? Math.round(par.whites*100) : 0, '%');
      setVal('blacks', par.blacks !== undefined ? Math.round(par.blacks*100) : 0, '%');
      setVal('saturation', par.saturation !== undefined ? Math.round(par.saturation*100) : 100, '%');
      setVal('vibrance', par.vibrance !== undefined ? Math.round(par.vibrance*100) : 100, '%');
      setVal('clarity', par.clarity !== undefined ? Math.round(par.clarity*100) : 0, '%');
      setVal('dehaze', par.dehaze !== undefined ? Math.round(par.dehaze*100) : 0, '%');
      setVal('vignette', par.vignette !== undefined ? Math.round(par.vignette*100) : 0, '%');

      applyCurrentManualParams();
      showToast(Preset "" aplicado!);
    }'''

new_func = '''    function applyPresetObj(presetId) {
      const p = (activeTeam.presets || []).find(x => x.id === presetId);
      if (!p || !activeItem) return;
      
      activeItem.currentParams = { ...p.params };
      const par = p.params;

      const setVal = (id, internalVal, displayVal) => {
        const el = document.getElementById(param_);
        const valEl = document.getElementById(al_);
        if (el && internalVal !== undefined) {
          el.value = internalVal;
          if (valEl) valEl.textContent = displayVal;
        }
      };

      setVal('exposure', par.exposure_compensation, par.exposure_compensation);
      setVal('kelvin', par.temperature_kelvin, par.temperature_kelvin + 'K');
      setVal('tint', par.tint, par.tint);
      setVal('contrast', par.contrast, par.contrast + 'x');
      setVal('highlights', par.highlights, Math.round(par.highlights*100) + '%');
      setVal('shadows', par.shadows, Math.round(par.shadows*100) + '%');
      setVal('whites', par.whites, Math.round(par.whites*100) + '%');
      setVal('blacks', par.blacks, Math.round(par.blacks*100) + '%');
      setVal('saturation', par.saturation, Math.round(par.saturation*100) + '%');
      if (par.vibrance !== undefined) setVal('vibrance', par.vibrance, Math.round(par.vibrance*100) + '%');
      setVal('clarity', par.clarity, Math.round(par.clarity*100) + '%');
      setVal('dehaze', par.dehaze, Math.round(par.dehaze*100) + '%');
      setVal('vignette', par.vignette, Math.round(par.vignette*100) + '%');

      applyCurrentManualParams();
      showToast(Preset "" aplicado!);
    }'''

import re
# escape variables for replace
# Actually regex is safer if we just match between function applyPresetObj(presetId) { and }
pattern = r'    function applyPresetObj\(presetId\) \{[\s\S]*?showToast\(Preset "\$\{p\.name\}" aplicado!\);\n    \}'
if re.search(pattern, html):
    html = re.sub(pattern, new_func.replace('\\', '\\\\'), html)
else:
    print("Pattern not found! Trying manual substring replacement...")
    start_idx = html.find('function applyPresetObj(presetId) {')
    end_idx = html.find('}', html.find('showToast(Preset "" aplicado!);'))
    if start_idx != -1 and end_idx != -1:
        html = html[:start_idx-4] + new_func + html[end_idx+1:]
        
open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
