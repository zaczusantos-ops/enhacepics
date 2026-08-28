import re

html = open('index.html', encoding='utf-8').read()

new_apply = '''    function applyPresetObj(presetId) {
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

html = re.sub(r'    function applyPresetObj\(presetId\) \{[\s\S]*?showToast\(Preset "\$\{p\.name\}" aplicado!\);\n    \}', new_apply, html)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
