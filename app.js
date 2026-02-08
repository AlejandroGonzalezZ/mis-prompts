/**
 * Sistema de Alertas Dinámicas
 */
const AlertSystem = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',

  show(message, type = 'success', duration = 5000) {
    const alertsContainer = document.getElementById('alerts-container');
    const alertId = `alert-${Date.now()}`;
    
    const alertHTML = `
      <div id="${alertId}" class="animate-in fade-in slide-in-from-top-4 ${this.getAlertClasses(type)}">
        <div class="flex items-start justify-between">
          <div class="flex items-start gap-3">
            <span class="text-xl">${this.getAlertIcon(type)}</span>
            <p>${message}</p>
          </div>
          <button onclick="document.getElementById('${alertId}').remove()" class="text-lg cursor-pointer hover:opacity-70">✕</button>
        </div>
      </div>
    `;

    alertsContainer.insertAdjacentHTML('beforeend', alertHTML);

    if (duration > 0) {
      setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
          alert.classList.add('animate-out', 'fade-out', 'slide-out-to-top-4');
          setTimeout(() => alert.remove(), 300);
        }
      }, duration);
    }
  },

  getAlertClasses(type) {
    const base = 'bg-neutral-900/80 backdrop-blur-md p-4 rounded-xl border transition-all duration-300';
    
    switch(type) {
      case 'success':
        return `${base} border-emerald-500/50 shadow-[0_0_15px_-5px_rgba(16,185,129,0.3)] text-emerald-200`;
      case 'error':
        return `${base} border-red-500/50 shadow-[0_0_15px_-5px_rgba(239,68,68,0.3)] text-red-200`;
      case 'warning':
        return `${base} border-orange-500/50 shadow-[0_0_20px_-5px_rgba(249,115,22,0.4)] text-orange-100`;
      default:
        return base;
    }
  },

  getAlertIcon(type) {
    const icons = {
      success: '✔️',
      error: '❌',
      warning: '⚠️'
    };
    return icons[type] || '❓';
  }
};

/**
 * Manejo de Carga de Imágenes
 */
const ImageHandler = {
  init() {
    const imageInput = document.getElementById('image-upload');
    if (imageInput) {
      imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
    }
  },

  handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validar tipo de archivo
    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      AlertSystem.show('Por favor, sube una imagen en formato JPG o PNG', AlertSystem.WARNING);
      event.target.value = '';
      return;
    }

    // Validar tamaño (máximo 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      AlertSystem.show('La imagen es demasiado grande. Máximo 10MB', AlertSystem.WARNING);
      event.target.value = '';
      return;
    }

    // Mostrar preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = document.getElementById('image-preview');
      preview.innerHTML = `
        <div class="relative inline-block">
          <img src="${e.target.result}" alt="Preview" class="max-w-xs max-h-48 rounded-lg border border-orange-500/50 shadow-glow">
          <button type="button" onclick="ImageHandler.clearImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition-colors">
            ✕
          </button>
        </div>
      `;
      AlertSystem.show('Imagen cargada correctamente', AlertSystem.SUCCESS, 3000);
    };
    reader.readAsDataURL(file);
  },

  clearImage() {
    document.getElementById('image-upload').value = '';
    document.getElementById('image-preview').innerHTML = '';
  },

  getImageData() {
    const input = document.getElementById('image-upload');
    return input.files[0] || null;
  }
};

/**
 * Manejo de Copiar al Portapapeles
 */
const ClipboardHandler = {
  init() {
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('copy-btn')) {
        this.copyToClipboard(e.target);
      }
    });
  },

  async copyToClipboard(button) {
    const textareaId = button.dataset.target;
    const textarea = document.getElementById(textareaId);

    if (!textarea || !textarea.value.trim()) {
      AlertSystem.show('No hay contenido para copiar', AlertSystem.WARNING);
      return;
    }

    try {
      await navigator.clipboard.writeText(textarea.value);
      
      // Cambiar texto del botón temporalmente
      const originalText = button.textContent;
      button.textContent = '✔️ Copiado';
      button.classList.add('bg-emerald-500');
      button.classList.remove('bg-orange-500', 'hover:bg-orange-600');

      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('bg-emerald-500');
        button.classList.add('bg-orange-500', 'hover:bg-orange-600');
      }, 2000);

      AlertSystem.show('¡Prompt copiado al portapapeles!', AlertSystem.SUCCESS, 2000);
    } catch (err) {
      AlertSystem.show('Error al copiar al portapapeles', AlertSystem.ERROR);
      console.error('Error:', err);
    }
  }
};

