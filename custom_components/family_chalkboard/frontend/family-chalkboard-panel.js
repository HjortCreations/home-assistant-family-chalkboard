const VIEW_MODE_STORAGE_KEY = "family-chalkboard:view-mode";
const MIN_CANVAS_ASPECT_RATIO = 0.1;
const MAX_CANVAS_ASPECT_RATIO = 10;

const TRANSLATIONS = {
  en: {
    title: "Family Chalkboard",
    subtitle: "Write or draw – everything saves automatically",
    loading: "Loading…",
    saving: "Saving…",
    saved: "Saved",
    saveError: "Could not save",
    loadError: "Could not load",
    noteLabel: "Family note",
    notePlaceholder: "Leave a small note for the family…",
    drawingArea: "Drawing area",
    drawingTools: "Drawing tools",
    chalk: "Chalk",
    eraser: "Eraser",
    undo: "Undo",
    undoLabel: "Undo the latest stroke",
    viewFit: "Fit",
    viewFill: "Fill",
    viewFitLabel: "View mode: fit the drawing without distortion",
    viewFillLabel: "View mode: fill the drawing area; proportions may change",
    clear: "Clear",
    empty: "Draw here with your finger ✦",
    canvasLabel: "Draw here with your finger",
    clearTitle: "Clear the whole board?",
    clearDescription: "Both the drawing and the family note will be removed.",
    cancel: "Cancel",
    confirm: "Yes, clear",
    colors: {
      white: "White chalk",
      yellow: "Yellow chalk",
      pink: "Pink chalk",
      blue: "Blue chalk",
      green: "Green chalk",
    },
    sizes: {
      thin: "Thin chalk",
      medium: "Medium chalk",
      thick: "Thick chalk",
    },
  },
  sv: {
    title: "Griffeltavlan",
    subtitle: "Skriv eller rita – allt sparas automatiskt",
    loading: "Laddar…",
    saving: "Sparar…",
    saved: "Sparad",
    saveError: "Kunde inte spara",
    loadError: "Kunde inte ladda",
    noteLabel: "Familjens notering",
    notePlaceholder: "Skriv en liten notering till familjen…",
    drawingArea: "Rityta",
    drawingTools: "Ritverktyg",
    chalk: "Krita",
    eraser: "Sudd",
    undo: "Ångra",
    undoLabel: "Ångra senaste strecket",
    viewFit: "Passa in",
    viewFill: "Fyll ytan",
    viewFitLabel: "Visning: passa in teckningen utan förvrängning",
    viewFillLabel: "Visning: fyll ritytan; proportionerna kan ändras",
    clear: "Töm",
    empty: "Rita med fingret här ✦",
    canvasLabel: "Rita med fingret här",
    clearTitle: "Töm hela tavlan?",
    clearDescription: "Både teckningen och familjens notering tas bort.",
    cancel: "Avbryt",
    confirm: "Ja, töm",
    colors: {
      white: "Vit krita",
      yellow: "Gul krita",
      pink: "Rosa krita",
      blue: "Blå krita",
      green: "Grön krita",
    },
    sizes: {
      thin: "Tunn krita",
      medium: "Mellanstor krita",
      thick: "Tjock krita",
    },
  },
};

