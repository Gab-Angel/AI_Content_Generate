/**
 * AI Content Generator - Frontend Application
 * Gerencia o formulário e a comunicação com a API REST
 */

const API_BASE = window.location.origin;

// ===== DOM Elements =====
const form = document.getElementById('generateForm');
const submitBtn = document.getElementById('submitBtn');
const typePostSelect = document.getElementById('type_post');
const slidesGroup = document.getElementById('slidesGroup');
const slidesInput = document.getElementById('slides');
const errorBanner = document.getElementById('errorBanner');
const errorMessage = errorBanner?.querySelector('.error-message');
const successBanner = document.getElementById('successBanner');
const errorsToolbar = document.getElementById('errorsToolbar');
const toggleErrorsBtn = document.getElementById('toggleErrorsBtn');
const toggleErrorsText = toggleErrorsBtn?.querySelector('.toggle-errors-text');
const resultsSection = document.getElementById('resultsSection');
const researchContent = document.getElementById('researchContent');
const contentResult = document.getElementById('contentResult');

// ===== Estado =====
let isSubmitting = false;

// Garante que banners e seções ocultos ao carregar (evita mostrar sucesso antes de gerar)
if (successBanner) successBanner.hidden = true;
if (errorBanner) errorBanner.hidden = true;
if (errorsToolbar) errorsToolbar.hidden = true;
if (resultsSection) resultsSection.hidden = true;
let hasError = false;
let errorsVisible = true;
let successBannerTimeout = null;      // timeout que esconde o banner após 5s
let successBannerShowTimeout = null;  // timeout que mostra o banner após 350ms (cancelar ao iniciar nova geração)

// ===== Toggle Slides (apenas para carousel) =====
function toggleSlidesVisibility() {
    const isCarousel = typePostSelect?.value === 'carousel';
    if (slidesGroup) {
        slidesGroup.classList.toggle('hidden', !isCarousel);
        if (slidesInput) {
            slidesInput.required = isCarousel;
        }
    }
}

typePostSelect?.addEventListener('change', toggleSlidesVisibility);
toggleSlidesVisibility(); // Estado inicial

// Fechar banner de erro ao clicar no X (oculta erros)
errorBanner?.querySelector('.error-dismiss')?.addEventListener('click', () => {
    errorsVisible = false;
    hideErrorBanner();
    updateErrorsToolbar();
});

// Toggle mostrar/ocultar erros
toggleErrorsBtn?.addEventListener('click', () => {
    errorsVisible = !errorsVisible;
    if (errorsVisible) {
        errorBanner.hidden = false;
        toggleErrorsBtn.setAttribute('aria-expanded', 'true');
        if (toggleErrorsText) toggleErrorsText.textContent = 'Ocultar erros';
    } else {
        errorBanner.hidden = true;
        toggleErrorsBtn.setAttribute('aria-expanded', 'false');
        if (toggleErrorsText) toggleErrorsText.textContent = 'Mostrar erros';
    }
});

// ===== Helpers =====
function setLoading(loading) {
    isSubmitting = loading;
    if (submitBtn) {
        submitBtn.disabled = loading;
        submitBtn.classList.toggle('loading', loading);
    }
}