/**
 * Manejo de Formulario Principal
 */
const FormHandler = {
  init() {
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.validateAndSubmit());
    }

    // Agregar botones de copiar a los textarea de resultados
    this.setupResultButtons();
  },

  setupResultButtons() {
    const resultIds = ['prompt-es', 'prompt-video'];
    const buttonTexts = ['Copiar', 'Copiar'];

    resultIds.forEach((id, index) => {
      const textarea = document.getElementById(id);
      if (textarea) {
        const buttonContainer = textarea.parentElement.querySelector('button');
        if (buttonContainer) {
          const button = buttonContainer || document.createElement('button');
          button.type = 'button';
          button.className = 'mt-2 px-4 py-2 rounded-full bg-orange-500 text-deep-black text-sm font-bold hover:bg-orange-600 transition-colors duration-300 copy-btn';
          button.dataset.target = id;
          button.textContent = buttonTexts[index];
          
          if (!buttonContainer) {
            textarea.parentElement.appendChild(button);
          }
        }
      }
    });

    // Agregar botón "Guardar en Favoritos"
    const saveFavBtn = document.querySelector('button.bg-gradient-to-r.from-orange-600:last-of-type');
    if (saveFavBtn) {
      saveFavBtn.id = 'save-favorites-btn';
      saveFavBtn.addEventListener('click', () => this.saveFavorite());
    }
  },

  validateAndSubmit() {
    const ideaInput = document.getElementById('idea-input').value.trim();
    const styleSelect = document.getElementById('style-select').value;
    const personajes = this.getSelectedCharacters();

    if (!ideaInput) {
      AlertSystem.show('Por favor, ingresa una idea o descripción', AlertSystem.WARNING);
      return;
    }

    this.setLoading(true);
    this.submitToBackend({
      idea: ideaInput,
      style: styleSelect,
      personajes: personajes,
      image: ImageHandler.getImageData()
    });
  },

  getSelectedCharacters() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][value]');
    const selected = Array.from(checkboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value);
    return selected.length > 0 ? selected : ['ninguno'];
  },

  setLoading(isLoading) {
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
      sendBtn.disabled = isLoading;
      sendBtn.textContent = isLoading ? '⏳ Generando...' : 'Enviar Información';
    }
  },

  async submitToBackend(data) {
    try {
      console.log('Enviando datos al backend:', data);

      // Preparar FormData para enviar con archivo si existe
      const formData = new FormData();
      formData.append('idea', data.idea);
      formData.append('style', data.style);
      formData.append('personajes', JSON.stringify(data.personajes));
      
      if (data.image) {
        formData.append('image', data.image);
      }

      // URL del backend
      const apiUrl = data.image 
        ? 'http://localhost:8001/api/generate-with-image'
        : 'http://localhost:8001/api/generate-prompts';

      // Llamar al backend
      const endpoint = data.image 
        ? 'http://localhost:8001/api/generate-with-image'
        : 'http://localhost:8001/api/generate-prompts';
      
      const response = await fetch(endpoint, {
        method: data.image ? 'POST' : 'POST',
        headers: data.image ? {} : { 'Content-Type': 'application/json' },
        body: data.image ? formData : JSON.stringify({
          idea: data.idea,
          style: data.style,
          personajes: data.personajes
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error en el servidor');
      }

      const result = await response.json();
      
      this.displayResults({
        prompt_es: result.prompt_es,
        prompt_video: result.prompt_video,
        model_info: result.model_info || result.model_used || ''
      });
      
      AlertSystem.show('¡Prompts generados exitosamente!', AlertSystem.SUCCESS);
      console.log('✅ Respuesta del servidor:', result);

    } catch (error) {
      AlertSystem.show('Error al conectar con el servidor: ' + error.message, AlertSystem.ERROR);
      console.error('Error:', error);
      
      // Fallback: mostrar prompts simulados
      console.log('⚠️ Usando respuesta simulada como fallback');
      this.displayResults({
        prompt_es: 'Fotografía ultrarrealista de una mujer en un entorno hermoso...',
        prompt_video: 'Woman walking gracefully with gentle camera movement...'
      });
    } finally {
      this.setLoading(false);
    }
  },

  displayResults(results) {
    document.getElementById('prompt-es').value = results.prompt_es || '';
    document.getElementById('prompt-video').value = results.prompt_video || '';
    const infoEl = document.getElementById('model-info');
    if (infoEl) infoEl.textContent = results.model_info || '';
  },

  async saveFavorite() {
    const promptEs = document.getElementById('prompt-es').value.trim();
    const promptVideo = document.getElementById('prompt-video').value.trim();
    const ideaInput = document.getElementById('idea-input').value.trim();
    const personajes = this.getSelectedCharacters().join(', ');

    if (!promptEs || !promptVideo) {
      AlertSystem.show('Debes generar los prompts antes de guardarlos', AlertSystem.WARNING);
      return;
    }

    try {
      const response = await fetch('http://localhost:8001/api/save-favorite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          titulo: ideaInput || 'Prompt sin título',
          personaje: personajes,
          prompt_es: promptEs,
          prompt_video: promptVideo
        })
      });

      const result = await response.json();

      if (result.success) {
        AlertSystem.show('¡Prompt agregado a favoritos!', AlertSystem.SUCCESS);
        this.clearForm();
        this.loadFavorites(); // Recargar tabla de favoritos
      } else {
        AlertSystem.show('Error al guardar: ' + result.error, AlertSystem.ERROR);
      }
    } catch (error) {
      AlertSystem.show('Error de conexión: ' + error.message, AlertSystem.ERROR);
      console.error('Error:', error);
    }
  },

  clearForm() {
    document.getElementById('idea-input').value = '';
    document.getElementById('style-select').value = 'fotografia';
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    ImageHandler.clearImage();
    document.getElementById('prompt-es').value = '';
    document.getElementById('prompt-video').value = '';
  }
};

