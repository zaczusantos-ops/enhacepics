import re

html = open('index.html', encoding='utf-8').read()

# 1. Add f_stop and focal_point to applyCurrentManualParams
apply_params_old = '''vignette: parseFloat(document.getElementById('param_vignette').value)
      };'''
apply_params_new = '''vignette: parseFloat(document.getElementById('param_vignette').value),
        f_stop_simulation: currentFStop,
        focal_point_x: focalPoint.x,
        focal_point_y: focalPoint.y
      };'''
html = html.replace(apply_params_old, apply_params_new)


# 2. Add Bokeh Logic to processImageClientSideFast
end_fast_old = '''fastCtx.putImageData(imgData, 0, 0);

      return {
        base64: fastCanvas.toDataURL('image/jpeg', isFullResolution ? 0.94 : 0.88),'''

end_fast_new = '''fastCtx.putImageData(imgData, 0, 0);

      // --- 3. HARDWARE-ACCELERATED BOKEH (DEPTH OF FIELD) ---
      const fstop = params.f_stop_simulation !== undefined ? params.f_stop_simulation : (typeof currentFStop !== 'undefined' ? currentFStop : 8.0);
      if (fstop < 8.0) {
        const maxBlur = (8.0 - fstop) * 1.5;
        const fpx = (params.focal_point_x !== undefined ? params.focal_point_x : (typeof focalPoint !== 'undefined' ? focalPoint.x : 0.5)) * targetW;
        const fpy = (params.focal_point_y !== undefined ? params.focal_point_y : (typeof focalPoint !== 'undefined' ? focalPoint.y : 0.4)) * targetH;

        // Blur layer
        const bCvs = document.createElement('canvas');
        bCvs.width = targetW; bCvs.height = targetH;
        const bCtx = bCvs.getContext('2d');
        bCtx.filter = lur(px);
        bCtx.drawImage(fastCanvas, 0, 0);

        // Alpha Mask layer (Radial Gradient)
        const mCvs = document.createElement('canvas');
        mCvs.width = targetW; mCvs.height = targetH;
        const mCtx = mCvs.getContext('2d');
        
        // Depth radius mapping based on f-stop
        const r1 = Math.min(targetW, targetH) * 0.15 * (fstop / 2.8);
        const r2 = Math.min(targetW, targetH) * 0.6;
        
        const grad = mCtx.createRadialGradient(fpx, fpy, r1, fpx, fpy, r2);
        grad.addColorStop(0, 'rgba(0,0,0,0)'); // Transparent focus area
        grad.addColorStop(1, 'rgba(0,0,0,1)'); // Opaque blurred edges
        mCtx.fillStyle = grad;
        mCtx.fillRect(0, 0, targetW, targetH);

        // Cut mask into blur layer
        bCtx.globalCompositeOperation = 'destination-in';
        bCtx.drawImage(mCvs, 0, 0);

        // Stamp blurred edges over the sharp original
        fastCtx.drawImage(bCvs, 0, 0);
      }

      return {
        base64: fastCanvas.toDataURL('image/jpeg', isFullResolution ? 0.94 : 0.88),'''

html = html.replace(end_fast_old, end_fast_new)

# 3. Fix the HTML bug where we click to update Focal Point but it doesn't trigger a re-render!
# Let's check document.getElementById('imgAfter').addEventListener('click', function(event) {
html = re.sub(r'(resetFocalCenter\(\);\n.*?updateFocalReticleUI\(\);\n)', r'\g<1>      applyCurrentManualParams();\n', html)
html = re.sub(r'(updateFocalReticleUI\(\);\n      \}\n    \}\);)', r'updateFocalReticleUI();\n        applyCurrentManualParams();\n      }\n    });', html)

# Also fix setFStop so it re-renders
html = html.replace('''document.getElementById('fStopTag').textContent = / Bokeh;\n    }''', '''document.getElementById('fStopTag').textContent = / Bokeh;\n      applyCurrentManualParams();\n    }''')


open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