function showError(message) {
    hasError = true;
    errorsVisible = true;
    if (errorBanner && errorMessage) {
        errorMessage.textContent = message;
        errorBanner.hidden = false;
        errorBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    updateErrorsToolbar();
    hideSuccessBanner();
}

function hideErrorBanner() {
    if (errorBanner) errorBanner.hidden = true;
}

function hideError() {
    if (errorBanner) errorBanner.hidden = true;
    updateErrorsToolbar();
}

function updateErrorsToolbar() {
    if (!errorsToolbar || !toggleErrorsBtn || !toggleErrorsText) return;
    if (!hasError) {
        errorsToolbar.hidden = true;
        return;
    }
    errorsToolbar.hidden = false;
    toggleErrorsBtn.setAttribute('aria-expanded', String(errorsVisible));
    if (toggleErrorsText) toggleErrorsText.textContent = errorsVisible ? 'Ocultar erros' : 'Mostrar erros';
    errorBanner.hidden = !errorsVisible;
}

function showSuccessBanner() {
    if (!successBanner) return;
    if (successBannerTimeout) clearTimeout(successBannerTimeout);
    successBanner.hidden = false;
    successBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    successBannerTimeout = setTimeout(() => {
        successBanner.hidden = true;
        successBannerTimeout = null;
    }, 5000);
}

function hideSuccessBanner() {
    if (successBanner) successBanner.hidden = true;
    if (successBannerTimeout) {
        clearTimeout(successBannerTimeout);
        successBannerTimeout = null;
    }
    // Cancela o agendamento de "mostrar banner" (evita que apareça no meio de uma nova geração)
    if (successBannerShowTimeout) {
        clearTimeout(successBannerShowTimeout);
        successBannerShowTimeout = null;
    }
}

function renderResearch(research) {
    if (!researchContent) return;

    const html = [
        research.summary && `
            <h4>Resumo</h4>
            <p>${escapeHtml(research.summary)}</p>
        `,
        research.key_points?.length && `
            <h4>Pontos Principais</h4>
            <ul>
                ${research.key_points.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
            </ul>
        `,
        research.sources?.length && `
            <h4>Fontes</h4>
            <ul>
                ${research.sources.map(s => `<li><a href="${escapeHtml(s)}" target="_blank" rel="noopener">${truncateUrl(s)}</a></li>`).join('')}
            </ul>
        `,
        research.insights?.length && `
            <h4>Insights</h4>
            <ul>
                ${research.insights.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
            </ul>
        `
    ].filter(Boolean).join('');

    researchContent.innerHTML = html || '<p>Nenhuma pesquisa disponível.</p>';
}

function renderContent(content) {
    if (!contentResult) return;

    const html = [
        content.title && `
            <h4>Título</h4>
            <p>${escapeHtml(content.title)}</p>
        `,
        content.texts?.length && `
            <h4>Textos</h4>
            <ul class="texts-list">
                ${content.texts.map((t, i) => `<li><strong>${i + 1}.</strong> ${escapeHtml(t)}</li>`).join('')}
            </ul>
        `,
        content.caption && `
            <h4>Caption</h4>
            <p>${escapeHtml(content.caption)}</p>
        `,
        content.hashtags && `
            <h4>Hashtags</h4>
            <p class="hashtags">${escapeHtml(content.hashtags)}</p>
        `,
        content.notes && `
            <h4>Notas</h4>
            <p>${escapeHtml(content.notes)}</p>
        `
    ].filter(Boolean).join('');

    contentResult.innerHTML = html || '<p>Nenhum conteúdo gerado.</p>';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateUrl(url) {
    if (!url) return '';
    try {
        const u = new URL(url);
        return u.hostname + (u.pathname.length > 30 ? u.pathname.slice(0, 30) + '...' : u.pathname);
    } catch {
        return url.length > 50 ? url.slice(0, 50) + '...' : url;
    }
}

// ===== Submit Handler =====
async function handleSubmit(e) {
    e.preventDefault();
    if (isSubmitting) return;

    hideErrorBanner();
    hideSuccessBanner();
    hasError = false;
    errorsVisible = true;
    updateErrorsToolbar();

    const payload = {
        type_post: form.type_post.value,
        topic: form.topic.value.trim(),
        idea: form.idea.value.trim(),
        tone: form.tone.value
    };

    if (form.type_post.value === 'carousel' && slidesInput?.value) {
        payload.slides = parseInt(slidesInput.value, 10) || 3;
    }

    setLoading(true);

    try {
        const res = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            const msg = typeof data.detail === 'string'
                ? data.detail
                : Array.isArray(data.detail) && data.detail[0]?.msg
                    ? data.detail.map(d => d.msg).join('; ')
                    : data.error || `Erro ${res.status}`;
            throw new Error(msg);
        }

        if (!data.success) {
            showError(data.error || 'Erro ao gerar conteúdo.');
        }

        // Renderiza resultados
        if (data.research) {
            renderResearch(data.research);
        }
        if (data.content) {
            renderContent(data.content);
        }

        if (data.research || data.content) {
            resultsSection.hidden = false;
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            // Banner de sucesso só quando a API confirmar sucesso (tarefa concluída)
            if (data.success === true) {
                setLoading(false);
                // Cancela qualquer exibição de banner agendada por uma geração anterior
                if (successBannerShowTimeout) {
                    clearTimeout(successBannerShowTimeout);
                    successBannerShowTimeout = null;
                }
                // Exibe o banner só após a interface atualizar (botão "Gerar" e resultados já visíveis)
                successBannerShowTimeout = setTimeout(() => {
                    successBannerShowTimeout = null;
                    showSuccessBanner();
                }, 350);
            }
        }
    } catch (err) {
        const message = err.message || 'Falha na comunicação com o servidor. Verifique sua conexão e as variáveis de ambiente (GROQ_API_KEY, TAVILY_API_KEY).';
        showError(message);
        console.error('Generate error:', err);
    } finally {
        setLoading(false);
    }
}

form?.addEventListener('submit', handleSubmit);