/**
 * Manejo del Panel de Favoritos
 */
const FavoritesHandler = {
  init() {
    const searchInput = document.getElementById('search-favorites');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.searchFavorites(e.target.value));
    }
    
    // Cargar favoritos al iniciar
    this.loadFavorites();
  },

  async loadFavorites() {
    try {
      const response = await fetch('http://localhost:8001/api/favorites');
      const result = await response.json();
      
      if (result.success && result.data && result.data.length > 0) {
        this.populateTable(result.data);
      } else {
        console.log('No hay favoritos guardados');
      }
    } catch (error) {
      console.error('Error al cargar favoritos:', error);
    }
  },

  populateTable(prompts) {
    const tableBody = document.getElementById('favorites-table-body');
    tableBody.innerHTML = '';
    
    prompts.forEach((prompt, index) => {
      const row = document.createElement('tr');
      row.className = 'bg-neutral-800/80 hover:bg-neutral-700/80 transition-colors duration-200';
      row.innerHTML = `
        <td class="px-4 py-2 border-b border-neutral-700">${index + 1}</td>
        <td class="px-4 py-2 border-b border-neutral-700">${prompt.Título || 'Sin título'}</td>
        <td class="px-4 py-2 border-b border-neutral-700">${prompt.Personaje || '-'}</td>
        <td class="px-4 py-2 border-b border-neutral-700 truncate text-xs">${(prompt.Prompt_ES || '').substring(0, 50)}...</td>
        <td class="px-4 py-2 border-b border-neutral-700 truncate text-xs">${(prompt.Prompt_Video || '').substring(0, 50)}...</td>
      `;
      tableBody.appendChild(row);
    });
  },

  async searchFavorites(query) {
    query = query.toLowerCase().trim();
    
    if (!query) {
      this.loadFavorites();
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8001/api/favorites/search?query=${encodeURIComponent(query)}`);
      const result = await response.json();
      
      if (result.success && result.data && result.data.length > 0) {
        this.populateTable(result.data);
        AlertSystem.show(`Se encontraron ${result.count} coincidencia(s)`, AlertSystem.SUCCESS, 2000);
      } else {
        AlertSystem.show(`No se encontraron resultados para "${query}"`, AlertSystem.WARNING);
        document.getElementById('favorites-table-body').innerHTML = '';
      }
    } catch (error) {
      AlertSystem.show('Error en búsqueda: ' + error.message, AlertSystem.ERROR);
      console.error('Error:', error);
    }
  }
};

/**
 * Inicialización Global
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Aplicación cargada');
  ImageHandler.init();
  ClipboardHandler.init();
  FormHandler.init();
  FavoritesHandler.init();
});