const TEMPLATE = `
  <style>
    :host {
      display: block;
      width: 100%;
      height: 100%;
      min-height: 100vh;
      min-height: var(--family-chalkboard-viewport-height, 100dvh);
      overflow: hidden;
      color-scheme: dark;
      font-family:
        Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
      --gold: #d7a45c;
      --gold-soft: #f0c986;
      --ink: #f5f1ea;
      --muted: #b9aa9a;
      --border: rgba(215, 164, 92, .28);
      background: #08090a;
      color: var(--ink);
    }

    * {
      box-sizing: border-box;
    }

    button,
    textarea {
      font: inherit;
    }

    button {
      -webkit-tap-highlight-color: transparent;
    }

    .app {
      width: 100%;
      height: 100%;
      min-height: 100vh;
      min-height: var(--family-chalkboard-viewport-height, 100dvh);
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr);
      gap: 14px;
      padding: 18px;
      overflow: hidden;
      background:
        radial-gradient(
          circle at 80% 0%,
          rgba(183, 119, 47, .13),
          transparent 32%
        ),
        linear-gradient(145deg, #11100f, #050607 68%);
    }

    .topbar,
    .note-card,
    .board-shell {
      border: 1px solid var(--border);
      border-radius: 24px;
      background:
        linear-gradient(145deg, rgba(31, 28, 25, .94), rgba(10, 11, 13, .97));
      box-shadow:
        0 18px 44px rgba(0, 0, 0, .38),
        inset 0 1px 0 rgba(255, 234, 199, .06);
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
    }

    .title-group {
      min-width: 0;
    }

    h1 {
      margin: 0;
      color: var(--ink);
      font-size: clamp(1.45rem, 3.4vw, 2.2rem);
      letter-spacing: -.035em;
    }

    .subtitle {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: clamp(.85rem, 2vw, 1rem);
    }

    .save-status {
      flex: 0 0 auto;
      min-width: 92px;
      padding: 9px 13px;
      border: 1px solid rgba(215, 164, 92, .22);
      border-radius: 999px;
      color: var(--gold-soft);
      background: rgba(215, 164, 92, .09);
      font-size: .84rem;
      font-weight: 750;
      text-align: center;
    }

    .save-status[data-state="error"] {
      color: #ffb0a9;
      border-color: rgba(255, 121, 110, .3);
      background: rgba(255, 121, 110, .1);
    }

    .note-card {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      align-items: center;
      gap: 16px;
      padding: 14px 18px;
    }

    .note-label {
      display: grid;
      place-items: center;
      width: 52px;
      height: 52px;
      border-radius: 17px;
      color: #17120c;
      background: linear-gradient(145deg, var(--gold-soft), var(--gold));
      box-shadow: 0 8px 24px rgba(183, 119, 47, .24);
      font-size: 1.5rem;
      font-weight: 900;
    }

    textarea {
      width: 100%;
      min-height: 58px;
      max-height: 112px;
      resize: none;
      border: 0;
      outline: 0;
      color: var(--ink);
      background: transparent;
      font-size: clamp(1rem, 2.4vw, 1.25rem);
      line-height: 1.42;
    }

    textarea::placeholder {
      color: #8d8176;
    }

    .board-shell {
      min-height: 0;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      overflow: hidden;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 9px;
      min-height: 78px;
      padding: 12px 14px;
      overflow-x: auto;
      scrollbar-width: none;
      border-bottom: 1px solid rgba(215, 164, 92, .18);
      background: rgba(13, 13, 13, .76);
    }

    .toolbar::-webkit-scrollbar {
      display: none;
    }

    .tool-button,
    .color-button,
    .size-button {
      flex: 0 0 auto;
      min-width: 54px;
      min-height: 54px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(255, 255, 255, .1);
      border-radius: 17px;
      color: var(--ink);
      background: rgba(255, 255, 255, .055);
      font-weight: 760;
    }

    .tool-button {
      padding: 0 15px;
    }

    .tool-button:active,
    .color-button:active,
    .size-button:active {
      transform: translateY(1px);
    }

    .tool-button[aria-pressed="true"],
    .size-button[aria-pressed="true"] {
      color: #17120c;
      border-color: var(--gold);
      background: linear-gradient(145deg, var(--gold-soft), var(--gold));
    }

    .tool-button.danger {
      color: #ffc0ba;
      border-color: rgba(255, 121, 110, .22);
    }

    .separator {
      flex: 0 0 1px;
      width: 1px;
      height: 42px;
      margin: 0 2px;
      background: rgba(255, 255, 255, .12);
    }

    .color-button {
      position: relative;
      width: 54px;
      padding: 0;
    }

    .color-button::before {
      content: "";
      width: 25px;
      height: 25px;
      border-radius: 50%;
      background: var(--chalk-color);
      box-shadow: 0 0 0 2px rgba(255, 255, 255, .08);
    }

    .color-button[aria-pressed="true"] {
      border-color: var(--gold);
      box-shadow: inset 0 0 0 2px rgba(215, 164, 92, .24);
    }

    .size-button {
      width: 54px;
      padding: 0;
    }

    .size-dot {
      width: var(--dot-size);
      height: var(--dot-size);
      border-radius: 50%;
      background: currentColor;
    }

    .canvas-wrap {
      position: relative;
      min-height: 0;
      overflow: hidden;
      background:
        radial-gradient(circle at 50% 50%, rgba(215, 164, 92, .055), transparent 68%),
        #090c0b;
    }

    .drawing-surface {
      position: absolute;
      inset: 0;
      overflow: hidden;
      outline: 1px solid rgba(215, 164, 92, .12);
      outline-offset: -1px;
      border-radius: 16px;
      background:
        radial-gradient(
          circle at 18% 20%,
          rgba(255, 255, 255, .026) 0 1px,
          transparent 2px
        ),
        radial-gradient(
          circle at 74% 63%,
          rgba(255, 255, 255, .02) 0 1px,
          transparent 2px
        ),
        linear-gradient(120deg, rgba(255, 255, 255, .012), transparent 35%),
        #15211d;
      background-size: 31px 29px, 37px 41px, auto, auto;
      box-shadow:
        0 12px 42px rgba(0, 0, 0, .34),
        inset 0 0 72px rgba(0, 0, 0, .42);
    }

    canvas {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      touch-action: none;
      cursor: crosshair;
    }

    .empty-hint {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      padding: 28px;
      color: rgba(235, 240, 231, .42);
      font-size: clamp(1.05rem, 3vw, 1.45rem);
      font-weight: 650;
      text-align: center;
      pointer-events: none;
      transition: opacity .2s ease;
    }

    .empty-hint[hidden] {
      opacity: 0;
    }

    dialog {
      width: min(88vw, 440px);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 0;
      color: var(--ink);
      background: linear-gradient(145deg, #26211d, #0d0e10);
      box-shadow: 0 24px 80px rgba(0, 0, 0, .7);
    }

    dialog::backdrop {
      background: rgba(0, 0, 0, .72);
      backdrop-filter: blur(4px);
    }

    .dialog-content {
      padding: 24px;
    }

    .dialog-content h2 {
      margin: 0 0 8px;
      font-size: 1.45rem;
    }

    .dialog-content p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }

    .dialog-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      padding: 0 24px 24px;
    }

    .dialog-actions button {
      min-height: 54px;
      border: 1px solid rgba(255, 255, 255, .12);
      border-radius: 17px;
      color: var(--ink);
      background: rgba(255, 255, 255, .06);
      font-weight: 780;
    }

    .dialog-actions .confirm {
      color: #1b0c09;
      border-color: #ff8b80;
      background: #ff8b80;
    }

    @media (max-width: 620px) {
      .app {
        gap: 10px;
        padding: 10px;
      }

      .topbar {
        padding: 14px;
        border-radius: 20px;
      }

      .subtitle {
        display: none;
      }

      .note-card {
        padding: 10px 13px;
        border-radius: 20px;
      }

      .note-label {
        width: 44px;
        height: 44px;
        border-radius: 14px;
      }

      .toolbar {
        min-height: 68px;
        padding: 8px 10px;
      }

      .tool-button,
      .color-button,
      .size-button {
        min-width: 50px;
        min-height: 50px;
        border-radius: 15px;
      }
    }

    @media (max-height: 700px) {
      .app {
        gap: 8px;
        padding: 8px;
      }

      .topbar,
      .note-card {
        padding: 9px 12px;
        border-radius: 18px;
      }

      .subtitle {
        display: none;
      }

      .note-label {
        width: 40px;
        height: 40px;
        border-radius: 13px;
      }

      textarea {
        min-height: 44px;
      }

      .toolbar {
        min-height: 58px;
        padding: 5px 8px;
      }

      .tool-button,
      .color-button,
      .size-button {
        min-width: 46px;
        min-height: 46px;
        border-radius: 14px;
      }
    }

    @media (orientation: landscape) and (min-width: 900px) {
      .app {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        grid-template-rows: auto minmax(0, 1fr);
      }

      .topbar,
      .note-card {
        min-width: 0;
      }

      .board-shell {
        grid-column: 1 / -1;
      }
    }
  </style>

  <main class="app">
    <header class="topbar">
      <div class="title-group">
        <h1 data-i18n="title">Family Chalkboard</h1>
        <p class="subtitle" data-i18n="subtitle">
          Write or draw – everything saves automatically
        </p>
      </div>
      <div class="save-status" id="save-status" role="status" aria-live="polite">
        Loading…
      </div>
    </header>

    <section class="note-card" id="note-card" aria-label="Family note">
      <div class="note-label" aria-hidden="true">Aa</div>
      <textarea
        id="family-note"
        maxlength="1000"
        rows="2"
        aria-label="Family note"
        placeholder="Leave a small note for the family…"
      ></textarea>
    </section>

    <section class="board-shell" id="board-shell" aria-label="Drawing area">
      <nav class="toolbar" id="toolbar" aria-label="Drawing tools">
        <button class="tool-button" id="pen-tool" type="button" aria-pressed="true">
          Chalk
        </button>
        <button class="tool-button" id="eraser-tool" type="button" aria-pressed="false">
          Eraser
        </button>

        <span class="separator" aria-hidden="true"></span>

        <button class="color-button" type="button" data-color="#f3f1e8" data-label="white" style="--chalk-color:#f3f1e8" aria-label="White chalk" aria-pressed="true"></button>
        <button class="color-button" type="button" data-color="#f5cf68" data-label="yellow" style="--chalk-color:#f5cf68" aria-label="Yellow chalk" aria-pressed="false"></button>
        <button class="color-button" type="button" data-color="#f29ab2" data-label="pink" style="--chalk-color:#f29ab2" aria-label="Pink chalk" aria-pressed="false"></button>
        <button class="color-button" type="button" data-color="#82c7ef" data-label="blue" style="--chalk-color:#82c7ef" aria-label="Blue chalk" aria-pressed="false"></button>
        <button class="color-button" type="button" data-color="#9fd69b" data-label="green" style="--chalk-color:#9fd69b" aria-label="Green chalk" aria-pressed="false"></button>

        <span class="separator" aria-hidden="true"></span>

        <button class="size-button" type="button" data-size="4" data-label="thin" aria-label="Thin chalk" aria-pressed="false">
          <span class="size-dot" style="--dot-size:6px"></span>
        </button>
        <button class="size-button" type="button" data-size="8" data-label="medium" aria-label="Medium chalk" aria-pressed="true">
          <span class="size-dot" style="--dot-size:11px"></span>
        </button>
        <button class="size-button" type="button" data-size="15" data-label="thick" aria-label="Thick chalk" aria-pressed="false">
          <span class="size-dot" style="--dot-size:18px"></span>
        </button>

        <span class="separator" aria-hidden="true"></span>

        <button class="tool-button" id="undo-button" type="button" aria-label="Undo the latest stroke">
          Undo
        </button>
        <button class="tool-button" id="view-mode-button" type="button" aria-pressed="true">
          Fit
        </button>
        <button class="tool-button danger" id="clear-button" type="button">
          Clear
        </button>
      </nav>

      <div class="canvas-wrap" id="canvas-wrap">
        <div class="drawing-surface" id="drawing-surface">
          <canvas id="chalkboard" aria-label="Draw here with your finger"></canvas>
          <div class="empty-hint" id="empty-hint">
            Draw here with your finger ✦
          </div>
        </div>
      </div>
    </section>
  </main>

  <dialog id="clear-dialog">
    <div class="dialog-content">
      <h2 id="clear-title">Clear the whole board?</h2>
      <p id="clear-description">
        Both the drawing and the family note will be removed.
      </p>
    </div>
    <div class="dialog-actions">
      <button id="cancel-clear" type="button">Cancel</button>
      <button class="confirm" id="confirm-clear" type="button">Yes, clear</button>
    </div>
  </dialog>
`;

class FamilyChalkboardPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = TEMPLATE;

    this._hass = null;
    this._panel = null;
    this._narrow = false;
    this._loaded = false;
    this._connectInFlight = false;
    this._unsubscribe = null;
    this._board = {
      version: 2,
      note: "",
      canvas: { aspectRatio: null },
      strokes: [],
    };
    this._currentStroke = null;
    this._mode = "draw";
    this._color = "#f3f1e8";
    this._lineWidth = 8;
    this._saveTimer = null;
    this._saveInFlight = false;
    this._saveAgain = false;
    this._language = "en";
    this._viewMode = this._readViewMode();

    this._canvas = this.shadowRoot.getElementById("chalkboard");
    this._canvasWrap = this.shadowRoot.getElementById("canvas-wrap");
    this._drawingSurface = this.shadowRoot.getElementById("drawing-surface");
    this._context = this._canvas.getContext("2d");
    this._note = this.shadowRoot.getElementById("family-note");
    this._status = this.shadowRoot.getElementById("save-status");
    this._emptyHint = this.shadowRoot.getElementById("empty-hint");
    this._penTool = this.shadowRoot.getElementById("pen-tool");
    this._eraserTool = this.shadowRoot.getElementById("eraser-tool");
    this._undoButton = this.shadowRoot.getElementById("undo-button");
    this._viewModeButton = this.shadowRoot.getElementById("view-mode-button");
    this._clearButton = this.shadowRoot.getElementById("clear-button");
    this._clearDialog = this.shadowRoot.getElementById("clear-dialog");
    this._cancelClear = this.shadowRoot.getElementById("cancel-clear");
    this._confirmClear = this.shadowRoot.getElementById("confirm-clear");
    this._colorButtons = [
      ...this.shadowRoot.querySelectorAll(".color-button"),
    ];
    this._sizeButtons = [
      ...this.shadowRoot.querySelectorAll(".size-button"),
    ];

    this._resizeObserver = new ResizeObserver(() => this._redraw());
    this._viewportFrame = null;
    this._handleViewportResize = () => {
      this._updateViewportHeight();
      window.cancelAnimationFrame(this._viewportFrame);
      this._viewportFrame = window.requestAnimationFrame(() => this._redraw());
    };
    this._handleVisibility = () => {
      if (document.visibilityState === "hidden" && this._saveTimer) {
        this._saveBoard();
      }
    };

    this._bindEvents();
    this._applyTranslations();
    this._updateViewModeButton();
    this._setStatus("loading");
  }

  set hass(value) {
    const languageChanged =
      value?.language && value.language.slice(0, 2) !== this._language;
    this._hass = value;
    if (languageChanged) {
      this._selectLanguage();
      this._applyTranslations();
    }
    this._connect();
  }

  set panel(value) {
    this._panel = value;
  }

  set narrow(value) {
    this._narrow = Boolean(value);
  }

  connectedCallback() {
    this._updateViewportHeight();
    this._resizeObserver.observe(this._canvasWrap);
    window.addEventListener("resize", this._handleViewportResize);
    window.visualViewport?.addEventListener("resize", this._handleViewportResize);
    document.addEventListener("visibilitychange", this._handleVisibility);
    this._viewportFrame = window.requestAnimationFrame(() => {
      this._updateViewportHeight();
      this._redraw();
    });
    this._connect();
  }

  disconnectedCallback() {
    this._resizeObserver.disconnect();
    window.removeEventListener("resize", this._handleViewportResize);
    window.visualViewport?.removeEventListener(
      "resize",
      this._handleViewportResize,
    );
    document.removeEventListener("visibilitychange", this._handleVisibility);
    window.cancelAnimationFrame(this._viewportFrame);
    window.clearTimeout(this._saveTimer);
    if (this._unsubscribe) {
      this._unsubscribe();
      this._unsubscribe = null;
    }
  }

  _selectLanguage() {
    const parameter = new URLSearchParams(window.location.search).get("lang");
    const candidate =
      parameter || this._hass?.language || navigator.language || "en";
    this._language = candidate.toLowerCase().startsWith("sv") ? "sv" : "en";
  }

  _applyTranslations() {
    this._selectLanguage();
    const copy = TRANSLATIONS[this._language];
    this._copy = copy;
    this.shadowRoot.querySelector("[data-i18n='title']").textContent = copy.title;
    this.shadowRoot.querySelector("[data-i18n='subtitle']").textContent =
      copy.subtitle;
    this.shadowRoot
      .getElementById("note-card")
      .setAttribute("aria-label", copy.noteLabel);
    this._note.setAttribute("aria-label", copy.noteLabel);
    this._note.setAttribute("placeholder", copy.notePlaceholder);
    this.shadowRoot
      .getElementById("board-shell")
      .setAttribute("aria-label", copy.drawingArea);
    this.shadowRoot
      .getElementById("toolbar")
      .setAttribute("aria-label", copy.drawingTools);
    this._penTool.textContent = copy.chalk;
    this._eraserTool.textContent = copy.eraser;
    this._undoButton.textContent = copy.undo;
    this._undoButton.setAttribute("aria-label", copy.undoLabel);
    this._updateViewModeButton();
    this._clearButton.textContent = copy.clear;
    this._canvas.setAttribute("aria-label", copy.canvasLabel);
    this._emptyHint.textContent = copy.empty;
    this.shadowRoot.getElementById("clear-title").textContent = copy.clearTitle;
    this.shadowRoot.getElementById("clear-description").textContent =
      copy.clearDescription;
    this._cancelClear.textContent = copy.cancel;
    this._confirmClear.textContent = copy.confirm;
    this._colorButtons.forEach((button) => {
      button.setAttribute("aria-label", copy.colors[button.dataset.label]);
    });
    this._sizeButtons.forEach((button) => {
      button.setAttribute("aria-label", copy.sizes[button.dataset.label]);
    });
  }

  _setStatus(key, state = "ok") {
    this._status.textContent = this._copy[key] || key;
    this._status.dataset.state = state;
  }

  _updateViewportHeight() {
    const top = Math.max(0, this.getBoundingClientRect().top);
    const availableHeight = Math.max(320, window.innerHeight - top);
    this.style.setProperty(
      "--family-chalkboard-viewport-height",
      `${availableHeight}px`,
    );
  }

  _normalizeState(loaded) {
    const candidateRatio = Number(loaded?.canvas?.aspectRatio);
    const aspectRatio =
      Number.isFinite(candidateRatio) &&
      candidateRatio >= MIN_CANVAS_ASPECT_RATIO &&
      candidateRatio <= MAX_CANVAS_ASPECT_RATIO
        ? candidateRatio
        : null;
    return {
      version: 2,
      note: typeof loaded?.note === "string" ? loaded.note : "",
      canvas: { aspectRatio },
      strokes: Array.isArray(loaded?.strokes) ? loaded.strokes : [],
    };
  }

  _readViewMode() {
    try {
      return window.localStorage.getItem(VIEW_MODE_STORAGE_KEY) === "fill"
        ? "fill"
        : "fit";
    } catch (_error) {
      return "fit";
    }
  }

  _updateViewModeButton() {
    if (!this._viewModeButton || !this._copy) return;
    const isFit = this._viewMode === "fit";
    this._viewModeButton.textContent = isFit
      ? this._copy.viewFit
      : this._copy.viewFill;
    this._viewModeButton.setAttribute("aria-pressed", String(isFit));
    const label = isFit ? this._copy.viewFitLabel : this._copy.viewFillLabel;
    this._viewModeButton.setAttribute("aria-label", label);
    this._viewModeButton.setAttribute("title", label);
  }

  _setViewMode(mode) {
    this._viewMode = mode === "fill" ? "fill" : "fit";
    try {
      window.localStorage.setItem(VIEW_MODE_STORAGE_KEY, this._viewMode);
    } catch (_error) {
      // The preference remains active for this browser session.
    }
    this._updateViewModeButton();
    this._redraw();
  }

  _layoutDrawingSurface() {
    const rect = this._canvasWrap.getBoundingClientRect();
    let width = rect.width;
    let height = rect.height;
    let left = 0;
    let top = 0;
    const aspectRatio = this._board.canvas?.aspectRatio;

    if (
      this._viewMode === "fit" &&
      Number.isFinite(aspectRatio) &&
      aspectRatio > 0 &&
      rect.width > 0 &&
      rect.height > 0
    ) {
      if (rect.width / rect.height > aspectRatio) {
        width = rect.height * aspectRatio;
        left = (rect.width - width) / 2;
      } else {
        height = rect.width / aspectRatio;
        top = (rect.height - height) / 2;
      }
    }

    this._drawingSurface.style.left = `${left}px`;
    this._drawingSurface.style.top = `${top}px`;
    this._drawingSurface.style.width = `${Math.max(0, width)}px`;
    this._drawingSurface.style.height = `${Math.max(0, height)}px`;
  }

  _lockCanvasAspectRatio() {
    if (this._board.canvas?.aspectRatio) return;
    const rect = this._canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    this._board.canvas = {
      aspectRatio: Math.round((rect.width / rect.height) * 10000) / 10000,
    };
  }

  async _connect() {
    if (!this.isConnected || !this._hass || this._connectInFlight) return;

    if (this._loaded) {
      await this._subscribe();
      return;
    }

    this._connectInFlight = true;
    try {
      const loaded = await this._hass.callWS({
        type: "family_chalkboard/state/get",
      });
      this._board = this._normalizeState(loaded);
      this._note.value = this._board.note;
      this._loaded = true;
      this._redraw();
      this._setStatus("saved");
      await this._subscribe();
    } catch (error) {
      console.error("Family Chalkboard could not load state", error);
      this._redraw();
      this._setStatus("loadError", "error");
    } finally {
      this._connectInFlight = false;
    }
  }

  async _subscribe() {
    if (!this.isConnected || !this._hass || this._unsubscribe) return;
    try {
      const unsubscribe = await this._hass.connection.subscribeMessage(
        (state) => {
          if (this._currentStroke) return;
          this._board = this._normalizeState(state);
          if (this.shadowRoot.activeElement !== this._note) {
            this._note.value = this._board.note;
          }
          this._redraw();
        },
        { type: "family_chalkboard/state/subscribe" },
      );
      if (this.isConnected) {
        this._unsubscribe = unsubscribe;
      } else {
        unsubscribe();
      }
    } catch (error) {
      console.error("Family Chalkboard live updates are unavailable", error);
    }
  }

  _normalizedPoint(event) {
    const rect = this._canvas.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
    };
  }

  _renderStroke(stroke) {
    const rect = this._canvas.getBoundingClientRect();
    if (!stroke.points?.length || !rect.width || !rect.height) return;

    this._context.save();
    this._context.globalCompositeOperation =
      stroke.mode === "erase" ? "destination-out" : "source-over";
    this._context.strokeStyle = stroke.color || "#f3f1e8";
    this._context.fillStyle = stroke.color || "#f3f1e8";
    this._context.lineWidth = stroke.width || 8;
    this._context.lineCap = "round";
    this._context.lineJoin = "round";

    const first = stroke.points[0];
    const firstX = first.x * rect.width;
    const firstY = first.y * rect.height;

    if (stroke.points.length === 1) {
      this._context.beginPath();
      this._context.arc(
        firstX,
        firstY,
        this._context.lineWidth / 2,
        0,
        Math.PI * 2,
      );
      this._context.fill();
      this._context.restore();
      return;
    }

    this._context.beginPath();
    this._context.moveTo(firstX, firstY);
    for (let index = 1; index < stroke.points.length; index += 1) {
      const point = stroke.points[index];
      this._context.lineTo(point.x * rect.width, point.y * rect.height);
    }
    this._context.stroke();
    this._context.restore();
  }

  _redraw() {
    this._layoutDrawingSurface();
    const rect = this._canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rect.width * dpr));
    const height = Math.max(1, Math.round(rect.height * dpr));

    if (this._canvas.width !== width || this._canvas.height !== height) {
      this._canvas.width = width;
      this._canvas.height = height;
    }

    this._context.setTransform(dpr, 0, 0, dpr, 0, 0);
    this._context.clearRect(0, 0, rect.width, rect.height);
    this._board.strokes.forEach((stroke) => this._renderStroke(stroke));
    this._emptyHint.hidden = this._board.strokes.length > 0;
  }

  _drawLatestSegment(stroke) {
    if (stroke.points.length < 2) {
      this._renderStroke(stroke);
      return;
    }
    this._renderStroke({
      ...stroke,
      points: stroke.points.slice(-2),
    });
  }

  _scheduleSave() {
    this._setStatus("saving");
    window.clearTimeout(this._saveTimer);
    this._saveTimer = window.setTimeout(() => this._saveBoard(), 450);
  }

  async _saveBoard() {
    window.clearTimeout(this._saveTimer);
    this._saveTimer = null;

    if (!this._hass) {
      this._setStatus("saveError", "error");
      return;
    }
    if (this._saveInFlight) {
      this._saveAgain = true;
      return;
    }

    this._saveInFlight = true;
    const state = JSON.parse(JSON.stringify(this._board));
    try {
      await this._hass.callWS({
        type: "family_chalkboard/state/save",
        state,
      });
      this._setStatus("saved");
    } catch (error) {
      console.error("Family Chalkboard could not save state", error);
      this._setStatus("saveError", "error");
    } finally {
      this._saveInFlight = false;
      if (this._saveAgain) {
        this._saveAgain = false;
        this._saveBoard();
      }
    }
  }

  _beginStroke(event) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    event.preventDefault();
    this._lockCanvasAspectRatio();
    this._canvas.setPointerCapture(event.pointerId);
    this._currentStroke = {
      mode: this._mode,
      color: this._color,
      width:
        this._mode === "erase" ? this._lineWidth * 2.6 : this._lineWidth,
      points: [this._normalizedPoint(event)],
    };
    this._board.strokes.push(this._currentStroke);
    this._drawLatestSegment(this._currentStroke);
    this._emptyHint.hidden = true;
  }

  _continueStroke(event) {
    if (
      !this._currentStroke ||
      !this._canvas.hasPointerCapture(event.pointerId)
    ) {
      return;
    }
    event.preventDefault();
    const events = event.getCoalescedEvents
      ? event.getCoalescedEvents()
      : [event];
    events.forEach((item) => {
      this._currentStroke.points.push(this._normalizedPoint(item));
      this._drawLatestSegment(this._currentStroke);
    });
  }

  _endStroke(event) {
    if (!this._currentStroke) return;
    event.preventDefault();
    if (this._canvas.hasPointerCapture(event.pointerId)) {
      this._canvas.releasePointerCapture(event.pointerId);
    }
    this._currentStroke = null;
    this._scheduleSave();
  }

  _setMode(nextMode) {
    this._mode = nextMode;
    this._penTool.setAttribute(
      "aria-pressed",
      String(this._mode === "draw"),
    );
    this._eraserTool.setAttribute(
      "aria-pressed",
      String(this._mode === "erase"),
    );
  }

  _bindEvents() {
    this._penTool.addEventListener("click", () => this._setMode("draw"));
    this._eraserTool.addEventListener("click", () => this._setMode("erase"));

    this._colorButtons.forEach((button) => {
      button.addEventListener("click", () => {
        this._color = button.dataset.color;
        this._setMode("draw");
        this._colorButtons.forEach((item) => {
          item.setAttribute("aria-pressed", String(item === button));
        });
      });
    });

    this._sizeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        this._lineWidth = Number(button.dataset.size);
        this._sizeButtons.forEach((item) => {
          item.setAttribute("aria-pressed", String(item === button));
        });
      });
    });

    this._undoButton.addEventListener("click", () => {
      if (!this._board.strokes.length) return;
      this._board.strokes.pop();
      this._redraw();
      this._scheduleSave();
    });

    this._viewModeButton.addEventListener("click", () => {
      this._setViewMode(this._viewMode === "fit" ? "fill" : "fit");
    });

    this._clearButton.addEventListener("click", () => {
      this._clearDialog.showModal();
    });
    this._cancelClear.addEventListener("click", () => {
      this._clearDialog.close();
    });
    this._confirmClear.addEventListener("click", () => {
      this._board.note = "";
      this._board.canvas = { aspectRatio: null };
      this._board.strokes = [];
      this._note.value = "";
      this._redraw();
      this._clearDialog.close();
      this._scheduleSave();
    });

    this._note.addEventListener("input", () => {
      this._board.note = this._note.value;
      this._scheduleSave();
    });

    this._canvas.addEventListener("pointerdown", (event) => {
      this._beginStroke(event);
    });
    this._canvas.addEventListener("pointermove", (event) => {
      this._continueStroke(event);
    });
    this._canvas.addEventListener("pointerup", (event) => {
      this._endStroke(event);
    });
    this._canvas.addEventListener("pointercancel", (event) => {
      this._endStroke(event);
    });
  }
}

if (!customElements.get("family-chalkboard-panel")) {
  customElements.define("family-chalkboard-panel", FamilyChalkboardPanel);
}
