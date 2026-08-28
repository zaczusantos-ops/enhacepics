

    // Global Application State
    let churchServices = [];
    let activeService = null;
    let activeTeam = { 
      id: 'team_default', 
      name: 'Mídia Principal', 
      members: [],
      presets: []
    };
    let queue = [];
    let activeItem = null;
    let currentMainView = 'services'; // 'services', 'funnel', 'studio', 'team_area'
    let currentFunnelStep = 1; // 1: Dedup, 2: Top20, 3: Crop
    let isSidebarCollapsed = false;
    let smartCropMode = '4:5'; // '4:5', '1:1', 'off'

    let viewerMode = 'slider';
    let sliderPercent = 50;
    let isDragging = false;
    let currentTab = 1;
    let focalPoint = { x: 0.50, y: 0.40 };
    let currentFStop = 2.8;
    let currentUser = null;
    let currentAuthTab = 'login'; // 'login' or 'register'
    let pendingModalFiles = [];

    // Fast canvas cache for 60fps
    const fastCanvas = document.createElement('canvas');
    const fastCtx = fastCanvas.getContext('2d', { willReadFrequently: true });
    let animFrameRequested = false;

    const DEFAULT_TEAM_PRESETS = [
  {
    id: "warm_worship",
    name: "Warm Worship (Adoração Acolhedora)",
    category: "Louvor",
    icon: "fa-sun text-amber-400",
    description: "Ideal para momentos de louvor com iluminação quente de palco.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 6100, 
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.40,
      shadows: 0.30,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "clean_bright",
    name: "Clean & Bright (Culto Matutino)",
    category: "Matutino",
    icon: "fa-sun text-blue-400",
    description: "Perfeito para cultos durante o dia, batismos e reuniões com bastante luz natural.",
    params: {
      exposure_compensation: 0.40,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.10,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.15,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "moody_stage",
    name: "Moody Stage (Palco Dramático)",
    category: "Jovens",
    icon: "fa-film text-purple-400",
    description: "Destaque para feixes de luz, fumaça de palco e momentos intensos.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.25,
      highlights: -0.60,
      shadows: -0.15,
      whites: 0.0,
      blacks: -0.10,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: -0.15,
      vignette: 0.0
    }
  },
  {
    id: "natural_skin_tone",
    name: "Natural Skin Tone (Retratos)",
    category: "Retratos",
    icon: "fa-user text-emerald-400",
    description: "Foco na fidelidade das cores para fotos de pregadores.",
    params: {
      exposure_compensation: 0.10, 
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.15, 
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "deep_matte",
    name: "Deep Matte (Editorial)",
    category: "Redes Sociais",
    icon: "fa-image text-slate-400",
    description: "Visual moderno para posts do Instagram e materiais de divulgação.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 0.90,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.20,
      saturation: 0.85,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "golden_hour_glow",
    name: "Golden Hour Glow (Externas)",
    category: "Externas",
    icon: "fa-sun text-orange-400",
    description: "Para batismos em rios, retiros e piqueniques de jovens ao entardecer.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 6500,
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.30,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "stage_light_fix",
    name: "Stage Light Fix (Correção)",
    category: "Correção",
    icon: "fa-wrench text-red-400",
    description: "Corrige rostos estourados por LEDs fortes.",
    params: {
      exposure_compensation: 0.15,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.50,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.75,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "monochrome_worship",
    name: "Monochrome Worship (P&B)",
    category: "Fine Art",
    icon: "fa-circle-half-stroke text-slate-300",
    description: "Transmite solenidade, emoção e foco nas expressões.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.35,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.0,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "vintage_film",
    name: "Vintage Film (Comunhão)",
    category: "Estilo",
    icon: "fa-camera-retro text-amber-600",
    description: "Curva em S suave com pretos lavados, para memórias e comunhão.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5800,
      tint: 0.0,
      contrast: 1.15,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.20,
      saturation: 0.90,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "low_light_noise_control",
    name: "Low-Light Noise Control",
    category: "Noturno",
    icon: "fa-moon text-indigo-400",
    description: "Para fotos tiradas com ISO elevado em momentos mais escuros do culto.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: 0.0,
      shadows: 0.40,
      whites: 0.0,
      blacks: -0.10,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: -0.20,
      dehaze: 0.0,
      vignette: 0.0
    }
  }
];

    // ================= SUPABASE CLIENT & AUTHENTICATION =================
    const SUPABASE_URL = "https://eioigfblgpufwkrlalxz.supabase.co";
    const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpb2lnZmJsZ3B1ZndrcmxhbHh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2NjAyODgsImV4cCI6MjEwMzIzNjI4OH0.y7Ntvovwdsy7TrMDgZWEIBpaQUKffYPb9HS17qPNt1w";
    let supabaseClient = null;

    try {
      if (typeof supabase !== 'undefined' && supabase.createClient) {
        supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
      }
    } catch(e) {
      console.warn("Supabase SDK init exception:", e);
    }

    window.addEventListener('DOMContentLoaded', async () => {
      const dateInp = document.getElementById('newServiceDate');
      if (dateInp) dateInp.valueAsDate = new Date();

      await initSupabaseAuth();
      setupSliderEvents();
      setupAddMorePhotosInput();
    });

    async function initSupabaseAuth() {
      try {
        if (!supabaseClient && typeof supabase !== 'undefined' && supabase.createClient) {
          supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        }

        if (supabaseClient) {
          // Check current active session from Supabase
          const { data: { session } } = await supabaseClient.auth.getSession();
          if (session && session.user) {
            handleSupabaseUserSession(session.user);
          } else {
            checkUserSession(); // fallback to local cache if offline
          }

          // Realtime Auth State Change Listener (persist automatically)
          supabaseClient.auth.onAuthStateChange(async (event, session) => {
            if (session && session.user) {
              handleSupabaseUserSession(session.user);
              if (event === 'SIGNED_IN') {
                closeSupabaseAuthModal();
                showToast(`Bem-vindo(a), ${currentUser ? currentUser.name : 'usuário'}!`);
                loadTeamData();
                await loadStoredServices();
                switchMainView('services');
              }
            } else if (event === 'SIGNED_OUT') {
              currentUser = null;
              localStorage.removeItem('CHURCHPHOTO_USER_SESSION');
              renderAuthenticatedUser(null);
              loadTeamData();
              await loadStoredServices();
            }
          });
        } else {
          checkUserSession();
        }
      } catch (err) {
        console.warn("Supabase Auth Init Error:", err);
        checkUserSession();
      }

      loadTeamData();
      await loadStoredServices();
    }

    function handleSupabaseUserSession(user) {
      const metadata = user.user_metadata || {};
      const uName = metadata.full_name || metadata.name || (user.email ? user.email.split('@')[0] : "Voluntário");
      const uUsername = (metadata.username || (user.email ? user.email.split('@')[0] : 'voluntario')).toLowerCase().replace(/\s+/g, '');
      const churchName = metadata.church_name || 'Igreja';

      currentUser = {
        id: user.id,
        name: uName,
        username: uUsername,
        email: user.email,
        church_name: churchName,
        avatar_url: metadata.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(uName)}&backgroundColor=059669`,
        isSupabase: true
      };

      localStorage.setItem('CHURCHPHOTO_USER_SESSION', JSON.stringify(currentUser));
      renderAuthenticatedUser(currentUser);
      loadTeamData();
      loadStoredServices();
    }

    function openSupabaseAuthModal() {
      const modal = document.getElementById('supabaseAuthModal');
      hideSupabaseAuthAlert();
      switchSupabaseAuthTab('login');
      modal.style.display = 'flex';
      modal.classList.remove('hidden');
    }

    function closeSupabaseAuthModal() {
      const modal = document.getElementById('supabaseAuthModal');
      modal.style.display = 'none';
      modal.classList.add('hidden');
    }

    function switchSupabaseAuthTab(tab) {
      currentAuthTab = tab;
      const loginBtn = document.getElementById('authTabLoginBtn');
      const regBtn = document.getElementById('authTabRegisterBtn');
      const formLogin = document.getElementById('formSupabaseLogin');
      const formReg = document.getElementById('formSupabaseRegister');
      hideSupabaseAuthAlert();

      if (tab === 'login') {
        loginBtn.className = "py-2 rounded-lg bg-emerald-600 text-white font-bold transition-all cursor-pointer";
        regBtn.className = "py-2 rounded-lg text-slate-400 hover:text-white transition-all cursor-pointer";
        formLogin.style.display = 'block'; formLogin.classList.remove('hidden');
        formReg.style.display = 'none'; formReg.classList.add('hidden');
      } else {
        regBtn.className = "py-2 rounded-lg bg-emerald-600 text-white font-bold transition-all cursor-pointer";
        loginBtn.className = "py-2 rounded-lg text-slate-400 hover:text-white transition-all cursor-pointer";
        formReg.style.display = 'block'; formReg.classList.remove('hidden');
        formLogin.style.display = 'none'; formLogin.classList.add('hidden');
      }
    }

    function showSupabaseAuthAlert(msg) {
      const alertBox = document.getElementById('supabaseAuthAlert');
      const text = document.getElementById('supabaseAuthAlertText');
      text.textContent = msg;
      alertBox.style.display = 'block';
      alertBox.classList.remove('hidden');
    }

    function hideSupabaseAuthAlert() {
      const alertBox = document.getElementById('supabaseAuthAlert');
      alertBox.style.display = 'none';
      alertBox.classList.add('hidden');
    }

    async function handleSupabaseLoginSubmit(e) {
      e.preventDefault();
      const email = document.getElementById('supabaseLoginEmail').value.trim();
      const password = document.getElementById('supabaseLoginPassword').value;
      const submitBtn = document.getElementById('supabaseLoginSubmitBtn');

      if (!email || !password) return;
      if (!supabaseClient) {
        showSupabaseAuthAlert("Erro ao inicializar Supabase. Verifique sua conexão.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Entrando...</span>`;

      try {
        const { data, error } = await supabaseClient.auth.signInWithPassword({
          email: email,
          password: password
        });

        if (error) {
          showSupabaseAuthAlert("Erro ao entrar: " + (error.message === 'Invalid login credentials' ? 'E-mail ou senha incorretos.' : error.message));
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="fa-solid fa-arrow-right-to-bracket"></i> <span>Entrar no Sistema</span>`;
          return;
        }

        if (data && data.user) {
          handleSupabaseUserSession(data.user);
        }
        closeSupabaseAuthModal();
        loadTeamData();
        await loadStoredServices();
        switchMainView('services');
        showToast(`Bem-vindo(a) de volta, ${currentUser ? currentUser.name : ''}!`);

      } catch(err) {
        showSupabaseAuthAlert("Erro de conexão: " + err.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-arrow-right-to-bracket"></i> <span>Entrar no Sistema</span>`;
      }
    }

    async function handleSupabaseRegisterSubmit(e) {
      e.preventDefault();
      const name = document.getElementById('supabaseRegisterName').value.trim();
      const email = document.getElementById('supabaseRegisterEmail').value.trim();
      const password = document.getElementById('supabaseRegisterPassword').value;
      const church = document.getElementById('supabaseRegisterChurch').value.trim();
      const submitBtn = document.getElementById('supabaseRegisterSubmitBtn');

      if (!name || !email || !password) return;
      if (!supabaseClient) {
        showSupabaseAuthAlert("Erro ao inicializar Supabase. Verifique sua conexão.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Criando Conta...</span>`;

      try {
        const { data, error } = await supabaseClient.auth.signUp({
          email: email,
          password: password,
          options: {
            data: {
              full_name: name,
              church_name: church || 'Igreja'
            }
          }
        });

        if (error) {
          showSupabaseAuthAlert("Erro no cadastro: " + error.message);
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="fa-solid fa-user-check"></i> <span>Criar Minha Conta Grátis</span>`;
          return;
        }

        closeSupabaseAuthModal();
        if (data.session) {
          showToast(`Conta criada com sucesso! Bem-vindo(a), ${name}!`);
        } else {
          showToast("Conta criada! Se a confirmação de e-mail estiver ativa no Supabase, verifique sua caixa de entrada.");
        }
        loadTeamData();
        await loadStoredServices();
      } catch(err) {
        showSupabaseAuthAlert("Erro de conexão: " + err.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-user-check"></i> <span>Criar Minha Conta Grátis</span>`;
      }
    }

    async function handleSupabaseGoogleLogin() {
      if (!supabaseClient) {
        showToast("Supabase não disponível no momento.");
        return;
      }
      try {
        const { error } = await supabaseClient.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: window.location.origin + window.location.pathname
          }
        });
        if (error) showSupabaseAuthAlert("Erro Google OAuth: " + error.message);
      } catch(e) {
        showSupabaseAuthAlert("Erro ao iniciar Google Login: " + e.message);
      }
    }

    async function handleSupabaseForgotPassword() {
      const email = prompt("Digite seu e-mail cadastrado para receber o link de redefinição de senha:");
      if (!email || !email.trim()) return;

      if (!supabaseClient) {
        showToast("Supabase não disponível.");
        return;
      }

      const { error } = await supabaseClient.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: window.location.origin + window.location.pathname
      });

      if (error) {
        showToast("Erro ao enviar e-mail: " + error.message);
      } else {
        showToast("Link de redefinição enviado para " + email + "!");
      }
    }

    async function logoutUser() {
      try {
        if (supabaseClient) {
          await supabaseClient.auth.signOut();
        }
      } catch(e) {}
      currentUser = null;
      localStorage.removeItem('CHURCHPHOTO_USER_SESSION');
      renderAuthenticatedUser(null);
      loadTeamData();
      await loadStoredServices();
      showToast("Você saiu da sua conta.");
    }

    // ================= ENTERPRISE INDEXEDDB PERSISTENT STORAGE =================
    // ================= ENTERPRISE INDEXEDDB & HYBRID SUPABASE CLOUD SYNC =================
    const DB_NAME = 'ChurchPhotoPro_DB';
    const DB_VERSION = 1;

    function openIndexedDB() {
      return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e) => {
          const db = e.target.result;
          if (!db.objectStoreNames.contains('services')) {
            db.createObjectStore('services', { keyPath: 'id' });
          }
          if (!db.objectStoreNames.contains('photos')) {
            db.createObjectStore('photos', { keyPath: 'id' });
          }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
      });
    }

    function fileToDataUrl(file) {
      return new Promise((resolve) => {
        if (!file) { resolve(''); return; }
        const url = URL.createObjectURL(file);
        const img = new Image();
        img.onload = () => {
          const maxDim = 1200;
          let w = img.width, h = img.height;
          if (w > maxDim || h > maxDim) {
            const ratio = maxDim / Math.max(w, h);
            w = Math.round(w * ratio);
            h = Math.round(h * ratio);
          }
          const canvas = document.createElement('canvas');
          canvas.width = w; canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);
          URL.revokeObjectURL(url);
          resolve(canvas.toDataURL('image/jpeg', 0.85));
        };
        img.onerror = () => {
          URL.revokeObjectURL(url);
          resolve('');
        };
        img.src = url;
      });
    }

    async function dbSaveService(service) {
      try {
        const db = await openIndexedDB();
        const tx = db.transaction(['services', 'photos'], 'readwrite');
        const sStore = tx.objectStore('services');
        const pStore = tx.objectStore('photos');

        // Clean JSON-serializable service header
        const srvMeta = {
          id: service.id,
          userId: currentUser ? currentUser.id : (service.userId || 'guest'),
          teamId: service.teamId || 'team_default',
          title: service.title,
          date: service.date,
          presetName: service.presetName || 'Luz Quente Natural',
          createdAt: service.createdAt || new Date().toISOString(),
          photoIds: (service.items || []).map(i => i.id)
        };
        sStore.put(srvMeta);

        // Save each photo with its permanent data URL / Base64 cleanly
        for (const item of (service.items || [])) {
          const photoRecord = {
            id: item.id,
            serviceId: service.id,
            fileName: item.fileName || 'foto.jpg',
            previewUrl: item.previewUrl || item.processedBase64 || item.originalBase64 || '',
            processedBase64: item.processedBase64 || null,
            originalBase64: item.originalBase64 || item.previewUrl || '',
            status: item.status || 'idle',
            metadata: item.metadata || null,
            analysis: item.analysis || null,
            isTop20: item.isTop20 !== false,
            currentParams: item.currentParams || null
          };
          pStore.put(photoRecord);
        }

        return new Promise((resolve) => {
          tx.oncomplete = () => resolve(true);
          tx.onerror = (e) => {
            console.error("IndexedDB tx error:", e);
            resolve(false);
          };
        });
      } catch (e) {
        console.error("IndexedDB Save Error:", e);
        return false;
      }
    }

    async function dbLoadAllServices() {
      try {
        const db = await openIndexedDB();
        const tx = db.transaction(['services', 'photos'], 'readonly');
        const sStore = tx.objectStore('services');
        const pStore = tx.objectStore('photos');

        // Execute both requests in parallel in the same tick so transaction doesn't auto-commit
        const sReq = sStore.getAll();
        const pReq = pStore.getAll();

        const [rawServices, rawPhotos] = await new Promise((resolve) => {
          let sRes = null, pRes = null;
          let sDone = false, pDone = false;

          sReq.onsuccess = () => {
            sRes = sReq.result || [];
            sDone = true;
            if (pDone) resolve([sRes, pRes]);
          };
          sReq.onerror = () => {
            sRes = [];
            sDone = true;
            if (pDone) resolve([sRes, pRes]);
          };

          pReq.onsuccess = () => {
            pRes = pReq.result || [];
            pDone = true;
            if (sDone) resolve([sRes, pRes]);
          };
          pReq.onerror = () => {
            pRes = [];
            pDone = true;
            if (sDone) resolve([sRes, pRes]);
          };

          tx.onerror = (e) => {
            console.error("IndexedDB tx load error:", e);
            resolve([[], []]);
          };
        });

        const photosMap = {};
        (rawPhotos || []).forEach(p => {
          if (!photosMap[p.serviceId]) photosMap[p.serviceId] = [];
          photosMap[p.serviceId].push({
            id: p.id,
            fileName: p.fileName,
            previewUrl: p.previewUrl || p.processedBase64 || p.originalBase64 || '',
            processedBase64: p.processedBase64,
            originalBase64: p.originalBase64 || p.previewUrl,
            cachedImg: null,
            metadata: p.metadata,
            analysis: p.analysis,
            isTop20: p.isTop20,
            currentParams: p.currentParams,
            status: p.status || 'idle'
          });
        });

        const loaded = [];
        for (const s of (rawServices || [])) {
          s.items = photosMap[s.id] || [];
          loaded.push(s);
        }

        // Sort descending by date
        loaded.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
        return loaded;
      } catch (e) {
        console.error("IndexedDB Load Error:", e);
        return [];
      }
    }

    async function dbDeleteService(serviceId) {
      try {
        const db = await openIndexedDB();
        // 1. Read photo IDs first
        const txRead = db.transaction(['photos'], 'readonly');
        const pStoreRead = txRead.objectStore('photos');
        const pReq = pStoreRead.getAll();
        const allPhotos = await new Promise((resolve) => {
          pReq.onsuccess = () => resolve(pReq.result || []);
          pReq.onerror = () => resolve([]);
        });

        // 2. Delete service and photos in a dedicated write transaction
        const txWrite = db.transaction(['services', 'photos'], 'readwrite');
        txWrite.objectStore('services').delete(serviceId);
        const pStoreWrite = txWrite.objectStore('photos');
        allPhotos.filter(p => p.serviceId === serviceId).forEach(p => {
          pStoreWrite.delete(p.id);
        });

        return new Promise(resolve => {
          txWrite.oncomplete = () => resolve(true);
          txWrite.onerror = () => resolve(false);
        });
      } catch(e) {
        console.error("dbDeleteService error:", e);
        return false;
      }
    }

    async function dbClearAll() {
      try {
        const db = await openIndexedDB();
        const tx = db.transaction(['services', 'photos'], 'readwrite');
        tx.objectStore('services').clear();
        tx.objectStore('photos').clear();
        return new Promise(resolve => {
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => resolve(false);
        });
      } catch(e) {
        return false;
      }
    }

    // ================= SUPABASE CLOUD DATABASE SYNC (OPTIONAL / HYBRID) =================

    function showSupabaseSqlModal() {
      if(document.getElementById('supabaseSqlModal')) return;
      const modalHtml = `
        <div id="supabaseSqlModal" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div class="bg-church-900 border border-church-800 rounded-2xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
            <div class="p-4 border-b border-church-800 flex justify-between items-center bg-church-950/50 rounded-t-2xl">
              <h3 class="text-base font-bold text-white flex items-center gap-2"><i class="fa-solid fa-database text-blue-500"></i> Configure seu Banco de Dados</h3>
              <button onclick="document.getElementById('supabaseSqlModal').remove()" class="text-slate-400 hover:text-white transition-colors"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div class="p-5 overflow-y-auto">
              <p class="text-sm text-slate-300 mb-4">Seu login funcionou, mas as tabelas para salvar seus cultos na nuvem não existem no seu projeto Supabase. Para habilitar a sincronização em tempo real entre seus dispositivos, execute o script SQL abaixo no <strong>SQL Editor</strong> do seu painel Supabase:</p>
              <div class="relative bg-church-950 border border-church-800 rounded-lg p-3 group">
                <button onclick="navigator.clipboard.writeText(document.getElementById('sqlCode').innerText); showToast('SQL copiado!');" class="absolute top-2 right-2 px-2 py-1 rounded bg-church-800 text-slate-300 text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer flex items-center gap-1"><i class="fa-regular fa-copy"></i> Copiar</button>
                <pre id="sqlCode" class="text-[11px] text-blue-300 font-mono overflow-x-auto whitespace-pre">
create table church_services (
  id text primary key,
  user_id uuid references auth.users(id),
  team_id text,
  title text,
  date text,
  preset_name text,
  created_at text,
  items_json jsonb
);

create table team_presets (
  id text primary key,
  user_id uuid references auth.users(id),
  team_id text,
  name text,
  params_json jsonb,
  created_at text
);
</pre>
              </div>
            </div>
            <div class="p-4 border-t border-church-800 flex justify-end">
              <button onclick="document.getElementById('supabaseSqlModal').remove()" class="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm transition-all cursor-pointer">Entendi</button>
            </div>
          </div>
        </div>
      `;
      document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    async function syncServicesWithSupabaseCloud() {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        const { data: cloudServices, error } = await supabaseClient
          .from('church_services')
          .select('*')
          .eq('user_id', currentUser.id)
          .order('created_at', { ascending: false });

        if (error) {
          if (error.code === '42P01') showSupabaseSqlModal();
          throw error;
        }

        if (!error && Array.isArray(cloudServices) && cloudServices.length > 0) {
          const localMap = new Map();
          churchServices.forEach(s => localMap.set(s.id, s));

          let hasNew = false;
          for (const cs of cloudServices) {
            if (!localMap.has(cs.id)) {
              let items = [];
              try {
                items = typeof cs.items_json === 'string' ? JSON.parse(cs.items_json) : (cs.items_json || []);
              } catch(e) {}

              const parsed = {
                id: cs.id,
                userId: cs.user_id,
                teamId: cs.team_id || 'team_default',
                title: cs.title,
                date: cs.date,
                presetName: cs.preset_name || 'Luz Quente Natural',
                createdAt: cs.created_at || new Date().toISOString(),
                items: items
              };
              churchServices.push(parsed);
              await dbSaveService(parsed);
              hasNew = true;
            }
          }

          if (hasNew) {
            churchServices.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
            renderServicesGrid();
            renderSidebarRecentServices();
          }
        }
      } catch (e) {
        // Non-blocking
        console.log("Supabase Cloud Sync note:", e);
      }
    }

    async function saveServiceToSupabaseCloud(service) {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        const cleanItems = (service.items || []).map(i => ({
          id: i.id,
          fileName: i.fileName,
          status: i.status,
          isTop20: i.isTop20,
          currentParams: i.currentParams,
          metadata: i.metadata
        }));

        const { error } = await supabaseClient.from('church_services').upsert({
          id: service.id,
          user_id: currentUser.id,
          team_id: service.teamId || 'team_default',
          title: service.title,
          date: service.date,
          preset_name: service.presetName || 'Luz Quente Natural',
          created_at: service.createdAt || new Date().toISOString(),
          items_json: cleanItems
        });
        
        if (error) {
          if (error.code === '42P01') showSupabaseSqlModal();
          throw error;
        }
      } catch (e) {
        // Non-blocking
      }
    }

    async function deleteServiceFromSupabaseCloud(serviceId) {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        await supabaseClient.from('church_services').delete().eq('id', serviceId).eq('user_id', currentUser.id);
      } catch (e) {}
    }

    async function syncPresetsWithSupabaseCloud() {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        const { data: cloudPresets, error } = await supabaseClient
          .from('team_presets')
          .select('*')
          .eq('user_id', currentUser.id);

        if (!error && Array.isArray(cloudPresets) && cloudPresets.length > 0) {
          const allMap = new Map();
          (activeTeam.presets || []).forEach(p => allMap.set(p.id, p));

          for (const cp of cloudPresets) {
            let params = {};
            try {
              params = typeof cp.params_json === 'string' ? JSON.parse(cp.params_json) : (cp.params_json || {});
            } catch(e) {}

            allMap.set(cp.id, {
              id: cp.id,
              name: cp.name,
              category: cp.category || 'Geral',
              icon: cp.icon || 'fa-sliders text-purple-400',
              description: cp.description || '',
              params: params
            });
          }

          activeTeam.presets = Array.from(allMap.values());
          saveTeamData();
        }
      } catch (e) {}
    }

    async function savePresetToSupabaseCloud(preset) {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        await supabaseClient.from('team_presets').upsert({
          id: preset.id,
          user_id: currentUser.id,
          name: preset.name,
          category: preset.category || 'Geral',
          description: preset.description || '',
          icon: preset.icon || 'fa-sliders text-purple-400',
          params_json: preset.params || {}
        });
      } catch (e) {}
    }

    async function deletePresetFromSupabaseCloud(presetId) {
      if (!supabaseClient || !currentUser || !currentUser.id) return;
      try {
        await supabaseClient.from('team_presets').delete().eq('id', presetId).eq('user_id', currentUser.id);
      } catch (e) {}
    }

    function checkUserSession() {
      const savedUser = localStorage.getItem('CHURCHPHOTO_USER_SESSION');
      if (savedUser) {
        try {
          currentUser = JSON.parse(savedUser);
          renderAuthenticatedUser(currentUser);
        } catch (e) {
          currentUser = null;
        }
      }
    }

    function renderAuthenticatedUser(user) {
      const sideLoggedIn = document.getElementById('sideProfileLoggedIn');
      const sideLoggedOut = document.getElementById('sideProfileLoggedOut');
      const sideAvatar = document.getElementById('sideUserAvatar');
      const sideName = document.getElementById('sideUserName');
      const sideHandle = document.getElementById('sideUserHandle');
      const heroStatus = document.getElementById('userAccountStatusBadge');

      if (user) {
        if (sideLoggedOut) { sideLoggedOut.style.display = 'none'; sideLoggedOut.classList.add('hidden'); }
        if (sideLoggedIn) { sideLoggedIn.style.display = 'flex'; sideLoggedIn.classList.remove('hidden'); }

        if (sideAvatar) sideAvatar.src = user.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(user.name || 'M')}&backgroundColor=2563eb`;
        if (sideName) sideName.textContent = user.name || 'Voluntário';
        if (sideHandle) sideHandle.textContent = `@${user.username || 'voluntario'}`;
        if (heroStatus) heroStatus.innerHTML = `<span class="text-emerald-400 font-bold">Conectado como: ${user.name} (@${user.username})</span>`;
      } else {
        if (sideLoggedIn) { sideLoggedIn.style.display = 'none'; sideLoggedIn.classList.add('hidden'); }
        if (sideLoggedOut) { sideLoggedOut.style.display = 'flex'; sideLoggedOut.classList.remove('hidden'); }
        if (heroStatus) heroStatus.textContent = 'Conta: Visitante (Não autenticado)';
      }

      renderSidebarTeamMembers();
    }

    async function logoutUser() {
      const wasAuth0 = currentUser && currentUser.isAuth0;
      currentUser = null;
      localStorage.removeItem('CHURCHPHOTO_USER_SESSION');
      renderAuthenticatedUser(null);
      
      // Reset view to clean guest state
      loadTeamData();
      loadStoredServices();
      showToast("Você saiu da conta com sucesso.");

      if (wasAuth0 && auth0Client) {
        try {
          const isAuth = await auth0Client.isAuthenticated();
          if (isAuth) {
            await auth0Client.logout({
              logoutParams: {
                returnTo: window.location.origin + window.location.pathname
              }
            });
          }
        } catch(e) {}
      }
    }

    // ================= SIDEBAR & NAVIGATION =================

    function toggleSidebar() {
      const sidebar = document.getElementById('mainSidebar');
      const backdrop = document.getElementById('mobileSidebarBackdrop');
      
      if (sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
        backdrop.style.display = 'block';
        backdrop.classList.remove('hidden');
      } else {
        sidebar.classList.add('-translate-x-full');
        backdrop.style.display = 'none';
        backdrop.classList.add('hidden');
      }
    }

    function toggleSidebarCollapse() {
      const sidebar = document.getElementById('mainSidebar');
      const icon = document.getElementById('collapseToggleIcon');
      isSidebarCollapsed = !isSidebarCollapsed;

      if (isSidebarCollapsed) {
        sidebar.classList.remove('sidebar-expanded');
        sidebar.classList.add('sidebar-collapsed');
        icon.className = 'fa-solid fa-chevron-right text-xs';
      } else {
        sidebar.classList.remove('sidebar-collapsed');
        sidebar.classList.add('sidebar-expanded');
        icon.className = 'fa-solid fa-chevron-left text-xs';
      }
    }

    function switchMainView(view) {
      currentMainView = view;
      const viewServices = document.getElementById('viewServicesSection');
      const viewFunnel = document.getElementById('viewFunnelSection');
      const viewStudio = document.getElementById('viewStudioSection');
      const viewTeamArea = document.getElementById('viewTeamAreaSection');

      const topTitle = document.getElementById('topNavViewTitle');
      const topBadge = document.getElementById('topNavViewBadge');

      const sideNavServices = document.getElementById('sideNavServices');
      const sideNavFunnel = document.getElementById('sideNavFunnel');
      const sideNavStudio = document.getElementById('sideNavStudio');
      const sideNavTeamArea = document.getElementById('sideNavTeamArea');

      [sideNavServices, sideNavFunnel, sideNavStudio, sideNavTeamArea].forEach(btn => {
        if (btn) btn.className = "sidebar-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-church-800/70 transition-all cursor-pointer";
      });

      [viewServices, viewFunnel, viewStudio, viewTeamArea].forEach(v => {
        if (v) { v.style.display = 'none'; v.classList.add('hidden'); }
      });

      if (view === 'services') {
        viewServices.style.display = 'flex'; viewServices.classList.remove('hidden');
        topTitle.textContent = "Meus Cultos";
        topBadge.textContent = currentUser ? `Conta: @${currentUser.username}` : "Painel Central";
        sideNavServices.className = "sidebar-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 text-white transition-all cursor-pointer shadow-sm";
        renderServicesGrid();
      } else if (view === 'funnel') {
        viewFunnel.style.display = 'flex'; viewFunnel.classList.remove('hidden');
        topTitle.textContent = "Funil de Curadoria";
        topBadge.textContent = activeService ? activeService.title : "3 Fases";
        sideNavFunnel.className = "sidebar-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 text-white transition-all cursor-pointer shadow-sm";
        renderFunnelUI();
      } else if (view === 'team_area') {
        viewTeamArea.style.display = 'flex'; viewTeamArea.classList.remove('hidden');
        topTitle.textContent = "Meus Presets";
        topBadge.textContent = activeTeam.name;
        sideNavTeamArea.className = "sidebar-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold bg-purple-600 text-white transition-all cursor-pointer shadow-sm";
        renderTeamAreaView();
      } else {
        viewStudio.style.display = 'flex'; viewStudio.classList.remove('hidden');
        topTitle.textContent = "Estúdio DSLR";
        topBadge.textContent = activeService ? activeService.title : "Comparador";
        sideNavStudio.className = "sidebar-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 text-white transition-all cursor-pointer shadow-sm";
        if (activeItem) showProcessedViewer(activeItem);
      }

      if (window.innerWidth < 768) {
        document.getElementById('mainSidebar').classList.add('-translate-x-full');
        document.getElementById('mobileSidebarBackdrop').style.display = 'none';
      }
    }

    // ================= REAL TEAM WORKSPACE & PRESETS LINKED TO TEAM =================

    function getStorageTeamKey() {
      return currentUser ? `CHURCHPHOTO_TEAM_${currentUser.id}` : 'CHURCHPHOTO_TEAM_GUEST';
    }

    function loadTeamData() {
      // CLEAR CACHE TO FORCE NEW PRESETS
      localStorage.removeItem('CHURCHPHOTO_SAVED_PRESETS_MASTER');
      
      const key = getStorageTeamKey();
      let storedTeam = null;
      try {
        const raw = localStorage.getItem(key);
        if (raw) storedTeam = JSON.parse(raw);
      } catch(e) {}

      if (!storedTeam) {
        try {
          const guestRaw = localStorage.getItem('CHURCHPHOTO_TEAM_GUEST');
          if (guestRaw) storedTeam = JSON.parse(guestRaw);
        } catch(e) {}
      }

      const teamName = currentUser ? `Mídia ${currentUser.church_name || 'Sede'}` : 'Mídia Principal';
      const members = (storedTeam && storedTeam.members) ? storedTeam.members : [];

      // Combine DEFAULT presets with all stored custom presets
      const allPresetsMap = new Map();
      DEFAULT_TEAM_PRESETS.forEach(p => allPresetsMap.set(p.id, { ...p }));

//       // if (storedTeam && storedTeam.presets && Array.isArray(storedTeam.presets)) {
      }

//       // if (Array.isArray(userPresets)) {
      }

      activeTeam = {
        id: (storedTeam && storedTeam.id) ? storedTeam.id : 'team_default',
        name: (storedTeam && storedTeam.name) ? storedTeam.name : teamName,
        members: members,
        presets: Array.from(allPresetsMap.values())
      };

      saveTeamData();
    }

    function saveTeamData() {
      try {
        const key = getStorageTeamKey();
        localStorage.setItem(key, JSON.stringify(activeTeam));
        if (activeTeam && activeTeam.presets) {
          localStorage.setItem('CHURCHPHOTO_SAVED_PRESETS_MASTER', JSON.stringify(activeTeam.presets));
        }
      } catch(e) {}
      renderSidebarTeamMembers();
      renderStudioPresetsStrip();
    }

    function getRealTeamMembersList() {
      const members = [];
      if (currentUser) {
        members.push({ name: currentUser.name, username: currentUser.username, role: "Você (Líder da Equipe)" });
      } else {
        members.push({ name: "Você (Visitante)", username: "visitante", role: "Não autenticado" });
      }

      if (activeTeam.members && activeTeam.members.length > 0) {
        activeTeam.members.forEach(m => members.push(m));
      }
      return members;
    }

    function renderSidebarTeamMembers() {
      const listContainer = document.getElementById('sidebarRealMembersList');
      const teamTitle = document.getElementById('sidebarTeamTitle');
      const countBadge = document.getElementById('sidebarTeamCountBadge');
      const topBadge = document.getElementById('topTeamNameBadge');
      const sidePresetsBadge = document.getElementById('sideTeamPresetsCountBadge');
      const studioTeamLabel = document.getElementById('studioTeamNameLabel');

      const teamName = activeTeam.name || "Mídia Principal";
      if (teamTitle) teamTitle.textContent = teamName;
      if (topBadge) topBadge.textContent = teamName;
      if (studioTeamLabel) studioTeamLabel.textContent = teamName;

      const members = getRealTeamMembersList();
      if (countBadge) countBadge.textContent = `${members.length} membro${members.length > 1 ? 's' : ''}`;
      if (sidePresetsBadge) sidePresetsBadge.textContent = `${(activeTeam.presets || []).length} presets`;

      if (listContainer) {
        listContainer.innerHTML = members.map(m => `
          <div class="flex items-center justify-between py-1 px-1.5 rounded-lg bg-church-900/80 border border-church-800/60">
            <div class="flex items-center gap-1.5 min-w-0">
              <img src="https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(m.name)}&backgroundColor=2563eb" class="w-4 h-4 rounded-full border border-blue-500/40 shrink-0">
              <span class="text-[11px] font-semibold text-slate-200 truncate">${m.name}</span>
            </div>
            <span class="text-[9px] font-mono text-slate-400 shrink-0">${m.role || 'Membro'}</span>
          </div>
        `).join('');
      }
    }

    function renderTeamAreaView() {
      const headerTitle = document.getElementById('teamAreaHeaderName');
      const membersGrid = document.getElementById('teamAreaMembersGrid');
      const memberCount = document.getElementById('teamAreaMemberCountBadge');
      const presetsList = document.getElementById('teamPresetsManagerCardsList');

      if (headerTitle) headerTitle.textContent = activeTeam.name;

      const members = getRealTeamMembersList();
      if (memberCount) memberCount.textContent = `${members.length} membro${members.length > 1 ? 's' : ''} ativo${members.length > 1 ? 's' : ''}`;

      if (membersGrid) {
        membersGrid.innerHTML = members.map((m, idx) => `
          <div class="p-3.5 rounded-2xl bg-church-900 border border-church-800 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-2.5 min-w-0">
              <img src="https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(m.name)}&backgroundColor=2563eb" class="w-9 h-9 rounded-full border border-blue-500/50 shrink-0">
              <div class="min-w-0">
                <span class="text-xs font-bold text-white block truncate">${m.name}</span>
                <span class="text-[10px] text-blue-400 font-mono block truncate">@${m.username}</span>
              </div>
            </div>
            <span class="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/60 text-[9px] font-mono shrink-0">${m.role}</span>
          </div>
        `).join('');
      }

      const presets = activeTeam.presets || [];
      if (presetsList) {
        presetsList.innerHTML = presets.map(p => {
          const par = p.params || {};
          return `
            <div class="rounded-2xl bg-church-900 border border-church-800 hover:border-purple-500/50 p-4 shadow-xl flex flex-col justify-between transition-all">
              <div>
                <div class="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <div class="flex items-center gap-2">
                      <h4 class="text-sm font-bold text-white">${p.name}</h4>
                      <span class="px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 border border-purple-800/60 text-[9px] font-mono">${p.category || 'Geral'}</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-1 leading-snug">${p.description}</p>
                  </div>
                </div>

                <div class="flex flex-wrap gap-1.5 my-3">
                  <span class="px-2 py-0.5 rounded bg-church-950 text-blue-400 text-[10px] font-mono">Exp: ${par.exposure_compensation > 0 ? '+' : ''}${par.exposure_compensation || 0} EV</span>
                  <span class="px-2 py-0.5 rounded bg-church-950 text-amber-400 text-[10px] font-mono">Kelvin: ${par.temperature_kelvin || 5500}K</span>
                  <span class="px-2 py-0.5 rounded bg-church-950 text-emerald-400 text-[10px] font-mono">f/${par.f_stop_simulation || 2.8}</span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 pt-2 border-t border-church-800 mt-2">
                <button onclick="openEditPresetModal('${p.id}')" class="py-2 px-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
                  <i class="fa-solid fa-sliders text-xs"></i>
                  <span>Editar Sliders</span>
                </button>

                <button onclick="applyPresetToActiveService('${p.id}')" class="py-2 px-3 rounded-xl bg-church-800 hover:bg-church-700 text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
                  <i class="fa-solid fa-wand-magic-sparkles text-xs text-amber-300"></i>
                  <span>Aplicar Culto</span>
                </button>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    function openInviteMemberModal() {
      const modal = document.getElementById('inviteMemberModal');
      document.getElementById('inviteMemberInput').value = '';
      modal.style.display = 'flex';
      modal.classList.remove('hidden');
    }

    function closeInviteMemberModal() {
      const modal = document.getElementById('inviteMemberModal');
      modal.style.display = 'none';
      modal.classList.add('hidden');
    }

    function handleInviteMemberSubmit(e) {
      e.preventDefault();
      const input = document.getElementById('inviteMemberInput');
      const role = document.getElementById('inviteMemberRoleSelect').value;
      const val = input.value.trim();
      if (!val) return;

      const cleanUser = val.replace('@', '').toLowerCase();
      const cleanName = cleanUser.charAt(0).toUpperCase() + cleanUser.slice(1);

      const newMember = {
        name: cleanName,
        username: cleanUser,
        role: role || "Voluntário de Mídia"
      };

      if (!activeTeam.members) activeTeam.members = [];
      activeTeam.members.push(newMember);
      saveTeamData();
      closeInviteMemberModal();
      renderTeamAreaView();
      showToast(`@${cleanUser} adicionado à equipe com sucesso!`);
    }

    function renderStudioPresetsStrip() {
      const container = document.getElementById('presetsContainer');
      if (!container) return;

      const presets = activeTeam.presets || DEFAULT_TEAM_PRESETS;
      container.innerHTML = presets.map((p, idx) => `
        <button onclick="applyPresetObj('${p.id}')" class="shrink-0 p-3 rounded-2xl bg-church-900 border ${idx === 0 ? 'border-amber-400/80' : 'border-church-800'} hover:border-purple-500/60 active:scale-95 text-left transition-all w-[185px] sm:w-[220px] cursor-pointer">
          <div class="flex items-center justify-between gap-1 mb-1">
            <div class="flex items-center gap-1.5 text-xs font-bold text-white truncate">
              <i class="fa-solid ${p.icon || 'fa-sliders'} text-xs"></i>
              <span class="truncate">${p.name}</span>
            </div>
            <span class="px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 text-[8px] font-mono shrink-0">${p.category || 'Geral'}</span>
          </div>
          <p class="text-[11px] text-slate-400 line-clamp-2 leading-tight">${p.description}</p>
        </button>
      `).join('');
    }

    function openSavePresetModal() {
      document.getElementById('presetModalHeaderTitle').textContent = "Salvar Novo Preset da Equipe";
      document.getElementById('editingPresetId').value = "";
      document.getElementById('newPresetName').value = "";
      document.getElementById('newPresetDesc').value = "";
      
      const modal = document.getElementById('savePresetModal');
      modal.style.display = 'flex';
      modal.classList.remove('hidden');
    }

    function openEditPresetModal(presetId) {
      const p = (activeTeam.presets || []).find(x => x.id === presetId);
      if (!p) return;

      document.getElementById('presetModalHeaderTitle').textContent = `Editar Preset: ${p.name}`;
      document.getElementById('editingPresetId').value = p.id;
      document.getElementById('newPresetName').value = p.name;
      document.getElementById('newPresetCategory').value = p.category || "Louvor";
      document.getElementById('newPresetDesc').value = p.description || "";

      if (p.params) {
        document.getElementById('preset_edit_exp').value = p.params.exposure_compensation || 0;
        document.getElementById('preset_edit_kelvin').value = p.params.temperature_kelvin || 5500;
        document.getElementById('preset_edit_contrast').value = p.params.contrast || 1.10;
        document.getElementById('preset_edit_fstop').value = p.params.f_stop_simulation || 2.8;
      }

      const modal = document.getElementById('savePresetModal');
      modal.style.display = 'flex';
      modal.classList.remove('hidden');
    }

    function closeSavePresetModal() {
      const modal = document.getElementById('savePresetModal');
      modal.style.display = 'none';
      modal.classList.add('hidden');
    }

    function handleSaveTeamPresetSubmit(e) {
      e.preventDefault();
      const editId = document.getElementById('editingPresetId').value;
      const name = document.getElementById('newPresetName').value.trim();
      const cat = document.getElementById('newPresetCategory').value;
      const desc = document.getElementById('newPresetDesc').value.trim() || 'Preset calibrado para a equipe.';

      const exp = parseFloat(document.getElementById('preset_edit_exp').value);
      const kelvin = parseInt(document.getElementById('preset_edit_kelvin').value);
      const contrast = parseFloat(document.getElementById('preset_edit_contrast').value);
      const fstop = parseFloat(document.getElementById('preset_edit_fstop').value);

      const params = {
        exposure_compensation: exp,
        temperature_kelvin: kelvin,
        tint: 0.0,
        contrast: contrast,
        highlights_recovery: 0.45,
        shadows_lift: 0.35,
        saturation: 1.03,
        vibrance: 1.06,
        chromatic_aberration_fix: 0.50,
        led_clipping_restoration: 0.60,
        stage_led_tint_suppression: 0.45,
        vignette_correction: 0.35,
        selective_denoise: 0.30,
        skin_tone_protection_strength: 0.88,
        f_stop_simulation: fstop,
        bokeh_smoothness: 0.75,
        subject_microcontrast: 0.75
      };

      if (!activeTeam.presets) activeTeam.presets = [];

      let presetToSync = null;
      if (editId) {
        const target = activeTeam.presets.find(x => x.id === editId);
        if (target) {
          target.name = name;
          target.category = cat;
          target.description = desc;
          target.params = params;
          presetToSync = target;
          showToast(`Preset "${name}" atualizado na equipe!`);
        }
      } else {
        const newPreset = {
          id: 'preset_' + Date.now(),
          name: name,
          category: cat,
          icon: "fa-sliders text-purple-400",
          description: desc,
          params: params
        };
        activeTeam.presets.unshift(newPreset);
        presetToSync = newPreset;
        showToast(`Novo preset "${name}" adicionado à equipe!`);
      }

      saveTeamData();
      if (presetToSync) {
        savePresetToSupabaseCloud(presetToSync).catch(() => {});
      }
      closeSavePresetModal();
      renderTeamAreaView();
    }

    function applyPresetToActiveService(presetId) {
      const p = (activeTeam.presets || []).find(x => x.id === presetId);
      if (!p) return;

      if (activeService && activeService.items) {
        activeService.items.forEach(item => {
          item.currentParams = { ...p.params };
        });
        showToast(`Preset "${p.name}" aplicado a todas as fotos do culto!`);
        switchMainView('studio');
        processAllInQueue();
      } else {
        showToast(`Preset "${p.name}" pronto para ser usado no estúdio!`);
      }
    }

    function applyPresetObj(presetId) {
      const p = (activeTeam.presets || []).find(x => x.id === presetId);
      if (!p || !activeItem) return;
      
      activeItem.currentParams = { ...p.params };
      const par = p.params;

      const setVal = (id, val, suffix = '') => {
        const el = document.getElementById(`param_${id}`);
        const valEl = document.getElementById(`val_${id}`);
        if (el && val !== undefined) {
          el.value = val;
          if (valEl) valEl.textContent = `${val}${suffix}`;
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
      showToast(`Preset "${p.name}" aplicado!`);
    }

    // ================= REAL AI IMAGE ANALYSIS (LAPLACIAN & PERCEPTUAL HASH) =================
    
    async function analyzeImageReal(fileOrBlob) {
      return new Promise((resolve) => {
        const img = new Image();
        const url = URL.createObjectURL(fileOrBlob);
        img.onload = () => {
          const w = img.width;
          const h = img.height;
          
          const hashCanvas = document.createElement('canvas');
          hashCanvas.width = 9;
          hashCanvas.height = 8;
          const hctx = hashCanvas.getContext('2d', { willReadFrequently: true });
          hctx.drawImage(img, 0, 0, 9, 8);
          const hData = hctx.getImageData(0, 0, 9, 8).data;
          
          let hash = '';
          for (let y = 0; y < 8; y++) {
            for (let x = 0; x < 8; x++) {
              const idx1 = (y * 9 + x) * 4;
              const idx2 = (y * 9 + (x + 1)) * 4;
              const g1 = hData[idx1] * 0.299 + hData[idx1+1] * 0.587 + hData[idx1+2] * 0.114;
              const g2 = hData[idx2] * 0.299 + hData[idx2+1] * 0.587 + hData[idx2+2] * 0.114;
              hash += (g1 > g2) ? '1' : '0';
            }
          }

          const scale = Math.min(250 / Math.max(w, h), 1);
          const rw = Math.round(w * scale);
          const rh = Math.round(h * scale);
          
          const sCanvas = document.createElement('canvas');
          sCanvas.width = rw;
          sCanvas.height = rh;
          const sctx = sCanvas.getContext('2d', { willReadFrequently: true });
          sctx.drawImage(img, 0, 0, rw, rh);
          
          const srcData = sctx.getImageData(0, 0, rw, rh);
          let sum = 0, sqSum = 0, count = 0;
          const data = srcData.data;
          
          for (let y = 1; y < rh - 1; y++) {
            for (let x = 1; x < rw - 1; x++) {
              const i = (y * rw + x) * 4;
              const l = data[i]*0.299 + data[i+1]*0.587 + data[i+2]*0.114;
              const top = data[i - rw * 4]*0.299 + data[i - rw * 4 + 1]*0.587 + data[i - rw * 4 + 2]*0.114;
              const bot = data[i + rw * 4]*0.299 + data[i + rw * 4 + 1]*0.587 + data[i + rw * 4 + 2]*0.114;
              const left = data[i - 4]*0.299 + data[i - 3]*0.587 + data[i - 2]*0.114;
              const right = data[i + 4]*0.299 + data[i + 5]*0.587 + data[i + 6]*0.114;
              const lap = top + bot + left + right - 4 * l;
              sum += lap; sqSum += lap * lap; count++;
            }
          }
          
          const mean = sum / count;
          const variance = (sqSum / count) - (mean * mean);
          
          let score = 5.0 + (variance / 1000) * 5;
          if (score > 9.9) score = 9.9;
          if (score < 1.0) score = 1.0;
          
          URL.revokeObjectURL(url);
          resolve({ hash, sharpness: parseFloat(score.toFixed(1)), variance });
        };
        img.onerror = () => resolve({ hash: '0'.repeat(64), sharpness: 5.0, variance: 0 });
        img.src = url;
      });
    }

    function computePhotoScore(item) {
      if (item && item.metadata && item.metadata.sharpness) return item.metadata.sharpness.toFixed(1);
      return '8.5';
    }

    function calculateHammingDistance(h1, h2) {
      if (!h1 || !h2 || h1.length !== h2.length) return 999;
      let d = 0;
      for (let i = 0; i < h1.length; i++) {
        if (h1[i] !== h2[i]) d++;
      }
      return d;
    }

    function setFunnelStep(step) {
      currentFunnelStep = step;
      const s1 = document.getElementById('funnelStage1');
      const s2 = document.getElementById('funnelStage2');
      const s3 = document.getElementById('funnelStage3');

      const b1 = document.getElementById('stepBtn1');
      const b2 = document.getElementById('stepBtn2');
      const b3 = document.getElementById('stepBtn3');

      [b1, b2, b3].forEach(b => {
        b.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all";
      });

      if (step === 1) {
        s1.style.display = 'flex'; s1.classList.remove('hidden');
        s2.style.display = 'none'; s2.classList.add('hidden');
        s3.style.display = 'none'; s3.classList.add('hidden');
        b1.className = "px-3 py-1.5 rounded-lg bg-amber-600 text-white font-bold flex items-center gap-1.5 transition-all";
        renderDeduplicationGroups();
      } else if (step === 2) {
        // Descartar fotos duplicadas (não campeãs) da Fase 1
        if (activeService && activeService.dedupGroups) {
          const discardedIds = new Set();
          activeService.dedupGroups.forEach(g => {
            g.allPhotos.forEach(p => {
              if (p.id !== g.championId) discardedIds.add(p.id);
            });
          });
          activeService.items = activeService.items.filter(i => !discardedIds.has(i.id));
          dbSaveService(activeService);
        }

        s1.style.display = 'none'; s1.classList.add('hidden');
        s2.style.display = 'flex'; s2.classList.remove('hidden');
        s3.style.display = 'none'; s3.classList.add('hidden');
        b2.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold flex items-center gap-1.5 transition-all";
        renderTop20Grid();
      } else {
        // Enviar para Fase 3 (Studio) apenas as selecionadas na Fase 2
        if (activeService && activeService.items) {
          activeService.items = activeService.items.filter(i => i.isTop20 !== false);
          dbSaveService(activeService);
          openServiceInStudio(activeService.id);
        } else {
          switchMainView('studio');
        }
      }
    }

    function renderFunnelUI() {
      if (!activeService || !activeService.items || activeService.items.length === 0) {
        document.getElementById('dedupGroupsContainer').innerHTML = `<p class="text-xs text-slate-500 py-4">Nenhuma foto carregada para este culto.</p>`;
        return;
      }
      setFunnelStep(1);
    }

    function renderDeduplicationGroups() {
      const container = document.getElementById('dedupGroupsContainer');
      if (!activeService || !activeService.items || activeService.items.length === 0) return;

      if (!activeService.dedupGroups) {
        const groups = [];
        const items = activeService.items;
        
        const unassigned = [...items];
        let groupCounter = 1;
        
        while(unassigned.length > 0) {
          const champion = unassigned.shift();
          const chunk = [champion];
          
          for (let i = unassigned.length - 1; i >= 0; i--) {
            const candidate = unassigned[i];
            const dist = calculateHammingDistance(
              champion.metadata ? champion.metadata.hash : '',
              candidate.metadata ? candidate.metadata.hash : ''
            );
            if (dist <= 8) {
              chunk.push(candidate);
              unassigned.splice(i, 1);
            }
          }
          
          chunk.sort((a, b) => parseFloat(computePhotoScore(b)) - parseFloat(computePhotoScore(a)));
          
          if (chunk.length > 1) {
            groups.push({
              groupId: `grp_${groupCounter++}`,
              name: `Sequência ${groupCounter - 1} (${chunk.length} fotos)`,
              championId: chunk[0].id,
              allPhotos: chunk
            });
          }
        }
        activeService.dedupGroups = groups;
      }

      const groups = activeService.dedupGroups;
      
      if (groups.length === 0) {
         container.innerHTML = `
           <div class="text-center py-10">
             <i class="fa-solid fa-check-double text-4xl text-emerald-500 mb-4"></i>
             <p class="text-sm font-bold text-white mb-2">Sua galeria está limpa!</p>
             <p class="text-xs text-slate-400">A IA não detectou fotos repetidas ou em rajada.</p>
             <button onclick="setFunnelStep(2)" class="mt-4 px-4 py-2 rounded-lg bg-emerald-600 text-white font-bold text-xs cursor-pointer">Ir para Seleção Top 20</button>
           </div>`;
         return;
      }

      container.innerHTML = groups.map(g => {
        const champ = g.allPhotos.find(p => p.id === g.championId) || g.allPhotos[0];
        const discarded = g.allPhotos.filter(p => p.id !== champ.id);

        champ.isTop20 = true;
        discarded.forEach(d => {
          const globalItem = activeService.items.find(i => i.id === d.id);
          if(globalItem) globalItem.isTop20 = false;
        });

        return `
          <div class="rounded-2xl bg-church-900 border border-church-800 p-4 flex flex-col gap-3 shadow-md">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-white flex items-center gap-1.5">
                <i class="fa-solid fa-layer-group text-blue-400"></i> ${g.name}
              </span>
              <span class="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/60 text-[9px] font-mono font-bold">
                ⭐ Foto Campeã Eleita
              </span>
            </div>

            <div class="relative rounded-xl overflow-hidden bg-church-950 border-2 border-amber-400/80 aspect-video flex items-center justify-center">
              <img src="${champ.processedBase64 || champ.previewUrl}" class="w-full h-full object-cover">
              <span class="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 text-amber-300 text-[10px] font-bold flex items-center gap-1">
                <i class="fa-solid fa-trophy text-amber-400 text-xs"></i> Campeã (Maior Nitidez: ${computePhotoScore(champ)})
              </span>
            </div>

            ${discarded.length > 0 ? `
              <div class="pt-2 border-t border-church-800">
                <span class="text-[10px] text-slate-400 font-semibold block mb-1.5">Alternativas na mesma sequência (descartadas):</span>
                <div class="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                  ${discarded.map(alt => `
                    <div class="relative w-16 h-16 shrink-0 rounded-lg overflow-hidden bg-church-950 border border-church-800 group/alt">
                      <img src="${alt.processedBase64 || alt.previewUrl}" class="w-full h-full object-cover opacity-60 group-hover/alt:opacity-100 transition-opacity">
                      <button onclick="setChampionPhoto('${g.groupId}', '${alt.id}')" class="absolute inset-0 bg-black/70 opacity-0 group-hover/alt:opacity-100 flex items-center justify-center text-amber-300 text-[9px] font-bold transition-opacity cursor-pointer text-center p-1 leading-tight">
                        Tornar Campeã
                      </button>
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
    }

    function setChampionPhoto(groupId, photoId) {
      const group = activeService.dedupGroups.find(g => g.groupId === groupId);
      if (group) {
        group.championId = photoId;
        showToast("Foto campeã da sequência atualizada!");
        renderDeduplicationGroups();
      }
    }

    function renderTop20Grid() {
      const container = document.getElementById('top20GridContainer');
      const counter = document.getElementById('top20LiveCounter');
      if (!activeService || !activeService.items) return;

      const items = activeService.items;
      let selectedCount = items.filter(i => i.isTop20 !== false).length;
      if (counter) counter.textContent = `${selectedCount} / 20 Selecionadas`;

      container.innerHTML = items.map((item, idx) => {
        const isSelected = item.isTop20 !== false;
        const score = computePhotoScore(item);

        return `
          <div onclick="togglePhotoTop20Selection('${item.id}')" class="relative rounded-xl overflow-hidden bg-church-900 border-2 ${isSelected ? 'border-blue-500 shadow-lg shadow-blue-500/20' : 'border-church-800 opacity-60'} cursor-pointer transition-all flex flex-col group">
            <div class="relative aspect-[4/5] bg-church-950 flex items-center justify-center overflow-hidden">
              <img src="${item.processedBase64 || item.previewUrl}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200">
              
              <span class="absolute top-1.5 left-1.5 px-1.5 py-0.5 rounded bg-black/80 border border-amber-400/40 text-amber-300 text-[9px] font-mono font-bold flex items-center gap-1">
                <i class="fa-solid fa-star text-amber-400 text-[8px]"></i> ${score}
              </span>

              <div class="absolute top-1.5 right-1.5 w-5 h-5 rounded-full ${isSelected ? 'bg-blue-600 text-white' : 'bg-black/60 text-transparent'} border border-white/40 flex items-center justify-center text-[10px]">
                <i class="fa-solid fa-check"></i>
              </div>
            </div>

            <div class="p-2 text-[11px]">
              <span class="font-bold text-white block truncate">${item.fileName || 'Foto do Culto'}</span>
              <span class="text-[9px] text-blue-400 font-mono">Destaque IA</span>
            </div>
          </div>
        `;
      }).join('');
    }

    function togglePhotoTop20Selection(photoId) {
      const item = activeService.items.find(i => i.id === photoId);
      if (item) {
        item.isTop20 = !(item.isTop20 !== false);
        renderTop20Grid();
      }
    }

    function autoSelectTop20() {
      if (activeService && activeService.items) {
        const sorted = [...activeService.items].sort((a, b) => {
          const scoreA = parseFloat(computePhotoScore(a));
          const scoreB = parseFloat(computePhotoScore(b));
          return scoreB - scoreA;
        });
        const top20Ids = new Set(sorted.slice(0, 20).map(i => i.id));
        
        activeService.items.forEach(item => { 
          item.isTop20 = top20Ids.has(item.id); 
        });
        renderTop20Grid();
        showToast("Top 20 selecionadas pela IA com base na nitidez!");
      }
    }

    function toggleSelectAllPhotos(selectAll) {
      if (activeService && activeService.items) {
        activeService.items.forEach(item => item.isTop20 = selectAll);
        renderTop20Grid();
      }
    }

    function setSmartCropMode(mode) {
      smartCropMode = mode;
      const b45 = document.getElementById('cropBtn45');
      const b11 = document.getElementById('cropBtn11');
      const bOff = document.getElementById('cropBtnOff');
      const box = document.getElementById('smartCropGuideBox');

      [b45, b11, bOff].forEach(b => {
        b.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium text-[11px]";
      });

      if (mode === '4:5') {
        b45.className = "px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px]";
        box.style.display = 'block'; box.classList.remove('hidden');
        box.style.left = '20%'; box.style.top = '5%'; box.style.width = '60%'; box.style.height = '90%';
        showToast("Smart Crop 4:5 Vertical ativado!");
      } else if (mode === '1:1') {
        b11.className = "px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px]";
        box.style.display = 'block'; box.classList.remove('hidden');
        box.style.left = '15%'; box.style.top = '10%'; box.style.width = '70%'; box.style.height = '80%';
        showToast("Smart Crop 1:1 Quadrado ativado!");
      } else {
        bOff.className = "px-2.5 py-1 rounded-lg bg-church-800 text-white font-bold text-[11px]";
        box.style.display = 'none'; box.classList.add('hidden');
      }
    }

    // ================= SERVICES & PHOTO STORAGE (INDEXEDDB + BACKUP + CLOUD SYNC) =================

    async function loadStoredServices() {
      try {
        let loaded = await dbLoadAllServices();

        // Safety fallback: if indexedDB was empty or had errors, check local backup
        if (!loaded || loaded.length === 0) {
          try {
            const rawBackup = localStorage.getItem('CHURCHPHOTO_SERVICES_BACKUP');
            if (rawBackup) {
              const parsed = JSON.parse(rawBackup);
              if (Array.isArray(parsed) && parsed.length > 0) {
                loaded = parsed;
              }
            }
          } catch(e) {}
        }

        // Check legacy localStorage migration if still empty
        if (!loaded || loaded.length === 0) {
          const guestStored = localStorage.getItem('CHURCHPHOTO_SERVICES_GUEST') || localStorage.getItem('CHURCHPHOTO_SERVICES');
          if (guestStored) {
            try {
              const legacy = JSON.parse(guestStored);
              if (Array.isArray(legacy) && legacy.length > 0) {
                loaded = legacy;
              }
            } catch(e) {}
          }
        }

        if (loaded && loaded.length > 0) {
          churchServices = loaded;
          if (currentUser) {
            for (const s of churchServices) {
              if (!s.userId || s.userId === 'guest') {
                s.userId = currentUser.id;
                await dbSaveService(s);
              }
            }
          }
        }
      } catch (e) {
        console.error("loadStoredServices error:", e);
      }

      // Synchronize with Supabase cloud database if user is logged in
      if (currentUser && currentUser.id && supabaseClient) {
        try {
          await syncServicesWithSupabaseCloud();
          await syncPresetsWithSupabaseCloud();
        } catch(e) {}
      }

      renderServicesGrid();
      renderSidebarRecentServices();
    }

    async function saveServicesToStorage() {
      if (churchServices && churchServices.length > 0) {
        // 1. Save full data to IndexedDB
        for (const s of churchServices) {
          if (currentUser) s.userId = currentUser.id;
          await dbSaveService(s);
        }

        // 2. Save lightweight metadata backup to localStorage (safety net)
        try {
          const lightweightServices = churchServices.map(s => ({
            id: s.id,
            userId: s.userId,
            teamId: s.teamId,
            title: s.title,
            date: s.date,
            presetName: s.presetName,
            createdAt: s.createdAt,
            items: (s.items || []).map(i => ({
              id: i.id,
              fileName: i.fileName,
              status: i.status,
              isTop20: i.isTop20,
              currentParams: i.currentParams,
              metadata: i.metadata,
              previewUrl: (i.previewUrl && i.previewUrl.length < 50000) ? i.previewUrl : ''
            }))
          }));
          localStorage.setItem('CHURCHPHOTO_SERVICES_BACKUP', JSON.stringify(lightweightServices));
        } catch(e) {}

        // 3. Save to Supabase Cloud if online and logged in
        if (currentUser && currentUser.id && supabaseClient) {
          for (const s of churchServices) {
            saveServiceToSupabaseCloud(s).catch(() => {});
          }
        }
      }
      renderSidebarRecentServices();
    }

    async function clearDeviceDataPrompt() {
      if (confirm("Deseja limpar todos os cultos e fotos armazenados neste dispositivo?")) {
        await dbClearAll();
        localStorage.removeItem('CHURCHPHOTO_SERVICES');
        localStorage.removeItem('CHURCHPHOTO_SERVICES_GUEST');
        churchServices = [];
        activeService = null;
        queue = [];
        activeItem = null;
        renderServicesGrid();
        renderSidebarRecentServices();
        renderThumbnails();
        showToast("Cache e cultos do dispositivo limpos com sucesso!");
      }
    }

    function renderSidebarRecentServices() {
      const container = document.getElementById('sideRecentServicesList');
      const sideServicesCount = document.getElementById('sideServicesCountBadge');
      const sidePhotosCount = document.getElementById('sidePhotosCountBadge');

      if (sideServicesCount) sideServicesCount.textContent = churchServices.length;
      
      let totalPhotos = 0;
      churchServices.forEach(s => totalPhotos += (s.items ? s.items.length : 0));
      if (sidePhotosCount) sidePhotosCount.textContent = `${totalPhotos} fotos`;

      if (!churchServices || churchServices.length === 0) {
        container.innerHTML = `<span class="sidebar-text text-[11px] text-slate-500 px-2 py-1 block">Nenhum culto salvo</span>`;
        return;
      }

      container.innerHTML = churchServices.slice(0, 5).map(s => {
        const isCurrentActive = activeService && activeService.id === s.id;
        return `
          <button onclick="openServiceInStudio('${s.id}')" class="sidebar-item w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left text-xs transition-colors cursor-pointer ${
            isCurrentActive ? 'bg-church-800 text-blue-400 font-bold' : 'text-slate-400 hover:text-slate-200 hover:bg-church-800/40'
          }">
            <div class="flex items-center gap-2 min-w-0">
              <i class="fa-solid fa-church text-[11px] w-4 text-center text-slate-500"></i>
              <span class="sidebar-text truncate max-w-[130px]">${s.title}</span>
            </div>
            <span class="sidebar-badge text-[9px] font-mono text-slate-500">${s.items ? s.items.length : 0}</span>
          </button>
        `;
      }).join('');
    }

    function renderServicesGrid() {
      const container = document.getElementById('servicesListContainer');
      const emptyPrompt = document.getElementById('emptyServicesPrompt');
      const countBadge = document.getElementById('servicesCountBadge');

      countBadge.textContent = `${churchServices.length} culto${churchServices.length === 1 ? '' : 's'}`;

      if (!churchServices || churchServices.length === 0) {
        container.style.display = 'none';
        emptyPrompt.style.display = 'flex';
        emptyPrompt.classList.remove('hidden');
        return;
      }

      emptyPrompt.style.display = 'none';
      emptyPrompt.classList.add('hidden');
      container.style.display = 'grid';

      container.innerHTML = churchServices.map(srv => {
        const totalPhotos = srv.items ? srv.items.length : 0;
        const completedCount = srv.items ? srv.items.filter(i => i.status === 'completed').length : 0;
        const progressPct = totalPhotos > 0 ? Math.round((completedCount / totalPhotos) * 100) : 0;

        const previewThumbs = (srv.items || []).slice(0, 4).map(i => `
          <div class="w-12 h-12 rounded-lg overflow-hidden bg-church-950 border border-church-800 shrink-0">
            <img src="${i.processedBase64 || i.previewUrl}" class="w-full h-full object-cover">
          </div>
        `).join('');

        return `
          <div class="rounded-2xl sm:rounded-3xl bg-church-900 border border-church-800 hover:border-blue-500/50 p-4 sm:p-5 shadow-xl flex flex-col justify-between transition-all group">
            <div>
              <div class="flex items-start justify-between gap-2 mb-2">
                <div>
                  <h4 class="text-sm sm:text-base font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-1">
                    ${srv.title}
                  </h4>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                      <i class="fa-regular fa-calendar text-[10px]"></i> ${srv.date}
                    </span>
                    <span class="px-1.5 py-0.2 rounded bg-church-950 text-amber-400 border border-amber-400/20 text-[9px] font-mono">
                      ${srv.presetName || 'Luz Quente'}
                    </span>
                  </div>
                </div>

                <button onclick="deleteChurchService('${srv.id}', event)" class="text-slate-500 hover:text-red-400 p-1.5 rounded-lg transition-colors cursor-pointer" title="Excluir Culto">
                  <i class="fa-solid fa-trash-can text-xs"></i>
                </button>
              </div>

              <div class="flex items-center gap-1.5 my-3">
                ${previewThumbs}
                ${totalPhotos > 4 ? `<span class="w-12 h-12 rounded-lg bg-church-950 border border-church-800 flex items-center justify-center text-[10px] font-bold text-slate-400">+${totalPhotos - 4}</span>` : ''}
              </div>

              <div class="flex items-center justify-between text-[11px] mb-1">
                <span class="text-slate-400">${totalPhotos} foto${totalPhotos === 1 ? '' : 's'} no lote</span>
                <span class="font-bold ${progressPct === 100 ? 'text-emerald-400' : 'text-blue-400'}">${progressPct}% Tratado</span>
              </div>
              <div class="w-full h-1.5 rounded-full bg-church-950 overflow-hidden mb-4">
                <div class="h-full bg-gradient-to-r from-blue-600 to-emerald-500 transition-all duration-300" style="width: ${progressPct}%"></div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2 pt-2 border-t border-church-800">
              <button onclick="openServiceInFunnel('${srv.id}')" class="py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs font-bold flex items-center justify-center gap-1.5 shadow transition-all cursor-pointer">
                <i class="fa-solid fa-filter text-xs text-amber-300"></i>
                <span>Funil IA</span>
              </button>

              <button onclick="downloadServiceZip('${srv.id}')" class="py-2.5 px-3 rounded-xl bg-church-800 hover:bg-church-700 active:scale-95 border border-church-700 text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
                <i class="fa-solid fa-file-zipper text-emerald-400 text-xs"></i>
                <span>Baixar (.ZIP)</span>
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function openCreateServiceModal() {
      const modal = document.getElementById('createServiceModal');
      document.getElementById('newServiceTitle').value = '';
      document.getElementById('modalFileStatusText').textContent = 'Toque aqui para escolher as fotos da galeria';
      pendingModalFiles = [];
      modal.style.display = 'flex';
      modal.classList.remove('hidden');
    }

    function closeCreateServiceModal() {
      const modal = document.getElementById('createServiceModal');
      modal.style.display = 'none';
      modal.classList.add('hidden');
    }

    function setServiceSuggestion(text) {
      document.getElementById('newServiceTitle').value = text;
    }

    function handleModalFilesSelected(files) {
      if (files && files.length > 0) {
        pendingModalFiles = Array.from(files);
        document.getElementById('modalFileStatusText').innerHTML = `<span class="text-emerald-400 font-bold"><i class="fa-solid fa-check"></i> ${files.length} foto(s) carregada(s)</span>`;
      }
    }

    async function handleCreateServiceSubmit(e) {
      e.preventDefault();
      const title = document.getElementById('newServiceTitle').value.trim();
      const date = document.getElementById('newServiceDate').value;
      if (!title) return;

      const newService = {
        id: 'srv_' + Date.now(),
        userId: currentUser ? currentUser.id : 'guest',
        teamId: activeTeam ? activeTeam.id : 'team_default',
        title: title,
        date: date || new Date().toLocaleDateString('pt-BR'),
        presetName: activeTeam && activeTeam.presets && activeTeam.presets[0] ? activeTeam.presets[0].name : 'Luz Quente Natural',
        items: [],
        createdAt: new Date().toISOString()
      };

      if (pendingModalFiles.length > 0) {
        document.getElementById('modalFileStatusText').innerHTML = `<span class="text-amber-400 font-bold"><i class="fa-solid fa-spinner fa-spin"></i> IA analisando e classificando ${pendingModalFiles.length} foto(s)...</span>`;
        for (const file of pendingModalFiles) {
          const dataUrl = await fileToDataUrl(file);
          const aiData = await analyzeImageReal(file);
          
          newService.items.push({
            id: Date.now() + '_' + Math.random().toString(36).substr(2, 6),
            fileName: file.name,
            previewUrl: dataUrl,
            status: 'idle',
            processedBase64: null,
            originalBase64: dataUrl,
            cachedImg: null,
            metadata: aiData,
            analysis: null,
            isTop20: true,
            currentParams: null
          });
        }
      }

      churchServices.unshift(newService);
      await dbSaveService(newService);
      await saveServicesToStorage();
      renderServicesGrid();
      renderSidebarRecentServices();
      closeCreateServiceModal();
      showToast(`Culto "${title}" salvo com sucesso!`);

      openServiceInFunnel(newService.id);
    }

    function openServiceInFunnel(serviceId) {
      const srv = churchServices.find(s => s.id === serviceId);
      if (!srv) return;

      activeService = srv;
      queue = srv.items || [];

      document.getElementById('studioServiceTitle').textContent = srv.title;
      document.getElementById('studioServiceDate').textContent = `${srv.date} · ${queue.length} fotos`;

      renderThumbnails();
      switchMainView('funnel');
    }

    function openServiceInStudio(serviceId) {
      const srv = churchServices.find(s => s.id === serviceId);
      if (!srv) return;

      activeService = srv;
      queue = srv.items || [];

      document.getElementById('studioServiceTitle').textContent = srv.title;
      document.getElementById('studioServiceDate').textContent = `${srv.date} · ${queue.length} fotos`;

      renderThumbnails();
      switchMainView('studio');

      if (queue.length > 0) {
        selectQueueItem(queue[0].id);
        processAllInQueue();
      }
    }

    async function deleteChurchService(serviceId, event) {
      if (event) event.stopPropagation();
      if (confirm("Tem certeza que deseja excluir este culto e suas fotos?")) {
        await dbDeleteService(serviceId);
        deleteServiceFromSupabaseCloud(serviceId).catch(() => {});
        churchServices = churchServices.filter(s => s.id !== serviceId);
        await saveServicesToStorage();
        renderServicesGrid();
        renderSidebarRecentServices();
        showToast("Culto excluído com sucesso.");
      }
    }

    function setupAddMorePhotosInput() {
      const input = document.getElementById('addMorePhotosInput');
      if (input) {
        input.addEventListener('change', async (e) => {
          if (e.target.files && e.target.files.length > 0 && activeService) {
            showToast("Analisando novas fotos com IA...");
            for (const file of Array.from(e.target.files)) {
              const dataUrl = await fileToDataUrl(file);
              const aiData = await analyzeImageReal(file);
              const item = {
                id: Date.now() + '_' + Math.random().toString(36).substr(2, 6),
                fileName: file.name,
                previewUrl: dataUrl,
                status: 'idle',
                processedBase64: null,
                originalBase64: dataUrl,
                cachedImg: null,
                metadata: aiData,
                analysis: null,
                isTop20: true,
                currentParams: null
              };
              queue.push(item);
              activeService.items.push(item);
            }

            await dbSaveService(activeService);
            await saveServicesToStorage();
            renderThumbnails();
            renderSidebarRecentServices();
            showToast(`${e.target.files.length} foto(s) adicionada(s)!`);
            processAllInQueue();
            e.target.value = '';
          }
        });
      }
    }

    // ================= BATCH ZIP EXPORT =================

    async function downloadActiveServiceZip() {
      if (activeService) {
        await downloadServiceZip(activeService.id);
      }
    }

    async function downloadServiceZip(serviceId) {
      const srv = churchServices.find(s => s.id === serviceId);
      if (!srv || !srv.items || srv.items.length === 0) {
        showToast("Nenhuma foto disponível para download.");
        return;
      }

      showToast("Compactando fotos HD tratadas em ZIP...");

      try {
        const zip = new JSZip();
        const folderName = srv.title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
        const zipFolder = zip.folder(folderName);

        for (let i = 0; i < srv.items.length; i++) {
          const item = srv.items[i];
          let base64Data = item.processedBase64;

          if (!base64Data) {
            const img = item.cachedImg || new Image();
            if (!item.cachedImg) img.src = item.previewUrl;
            const params = item.currentParams || item.analysis || (activeTeam.presets && activeTeam.presets[0] ? activeTeam.presets[0].params : DEFAULT_TEAM_PRESETS[0].params);
            const res = processImageClientSideFast(img, params, true);
            base64Data = res.base64;
          }

          const cleanBase64 = base64Data.replace(/^data:image\/(png|jpeg|jpg);base64,/, '');
          const fileName = `foto_${(i + 1).toString().padStart(2, '0')}_dslr_hd.jpg`;
          zipFolder.file(fileName, cleanBase64, { base64: true });
        }

        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const downloadUrl = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${folderName}_hd_dslr.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);

        showToast("Download do lote ZIP concluído!");
      } catch (err) {
        console.error("Erro ZIP:", err);
        showToast("Erro ao compactar: " + err.message);
      }
    }

    function showToast(msg) {
      const toast = document.getElementById('toastNotification');
      const text = document.getElementById('toastText');
      if (toast && text) {
        text.textContent = msg;
        toast.style.pointerEvents = 'auto';
        toast.classList.remove('-translate-y-10', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
        setTimeout(() => {
          toast.classList.remove('translate-y-0', 'opacity-100');
          toast.classList.add('-translate-y-10', 'opacity-0');
          toast.style.pointerEvents = 'none';
        }, 3200);
      }
    }

    // ================= STUDIO THUMBNAILS & PHOTO PROCESSING =================

    function renderThumbnails() {
      const container = document.getElementById('thumbnailsList');
      if (!queue || queue.length === 0) {
        container.innerHTML = `<span class="text-xs text-slate-500 py-2">Nenhuma foto adicionada.</span>`;
        return;
      }

      container.innerHTML = queue.map(item => {
        const isSelected = activeItem && activeItem.id === item.id;
        return `
          <div onclick="selectQueueItem('${item.id}')" class="relative shrink-0 w-14 h-14 rounded-xl overflow-hidden cursor-pointer border-2 transition-all ${
            isSelected ? 'border-blue-500 scale-105 shadow-md shadow-blue-500/30' : 'border-church-800 opacity-70 hover:opacity-100'
          }">
            <img src="${item.processedBase64 || item.previewUrl}" class="w-full h-full object-cover">
            ${item.status === 'completed' ? '<span class="absolute top-0.5 right-0.5 w-2 h-2 rounded-full bg-emerald-400"></span>' : ''}
            ${item.status === 'analyzing' ? '<span class="absolute inset-0 bg-blue-900/60 flex items-center justify-center"><i class="fa-solid fa-spinner animate-spin text-white text-xs"></i></span>' : ''}
          </div>
        `;
      }).join('');
    }

    function selectQueueItem(id) {
      activeItem = queue.find(i => i.id === id);
      renderThumbnails();
      if (!activeItem) return;

      document.getElementById('activePhotoTitle').textContent = activeItem.fileName || activeItem.file?.name || 'Foto do Culto';

      if (activeItem.status === 'completed' && activeItem.processedBase64) {
        showProcessedViewer(activeItem);
      } else {
        processItem(id, false);
      }
    }

    function showProcessedViewer(item) {
      document.getElementById('emptyPrompt').style.display = 'none';
      document.getElementById('emptyPrompt').classList.add('hidden');
      document.getElementById('processingLoader').style.display = 'none';
      document.getElementById('processingLoader').classList.add('hidden');
      document.getElementById('parametersPanel').style.display = 'block';
      document.getElementById('parametersPanel').classList.remove('hidden');
      document.getElementById('downloadBtn').disabled = false;

      document.getElementById('imgAfter').src = item.processedBase64;
      document.getElementById('imgBefore').src = item.originalBase64 || item.previewUrl;
      document.getElementById('imgSideBefore').src = item.originalBase64 || item.previewUrl;
      document.getElementById('imgSideAfter').src = item.processedBase64;

      if (viewerMode === 'slider') {
        document.getElementById('sliderWrapper').style.display = 'block';
        document.getElementById('sliderWrapper').classList.remove('hidden');
        document.getElementById('sideBySideWrapper').style.display = 'none';
        document.getElementById('sideBySideWrapper').classList.add('hidden');
      } else {
        document.getElementById('sliderWrapper').style.display = 'none';
        document.getElementById('sliderWrapper').classList.add('hidden');
        document.getElementById('sideBySideWrapper').style.display = 'grid';
        document.getElementById('sideBySideWrapper').classList.remove('hidden');
      }

      if (item.metadata) {
        document.getElementById('resolutionBadge').textContent = `${item.metadata.width}x${item.metadata.height}px | ${item.metadata.executionTime || item.metadata.execution_time_ms}ms`;
      }

      const p = item.currentParams || item.analysis;
      if (p) {
        document.getElementById('analysisSummary').textContent = p.analysis_summary || 'Calibração DSLR concluída com sucesso.';
        document.getElementById('lightingTag').textContent = p.detected_lighting_condition || 'Iluminação de Palco';
        document.getElementById('sceneTag').textContent = p.scene_moment || 'Culto / Palco';
        document.getElementById('fStopTag').textContent = `f/${p.f_stop_simulation || 2.8} Bokeh`;

        focalPoint.x = p.focal_point_x || 0.50;
        focalPoint.y = p.focal_point_y || 0.40;
        currentFStop = p.f_stop_simulation || 2.8;

        updateFocusReticleUI();

        document.getElementById('param_exposure').value = p.exposure_compensation;
        document.getElementById('val_exposure').textContent = `${p.exposure_compensation > 0 ? '+' : ''}${p.exposure_compensation}`;
        document.getElementById('param_kelvin').value = p.temperature_kelvin;
        document.getElementById('val_kelvin').textContent = `${p.temperature_kelvin}K`;
        document.getElementById('param_tint').value = p.tint || 0.0;
        document.getElementById('val_tint').textContent = `${p.tint || 0.0}`;
        document.getElementById('param_contrast').value = p.contrast || 1.10;
        document.getElementById('val_contrast').textContent = `${(p.contrast || 1.10).toFixed(2)}x`;
        document.getElementById('param_highlights').value = p.highlights || 0.0;
        document.getElementById('val_highlights').textContent = `${Math.round((p.highlights || 0.0)*100)}%`;
        document.getElementById('param_shadows').value = p.shadows || 0.0;
        document.getElementById('val_shadows').textContent = `${Math.round((p.shadows || 0.0)*100)}%`;
        document.getElementById('param_whites').value = p.whites || 0.0;
        document.getElementById('val_whites').textContent = `${Math.round((p.whites || 0.0)*100)}%`;
        document.getElementById('param_blacks').value = p.blacks || 0.0;
        document.getElementById('val_blacks').textContent = `${Math.round((p.blacks || 0.0)*100)}%`;
        document.getElementById('param_saturation').value = p.saturation !== undefined ? p.saturation : 1.0;
        document.getElementById('val_saturation').textContent = `${Math.round((p.saturation !== undefined ? p.saturation : 1.0)*100)}%`;
        document.getElementById('param_clarity').value = p.clarity || 0.0;
        document.getElementById('val_clarity').textContent = `${Math.round((p.clarity || 0.0)*100)}%`;
        document.getElementById('param_dehaze').value = p.dehaze || 0.0;
        document.getElementById('val_dehaze').textContent = `${Math.round((p.dehaze || 0.0)*100)}%`;
        document.getElementById('param_vignette').value = p.vignette || 0.0;
        document.getElementById('val_vignette').textContent = `${Math.round((p.vignette || 0.0)*100)}%`;
      }
    }

    async function processItem(id, isBatch = false) {
      const item = queue.find(i => i.id === id);
      if (!item) return;

      item.status = 'analyzing';
      renderThumbnails();

      if (!item.cachedImg) {
        const img = new Image();
        img.src = item.previewUrl;
        await new Promise(resolve => { 
          img.onload = resolve; 
          img.onerror = resolve; 
        });
        item.cachedImg = img;
      }

      const params = item.currentParams || analyzeImageHeuristic(item.cachedImg);
      if (isBatch) params.f_stop_simulation = 8.0;

      item.analysis = params;
      item.currentParams = params;

      const result = processImageClientSideFast(item.cachedImg, params, false);
      item.status = 'completed';
      item.processedBase64 = result.base64;
      item.originalBase64 = item.previewUrl;
      item.metadata = { width: result.width, height: result.height, executionTime: result.executionTime };

      saveServicesToStorage();
      renderThumbnails();
      if (activeItem && activeItem.id === id) selectQueueItem(id);
    }

    async function processAllInQueue() {
      const btn = document.getElementById('batchProcessBtn');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-xs"></i> Processando...`;
      }

      for (const item of queue) {
        if (item.status !== 'completed') await processItem(item.id, true);
      }

      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-check text-emerald-300 text-xs"></i> Lote Concluído`;
        setTimeout(() => { btn.innerHTML = `<i class="fa-solid fa-bolt text-amber-300 text-xs"></i> Processar Lote`; }, 2500);
      }

      renderServicesGrid();
      renderSidebarRecentServices();
    }

    // ================= ULTRA-FAST LUT ACCELERATED ENGINE =================

    function kelvinToRGBMultipliers(kelvin) {
      let temp = Math.max(2500, Math.min(9000, kelvin)) / 100;
      let r, g, b;
      if (temp <= 66) {
        r = 255;
        g = 99.4708025861 * Math.log(temp) - 161.1195681661;
      } else {
        r = 329.698727446 * Math.pow(temp - 60, -0.1332047592);
        g = 288.1221695283 * Math.pow(temp - 60, -0.0755148492);
      }
      if (temp >= 66) b = 255;
      else if (temp <= 19) b = 0;
      else b = 138.5177312231 * Math.log(temp - 10) - 305.0447927307;

      return {
        r: 1.0 + ((Math.max(0, Math.min(255, r)) / 255.0) - 1.0) * 0.55,
        g: 1.0 + ((Math.max(0, Math.min(255, g)) / 243.6) - 1.0) * 0.55,
        b: 1.0 + ((Math.max(0, Math.min(255, b)) / 232.4) - 1.0) * 0.55,
      };
    }

    function processImageClientSideFast(imgElement, params, isFullResolution = false) {
      const startTime = performance.now();
      const origW = imgElement.naturalWidth || imgElement.width || 800;
      const origH = imgElement.naturalHeight || imgElement.height || 600;

      let targetW = origW;
      let targetH = origH;
      if (!isFullResolution) {
        const maxDim = 1200;
        if (Math.max(origW, origH) > maxDim) {
          const ratio = maxDim / Math.max(origW, origH);
          targetW = Math.round(origW * ratio);
          targetH = Math.round(origH * ratio);
        }
      }

      fastCanvas.width = targetW;
      fastCanvas.height = targetH;
      fastCtx.drawImage(imgElement, 0, 0, targetW, targetH);

      const imgData = fastCtx.getImageData(0, 0, targetW, targetH);
      const data = imgData.data;

      // --- 1. LIGHTROOM MATH ALGORITHMS ---
      const expMult = Math.pow(2.0, params.exposure_compensation || 0.0);
      
      // Kelvin and Tint to RGB White Balance
      const kelvin = params.temperature_kelvin || 5500;
      const tint = params.tint || 0.0;
      let temp = kelvin / 100.0;
      let rWB = temp <= 66 ? 255 : Math.max(0, Math.min(255, 329.6987 * Math.pow(temp - 60, -0.1332)));
      let gWB = temp <= 66 ? Math.max(0, Math.min(255, 99.4708 * Math.log(temp) - 161.1195)) : Math.max(0, Math.min(255, 288.1221 * Math.pow(temp - 60, -0.0755)));
      let bWB = temp >= 66 ? 255 : (temp <= 19 ? 0 : Math.max(0, Math.min(255, 138.5177 * Math.log(temp - 10) - 305.0448)));
      // Apply Tint on Green Channel
      gWB = Math.max(0, Math.min(255, gWB - tint));
      const wb = { r: rWB/255.0, g: gWB/255.0, b: bWB/255.0 };

      const contrast = params.contrast || 1.0;
      const highlights = params.highlights || 0.0; // -1.0 to 1.0
      const shadows = params.shadows || 0.0; // -1.0 to 1.0
      const whites = params.whites || 0.0; // -1.0 to 1.0
      const blacks = params.blacks || 0.0; // -1.0 to 1.0
      
      const sat = params.saturation || 1.0;
      const vib = params.vibrance || 1.0;
      const clarity = params.clarity || 0.0;
      const dehaze = params.dehaze || 0.0;
      const vignette = params.vignette || 0.0;

      // 1D LUT for Tone Mapping (Exposure, WB, Tone Curve)
      const lutR = new Uint8ClampedArray(256);
      const lutG = new Uint8ClampedArray(256);
      const lutB = new Uint8ClampedArray(256);

      for (let v = 0; v < 256; v++) {
        let norm = v / 255.0;
        
        let rVal = norm * expMult * wb.r;
        let gVal = norm * expMult * wb.g;
        let bVal = norm * expMult * wb.b;

        // Tone Curve adjustments based on luminance regions
        const processTone = (val) => {
          let n = val;
          // Shadows (Bottom 40%)
          if (shadows !== 0 && n < 0.4) {
             let mask = Math.pow(1.0 - (n / 0.4), 1.5);
             n = n + (shadows * 0.25 * mask);
          }
          // Highlights (Top 40%)
          if (highlights !== 0 && n > 0.6) {
             let mask = Math.pow((n - 0.6) / 0.4, 1.5);
             n = n + (highlights * 0.25 * mask);
          }
          // Blacks (Bottom 15%)
          if (blacks !== 0 && n < 0.15) {
             let mask = Math.pow(1.0 - (n / 0.15), 2.0);
             n = n + (blacks * 0.15 * mask);
          }
          // Whites (Top 15%)
          if (whites !== 0 && n > 0.85) {
             let mask = Math.pow((n - 0.85) / 0.15, 2.0);
             n = n + (whites * 0.15 * mask);
          }
          // Contrast Pivot
          if (Math.abs(contrast - 1.0) > 0.01) {
             n = (n - 0.5) * contrast + 0.5;
          }
          // Clarity Fake (Midtone S-Curve)
          if (clarity !== 0 && n > 0.2 && n < 0.8) {
             let midMask = Math.sin((n - 0.2) / 0.6 * Math.PI); // peak at 0.5
             let sCurve = (n - 0.5) * (1.0 + clarity * 0.5) + 0.5;
             n = n * (1.0 - midMask) + sCurve * midMask;
          }
          return Math.max(0, Math.min(1, n));
        };

        lutR[v] = Math.max(0, Math.min(255, Math.round(processTone(rVal) * 255)));
        lutG[v] = Math.max(0, Math.min(255, Math.round(processTone(gVal) * 255)));
        lutB[v] = Math.max(0, Math.min(255, Math.round(processTone(bVal) * 255)));
      }

      // --- 2. PER-PIXEL PROCESSING (Colors, Dehaze, Vignette) ---
      const doDehaze = dehaze !== 0;
      const dehazeFactor = dehaze * 0.15;
      const doSatVib = Math.abs(sat - 1.0) > 0.01 || Math.abs(vib - 1.0) > 0.01;
      const doVig = vignette !== 0;
      
      const len = data.length;
      
      if (!doDehaze && !doSatVib && !doVig) {
        // FASTEST PATH: Only LUT (Exposure, Contrast, WB, Tone Curve, Clarity)
        for (let i = 0; i < len; i += 4) {
          data[i] = lutR[data[i]];
          data[i + 1] = lutG[data[i + 1]];
          data[i + 2] = lutB[data[i + 2]];
        }
      } else if (!doVig) {
        // FAST 1D PATH: Color grading but no spatial vignette
        for (let i = 0; i < len; i += 4) {
          let r = lutR[data[i]];
          let g = lutG[data[i + 1]];
          let b = lutB[data[i + 2]];

          if (doDehaze) {
            let darkChannel = Math.min(r, Math.min(g, b)) / 255.0;
            r = Math.max(0, r - dehazeFactor * 255 * (1.0 - darkChannel));
            g = Math.max(0, g - dehazeFactor * 255 * (1.0 - darkChannel));
            b = Math.max(0, b - dehazeFactor * 255 * (1.0 - darkChannel));
            r = Math.min(255, r * (1.0 + dehazeFactor));
            g = Math.min(255, g * (1.0 + dehazeFactor));
            b = Math.min(255, b * (1.0 + dehazeFactor));
          }

          if (doSatVib) {
            let maxC = Math.max(r, Math.max(g, b));
            let minC = Math.min(r, Math.min(g, b));
            let saturationCurrent = maxC === 0 ? 0 : (maxC - minC) / maxC;
            let vibFactor = vib > 1.0 ? vib * (1.0 - saturationCurrent) : vib; 
            let mean = (r + g + b) / 3.0;
            let finalFactor = sat * vibFactor;
            r = mean + (r - mean) * finalFactor;
            g = mean + (g - mean) * finalFactor;
            b = mean + (b - mean) * finalFactor;
          }

          data[i] = r; data[i + 1] = g; data[i + 2] = b;
        }
      } else {
        // FULL 2D PATH: Vignette requires X/Y coordinates
        const centerX = targetW / 2;
        const centerY = targetH / 2;
        const maxDist = Math.sqrt(centerX * centerX + centerY * centerY);

        for (let y = 0; y < targetH; y++) {
          for (let x = 0; x < targetW; x++) {
            let i = (y * targetW + x) * 4;
            
            let r = lutR[data[i]];
            let g = lutG[data[i + 1]];
            let b = lutB[data[i + 2]];

            if (doDehaze) {
              let darkChannel = Math.min(r, Math.min(g, b)) / 255.0;
              r = Math.max(0, r - dehazeFactor * 255 * (1.0 - darkChannel));
              g = Math.max(0, g - dehazeFactor * 255 * (1.0 - darkChannel));
              b = Math.max(0, b - dehazeFactor * 255 * (1.0 - darkChannel));
              r = Math.min(255, r * (1.0 + dehazeFactor));
              g = Math.min(255, g * (1.0 + dehazeFactor));
              b = Math.min(255, b * (1.0 + dehazeFactor));
            }

            if (doSatVib) {
              let maxC = Math.max(r, Math.max(g, b));
              let minC = Math.min(r, Math.min(g, b));
              let saturationCurrent = maxC === 0 ? 0 : (maxC - minC) / maxC;
              let vibFactor = vib > 1.0 ? vib * (1.0 - saturationCurrent) : vib; 
              let mean = (r + g + b) / 3.0;
              let finalFactor = sat * vibFactor;
              r = mean + (r - mean) * finalFactor;
              g = mean + (g - mean) * finalFactor;
              b = mean + (b - mean) * finalFactor;
            }

            let dx = x - centerX;
            let dy = y - centerY;
            let dist = Math.sqrt(dx*dx + dy*dy) / maxDist;
            let vigMult = 1.0 + (vignette * Math.pow(dist, 2.0));
            r = Math.min(255, r * vigMult);
            g = Math.min(255, g * vigMult);
            b = Math.min(255, b * vigMult);

            data[i] = r; data[i + 1] = g; data[i + 2] = b;
          }
        }
      }

      fastCtx.putImageData(imgData, 0, 0);

      return {
        base64: fastCanvas.toDataURL('image/jpeg', isFullResolution ? 0.94 : 0.88),
        width: origW,
        height: origH,
        executionTime: Math.round(performance.now() - startTime)
      };
    }

    function analyzeImageHeuristic(imgElement) {
      if (!imgElement || !imgElement.width) return activeTeam.presets[0].params;

      const cvs = document.createElement('canvas');
      cvs.width = 16;
      cvs.height = 16;
      const ctx = cvs.getContext('2d');
      ctx.drawImage(imgElement, 0, 0, 16, 16);
      const data = ctx.getImageData(0, 0, 16, 16).data;

      let totalBrightness = 0;
      let totalR = 0, totalG = 0, totalB = 0;

      for(let i = 0; i < data.length; i += 4) {
        let r = data[i], g = data[i+1], b = data[i+2];
        totalR += r; totalG += g; totalB += b;
        totalBrightness += (r * 0.299 + g * 0.587 + b * 0.114);
      }

      const pixelCount = 256;
      const avgBrightness = totalBrightness / pixelCount;
      const avgR = totalR / pixelCount;
      const avgB = totalB / pixelCount;

      let chosenId = 'natural_skin_tone';

      if (avgR > avgB + 80 || avgB > avgR + 80) {
        chosenId = 'stage_light_fix';
      } else if (avgBrightness < 60) {
        chosenId = 'low_light_noise_control';
      } else if (avgBrightness > 160) {
        chosenId = 'clean_bright';
      } else if (avgR > avgB + 40 && avgBrightness > 100) {
        chosenId = 'golden_hour_glow';
      } else if (avgBrightness < 100 && avgR > avgB + 20) {
        chosenId = 'warm_worship';
      } else if (avgBrightness < 90) {
        chosenId = 'moody_stage';
      }

      const p = (activeTeam.presets || []).find(x => x.id === chosenId);
      
      const suggestedParams = p ? { ...p.params } : (activeTeam.presets[0] ? activeTeam.presets[0].params : {});
      return { ...suggestedParams, _ai_suggested_id: chosenId };
    }

    // ================= INTERACTION CONTROLS =================

    function switchControlTab(tabIdx) {
      currentTab = tabIdx;
      for (let i = 1; i <= 2; i++) {
        const btn = document.getElementById(`tabBtn${i}`);
        const content = document.getElementById(`tabContent${i}`);
        if (i === tabIdx) {
          if (btn) btn.className = 'px-3 sm:px-4 py-2 text-xs font-bold border-b-2 border-blue-500 text-blue-400 flex items-center gap-1.5 transition-all';
          if (content) { content.style.display = 'flex'; content.classList.remove('hidden'); }
        } else {
          if (btn) btn.className = 'px-3 sm:px-4 py-2 text-xs font-semibold border-b-2 border-transparent text-slate-400 hover:text-white flex items-center gap-1.5 transition-all';
          if (content) { content.style.display = 'none'; content.classList.add('hidden'); }
        }
      }
    }

    function handleViewportClick(event) {
      if (!activeItem || activeItem.status !== 'completed' || isDragging) return;
      const rect = document.getElementById('viewport').getBoundingClientRect();
      focalPoint.x = Math.max(0.1, Math.min(0.9, (event.clientX - rect.left) / rect.width));
      focalPoint.y = Math.max(0.1, Math.min(0.9, (event.clientY - rect.top) / rect.height));
      updateFocusReticleUI();
      applyCurrentManualParams();
    }

    function updateFocusReticleUI() {
      const reticle = document.getElementById('focusReticle');
      if (reticle) {
        reticle.style.display = 'block'; reticle.classList.remove('hidden');
        reticle.style.left = `${(focalPoint.x * 100).toFixed(1)}%`;
        reticle.style.top = `${(focalPoint.y * 100).toFixed(1)}%`;
      }
    }

    function resetFocalCenter() {
      focalPoint.x = 0.50; focalPoint.y = 0.40;
      updateFocusReticleUI();
      applyCurrentManualParams();
    }

    function setFStop(val) {
      currentFStop = val;
      document.querySelectorAll('.fstop-btn').forEach(btn => {
        btn.className = Math.abs(parseFloat(btn.getAttribute('data-fstop')) - val) < 0.05
          ? 'fstop-btn py-1.5 rounded-lg bg-blue-600 border border-blue-500 text-white font-bold'
          : 'fstop-btn py-1.5 rounded-lg bg-church-950 border border-church-800 text-slate-300 hover:text-white font-bold';
      });
      applyCurrentManualParams();
    }

    function updateSliderAndReprocess(id, val, suffix) {
      document.getElementById(`val_${id}`).textContent = `${val}${suffix}`;
      if (!animFrameRequested) {
        animFrameRequested = true;
        requestAnimationFrame(() => {
          applyCurrentManualParams();
          animFrameRequested = false;
        });
      }
    }

    function applyCurrentManualParams() {
      if (!activeItem) return;
      const params = {
        exposure_compensation: parseFloat(document.getElementById('param_exposure').value),
        temperature_kelvin: parseInt(document.getElementById('param_kelvin').value),
        tint: parseFloat(document.getElementById('param_tint').value),
        contrast: parseFloat(document.getElementById('param_contrast').value),
        highlights: parseFloat(document.getElementById('param_highlights').value),
        shadows: parseFloat(document.getElementById('param_shadows').value),
        whites: parseFloat(document.getElementById('param_whites').value),
        blacks: parseFloat(document.getElementById('param_blacks').value),
        saturation: parseFloat(document.getElementById('param_saturation').value),
        vibrance: 1.0,
        clarity: parseFloat(document.getElementById('param_clarity').value),
        dehaze: parseFloat(document.getElementById('param_dehaze').value),
        vignette: parseFloat(document.getElementById('param_vignette').value)
      };

      const img = activeItem.cachedImg || new Image();
      if (!activeItem.cachedImg) img.src = activeItem.previewUrl;
      const result = processImageClientSideFast(img, params, false);
      activeItem.processedBase64 = result.base64;
      activeItem.currentParams = params;
      document.getElementById('imgAfter').src = result.base64;
      document.getElementById('imgSideAfter').src = result.base64;
    }

    function setViewerMode(mode) {
      viewerMode = mode;
      document.getElementById('modeSliderBtn').className = mode === 'slider' ? 'px-2 py-1 rounded-md bg-blue-600 text-white font-medium text-[11px]' : 'px-2 py-1 rounded-md text-slate-400 hover:text-white font-medium text-[11px]';
      document.getElementById('modeSideBtn').className = mode === 'side' ? 'px-2 py-1 rounded-md bg-blue-600 text-white font-medium text-[11px]' : 'px-2 py-1 rounded-md text-slate-400 hover:text-white font-medium text-[11px]';
      if (activeItem && activeItem.status === 'completed') showProcessedViewer(activeItem);
    }

    function setupSliderEvents() {
      const divider = document.getElementById('dividerLine');
      const clip = document.getElementById('clipContainer');
      const wrapper = document.getElementById('sliderWrapper');

      const move = (clientX) => {
        const rect = wrapper.getBoundingClientRect();
        sliderPercent = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
        divider.style.left = `${sliderPercent}%`;
        clip.style.clipPath = `polygon(0 0, ${sliderPercent}% 0, ${sliderPercent}% 100%, 0 100%)`;
      };

      divider.onmousedown = () => isDragging = true;
      divider.ontouchstart = () => isDragging = true;
      window.onmousemove = (e) => { if (isDragging) move(e.clientX); };
      window.ontouchmove = (e) => { if (isDragging && e.touches[0]) move(e.touches[0].clientX); };
      window.onmouseup = () => { setTimeout(() => isDragging = false, 50); };
      window.ontouchend = () => { setTimeout(() => isDragging = false, 50); };
    }

    function downloadCurrentProcessed() {
      if (!activeItem) return;
      const img = activeItem.cachedImg || new Image();
      if (!activeItem.cachedImg) img.src = activeItem.previewUrl;
      const res = processImageClientSideFast(img, activeItem.currentParams || {}, true);
      const a = document.createElement('a');
      a.href = res.base64;
      a.download = `dslr_${activeItem.fileName || 'foto.jpg'}`;
      a.click();
    }
  