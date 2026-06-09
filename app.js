/* =========================================================================
   Фактура — логика витрины: рендер каталога, фильтр, поиск, модалка, форма.
   Данные берутся из products.js (PRODUCTS, CATEGORIES). Без сборки и зависимостей.
   ========================================================================= */
(function () {
  "use strict";

  /* ---------- утилиты ---------- */
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }
  function formatPrice(n) {
    return n.toLocaleString("ru-RU");
  }

  /* ---------- состояние ---------- */
  const state = { category: "all", query: "" };

  /* ---------- ссылки на DOM ---------- */
  const catalogGrid = $("#catalogGrid");
  const catalogEmpty = $("#catalogEmpty");
  const categoriesGrid = $("#categoriesGrid");
  const chipsBox = $("#chips");
  const resultCount = $("#resultCount");
  const resetBtn = $("#resetFilters");
  const searchInputs = [$("#searchInputHeader"), $("#searchInputCatalog")].filter(Boolean);
  const searchClear = $("#searchClear");

  /* ===================================================================
     Рендер категорий
     =================================================================== */
  function renderCategories() {
    categoriesGrid.innerHTML = CATEGORIES.map((c) => `
      <button class="category-card" type="button" data-cat="${c.key}" aria-label="Категория «${escapeHtml(c.name)}» — показать в каталоге">
        <span class="category-card__media">
          <img src="${c.image}" alt="Категория «${escapeHtml(c.name)}»" loading="lazy" width="640" height="400" />
        </span>
        <span class="category-card__body">
          <span class="category-card__name">${escapeHtml(c.name)}</span>
          <span class="category-card__blurb">${escapeHtml(c.blurb)}</span>
          <span class="category-card__more">Смотреть в каталоге</span>
        </span>
      </button>`).join("");
  }

  /* ===================================================================
     Чипсы-фильтры
     =================================================================== */
  function renderChips() {
    const all = `<button class="chip" type="button" data-cat="all">Все</button>`;
    const rest = CATEGORIES.map(
      (c) => `<button class="chip" type="button" data-cat="${c.key}">${escapeHtml(c.name)}</button>`
    ).join("");
    chipsBox.innerHTML = all + rest;
    updateActiveChip();
  }
  function updateActiveChip() {
    $$(".chip", chipsBox).forEach((ch) => {
      const active = ch.dataset.cat === state.category;
      ch.classList.toggle("is-active", active);
      ch.setAttribute("aria-pressed", String(active));
    });
  }

  /* ===================================================================
     Каталог: фильтр + поиск + рендер
     =================================================================== */
  function getFiltered() {
    const q = state.query.trim().toLowerCase();
    return PRODUCTS.filter((p) => {
      const byCat = state.category === "all" || p.catKey === state.category;
      const byQuery =
        !q ||
        p.name.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q) ||
        p.short.toLowerCase().includes(q);
      return byCat && byQuery;
    });
  }

  function cardHTML(p) {
    return `
      <article class="card">
        <div class="card__media">
          <img src="${p.image}" alt="${escapeHtml(p.name)} — ${escapeHtml(p.category)}" loading="lazy" width="800" height="600" />
          <span class="card__cat">${escapeHtml(p.category)}</span>
        </div>
        <div class="card__body">
          <h3 class="card__name">${escapeHtml(p.name)}</h3>
          <p class="card__short">${escapeHtml(p.short)}</p>
          <div class="card__footer">
            <div class="card__price">от ${formatPrice(p.priceFrom)} ₽<small>за ${escapeHtml(p.unit)}</small></div>
            <button class="btn btn--outline card__btn" type="button" data-detail="${p.id}">Подробнее</button>
          </div>
        </div>
      </article>`;
  }

  function applyFilter() {
    const list = getFiltered();
    catalogGrid.innerHTML = list.map(cardHTML).join("");

    const empty = list.length === 0;
    catalogEmpty.hidden = !empty;
    catalogGrid.hidden = empty;

    // счётчик
    const total = PRODUCTS.length;
    if (state.category === "all" && !state.query.trim()) {
      resultCount.textContent = `Всего позиций: ${total}`;
    } else {
      resultCount.textContent = `Найдено: ${list.length} из ${total}`;
    }

    // кнопка сброса
    const filtered = state.category !== "all" || state.query.trim() !== "";
    resetBtn.hidden = !filtered;

    updateActiveChip();
  }

  function setCategory(key) {
    state.category = key;
    applyFilter();
  }
  function setQuery(value, syncInputs) {
    state.query = value;
    if (searchClear) searchClear.hidden = value.trim() === "";
    if (syncInputs) searchInputs.forEach((i) => { if (i.value !== value) i.value = value; });
    applyFilter();
  }
  function resetFilters() {
    state.category = "all";
    setQuery("", true);
  }

  /* ===================================================================
     Модалка товара
     =================================================================== */
  const modal = $("#modal");
  const modalBody = $("#modalBody");
  let lastFocused = null;

  function modalHTML(p) {
    const specsRows = Object.entries(p.specs)
      .map(([k, v]) => `<tr><th scope="row">${escapeHtml(k)}</th><td>${escapeHtml(v)}</td></tr>`)
      .join("");
    return `
      <div class="modal__grid">
        <div class="modal__media">
          <img src="${p.image}" alt="${escapeHtml(p.name)} — ${escapeHtml(p.category)}" width="800" height="600" />
        </div>
        <div class="modal__content">
          <span class="modal__cat">${escapeHtml(p.category)}</span>
          <h2 class="modal__title" id="modalTitle">${escapeHtml(p.name)}</h2>
          <p class="modal__desc">${escapeHtml(p.description)}</p>
          <table class="modal__specs">
            <caption>Характеристики</caption>
            <tbody>${specsRows}</tbody>
          </table>
          <div class="modal__footer">
            <div class="modal__price">от ${formatPrice(p.priceFrom)} ₽ <small>за ${escapeHtml(p.unit)}</small></div>
            <button class="btn btn--primary btn--lg" type="button" data-request="${escapeHtml(p.name)}">Оставить заявку</button>
          </div>
        </div>
      </div>`;
  }

  function openModal(id, fromHash) {
    const p = PRODUCTS.find((x) => x.id === id);
    if (!p) return;
    modalBody.innerHTML = modalHTML(p);
    lastFocused = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("no-scroll");
    const closeBtn = $("#modalClose");
    if (closeBtn) closeBtn.focus();
    // короткая ссылка на товар (без прыжка по странице)
    if (!fromHash && window.history && history.replaceState) {
      history.replaceState(null, "", "#tovar-" + id);
    }
  }

  function closeModal() {
    if (modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("no-scroll");
    if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
    if (/^#tovar-\d+$/.test(location.hash) && window.history && history.replaceState) {
      history.replaceState(null, "", location.pathname + location.search);
    }
  }

  // фокус-ловушка внутри диалога
  function trapFocus(e) {
    if (modal.hidden || e.key !== "Tab") return;
    const focusables = $$(
      'a[href], button:not([disabled]), input, textarea, [tabindex]:not([tabindex="-1"])',
      modal
    ).filter((el) => el.offsetParent !== null);
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  /* ===================================================================
     Toast
     =================================================================== */
  const toast = $("#toast");
  let toastTimer = null;
  function showToast(message) {
    toast.innerHTML =
      `<span class="toast__icon" aria-hidden="true">✓</span><span class="toast__text">${message}</span>`;
    toast.hidden = false;
    // форсируем reflow, чтобы сработал transition
    void toast.offsetWidth;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove("is-visible");
      setTimeout(() => { toast.hidden = true; }, 300);
    }, 4500);
  }

  /* ===================================================================
     Форма заявки
     =================================================================== */
  const form = $("#leadForm");

  function setFieldError(input, message) {
    const field = input.closest(".field");
    field.classList.toggle("has-error", Boolean(message));
    const err = $('[data-error-for="' + input.id + '"]', field);
    if (err) err.textContent = message || "";
    if (message) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
  }

  function validatePhone(value) {
    const digits = value.replace(/\D/g, "");
    return digits.length >= 10 && digits.length <= 15;
  }

  function validateForm() {
    const name = $("#fName");
    const phone = $("#fPhone");
    let ok = true;

    if (!name.value.trim()) { setFieldError(name, "Укажите, как к вам обращаться"); ok = false; }
    else if (name.value.trim().length < 2) { setFieldError(name, "Слишком короткое имя"); ok = false; }
    else setFieldError(name, "");

    if (!phone.value.trim()) { setFieldError(phone, "Укажите телефон для связи"); ok = false; }
    else if (!validatePhone(phone.value)) { setFieldError(phone, "Введите корректный номер телефона"); ok = false; }
    else setFieldError(phone, "");

    return ok;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validateForm()) {
      const firstErr = $(".field.has-error .field__input", form);
      if (firstErr) firstErr.focus();
      return;
    }
    const name = $("#fName").value.trim();
    form.reset();
    ["fName", "fPhone", "fMessage"].forEach((id) => setFieldError($("#" + id), ""));
    showToast(`Спасибо, <b>${escapeHtml(name)}</b>! Заявка принята — менеджер свяжется с вами.`);
  }

  /* ===================================================================
     Бургер-меню
     =================================================================== */
  const burger = $("#burger");
  const nav = $("#nav");
  function setMenu(open) {
    nav.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Закрыть меню" : "Открыть меню");
  }

  /* ===================================================================
     Кнопка «наверх»
     =================================================================== */
  const toTop = $("#toTop");
  function onScroll() {
    const show = window.scrollY > 600;
    toTop.hidden = false; // оставляем в потоке, управляем классом
    toTop.classList.toggle("is-visible", show);
  }

  /* ===================================================================
     Делегирование событий
     =================================================================== */
  function bindEvents() {
    // клик по категории → фильтр + скролл к каталогу
    categoriesGrid.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-cat]");
      if (!btn) return;
      setCategory(btn.dataset.cat);
      document.getElementById("catalog").scrollIntoView({ behavior: "smooth", block: "start" });
    });

    // чипсы
    chipsBox.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      setCategory(chip.dataset.cat);
    });

    // «Подробнее» → модалка
    catalogGrid.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-detail]");
      if (!btn) return;
      openModal(Number(btn.dataset.detail));
    });

    // поиск (оба поля синхронизированы)
    searchInputs.forEach((input) => {
      input.addEventListener("input", () => setQuery(input.value, true));
    });
    if (searchClear) {
      searchClear.addEventListener("click", () => { setQuery("", true); searchInputs[searchInputs.length - 1].focus(); });
    }
    // не перезагружать страницу при Enter в форме поиска
    $$('form[role="search"]').forEach((f) => f.addEventListener("submit", (e) => e.preventDefault()));

    resetBtn.addEventListener("click", resetFilters);

    // модалка: закрытие
    modal.addEventListener("click", (e) => { if (e.target.closest("[data-close]")) closeModal(); });
    // «Оставить заявку» из модалки
    modal.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-request]");
      if (!btn) return;
      closeModal();
      const msg = $("#fMessage");
      if (msg) msg.value = `Интересует: ${btn.dataset.request}`;
      document.getElementById("contacts").scrollIntoView({ behavior: "smooth", block: "start" });
      setTimeout(() => { const n = $("#fName"); if (n) n.focus(); }, 450);
    });

    // клавиатура: Esc + фокус-ловушка
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { closeModal(); if (nav.classList.contains("is-open")) setMenu(false); }
      trapFocus(e);
    });

    // форма
    form.addEventListener("submit", handleSubmit);
    // снимаем ошибку при вводе
    ["fName", "fPhone"].forEach((id) => {
      const el = $("#" + id);
      el.addEventListener("input", () => { if (el.closest(".field").classList.contains("has-error")) setFieldError(el, ""); });
    });

    // бургер
    burger.addEventListener("click", () => setMenu(!nav.classList.contains("is-open")));
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
    window.addEventListener("resize", () => { if (window.innerWidth >= 960) setMenu(false); });

    // наверх
    toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ===================================================================
     Инициализация
     =================================================================== */
  function init() {
    renderCategories();
    renderChips();
    applyFilter();
    bindEvents();
    onScroll();
    const yearEl = $("#year");
    if (yearEl) yearEl.textContent = new Date().getFullYear();
    // открыть товар по короткой ссылке #tovar-N
    const m = /^#tovar-(\d+)$/.exec(location.hash);
    if (m) openModal(Number(m[1]), true);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
