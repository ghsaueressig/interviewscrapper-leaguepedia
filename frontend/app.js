const API_URL = "https://interviewscrapper-leaguepedia.onrender.com";

const MAX_URLS = 10;

const urlsInput = document.getElementById("urls");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const scrapeButton = document.getElementById("scrape");
const clearButton = document.getElementById("clear");
const languageSelect = document.getElementById("language");
const urlCountEl = document.getElementById("url-count");
const limitWarningEl = document.getElementById("limit-warning");

let isProcessing = false;


/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {
  "pt-BR": {
    subtitle: "Cole os links das matérias/vídeos e gere automaticamente o template ExternalContent/Line. Exclusivamente para o CBLOL.",
    languageLabel: "Idioma",
    linksLabel: "Links das matérias/vídeos",

    urlsPlaceholder: `Cole um link por linha.

Ex.:
https://maisesports.com.br/...
https://sheepesports.com/...
https://youtube.com/...`,

    hint: "Publicação, torneio, tipo de conteúdo, tradutor e vídeo são detectados automaticamente.",

    generateButton: "Gerar Templates",
    clearButton: "Limpar",

    apiNote: `Para evitar uso excessivo da ferramenta, é possível processar até ${MAX_URLS} links por vez.`,

    publication: "Publicação",
    type: "Tipo",
    tournament: "Torneio",
    players: "Jogador(es)",
    teams: "Equipe(s)",
    date: "Data",
    translator: "Tradutor",
    video: "Vídeo",

    unknownPublication: "Desconhecida",
    unknownType: "Desconhecido",
    unknownTournament: "Não identificado",
    unknownPlayers: "Não identificado",
    unknownTeams: "Não identificada",
    unknownDate: "Não identificada",
    noTranslator: "Nenhum",

    yes: "Sim",
    no: "Não",

    copyTemplate: "Copiar template",
    copied: "Copiado!",

    noUrls: "Cole pelo menos uma URL.",
    tooManyUrls: `O limite é de ${MAX_URLS} links por vez.`,
    processing: "Processando {count} link(s)...",
    processingDisabled: "Processando...",
    processed: "{success} processado(s)",
    withErrors: "; {failed} com erro.",
    error: "Erro: {message}",

    dateHeading: "📅 DATA: {date}",

    urlCount: "{count} / " + MAX_URLS,
    limitWarning: `⚠️ Máximo de ${MAX_URLS} links por requisição.`,

    unsupportedType: "Não identificado"
  },


  en: {
    subtitle: "Paste article/video links and automatically generate the ExternalContent/Line template. Exclusively for CBLOL..",
    languageLabel: "Language",
    linksLabel: "Article/video links",

    urlsPlaceholder: `Paste one link per line.

Example:
https://maisesports.com.br/...
https://sheepesports.com/...
https://youtube.com/...`,

    hint: "Publication, tournament, content type, translator and video status are detected automatically.",

    generateButton: "Generate Templates",
    clearButton: "Clear",

    apiNote: `To help prevent excessive use, you can process up to ${MAX_URLS} links at a time.`,

    publication: "Publication",
    type: "Type",
    tournament: "Tournament",
    players: "Player(s)",
    teams: "Team(s)",
    date: "Date",
    translator: "Translator",
    video: "Video",

    unknownPublication: "Unknown",
    unknownType: "Unknown",
    unknownTournament: "Not identified",
    unknownPlayers: "Not identified",
    unknownTeams: "Not identified",
    unknownDate: "Not identified",
    noTranslator: "None",

    yes: "Yes",
    no: "No",

    copyTemplate: "Copy template",
    copied: "Copied!",

    noUrls: "Paste at least one URL.",
    tooManyUrls: `The limit is ${MAX_URLS} links at a time.`,
    processing: "Processing {count} link(s)...",
    processingDisabled: "Processing...",
    processed: "{success} processed",
    withErrors: "; {failed} with errors.",
    error: "Error: {message}",

    dateHeading: "📅 DATE: {date}",

    urlCount: "{count} / " + MAX_URLS,
    limitWarning: `⚠️ Maximum of ${MAX_URLS} links per request.`,

    unsupportedType: "Not identified"
  },


  es: {
    subtitle: "Pega los enlaces de artículos/videos y genera automáticamente la plantilla ExternalContent/Line. Exclusivamente para CBLOL.",
    languageLabel: "Idioma",
    linksLabel: "Enlaces de artículos/videos",

    urlsPlaceholder: `Pega un enlace por línea.

Ejemplo:
https://maisesports.com.br/...
https://sheepesports.com/...
https://youtube.com/...`,

    hint: "La publicación, torneo, tipo de contenido, traductor y estado de vídeo se detectan automáticamente.",

    generateButton: "Generar plantillas",
    clearButton: "Limpiar",

    apiNote: `Para ayudar a evitar un uso excesivo, puedes procesar hasta ${MAX_URLS} enlaces a la vez.`,

    publication: "Publicación",
    type: "Tipo",
    tournament: "Torneo",
    players: "Jugador(es)",
    teams: "Equipo(s)",
    date: "Fecha",
    translator: "Traductor",
    video: "Vídeo",

    unknownPublication: "Desconocida",
    unknownType: "Desconocido",
    unknownTournament: "No identificado",
    unknownPlayers: "No identificado",
    unknownTeams: "No identificado",
    unknownDate: "No identificada",
    noTranslator: "Ninguno",

    yes: "Sí",
    no: "No",

    copyTemplate: "Copiar plantilla",
    copied: "¡Copiado!",

    noUrls: "Pega al menos una URL.",
    tooManyUrls: `El límite es de ${MAX_URLS} enlaces a la vez.`,
    processing: "Procesando {count} enlace(s)...",
    processingDisabled: "Procesando...",
    processed: "{success} procesado(s)",
    withErrors: "; {failed} con errores.",
    error: "Error: {message}",

    dateHeading: "📅 FECHA: {date}",

    urlCount: "{count} / " + MAX_URLS,
    limitWarning: `⚠️ Máximo de ${MAX_URLS} enlaces por solicitud.`,

    unsupportedType: "No identificado"
  },


  fr: {
    subtitle: "Collez les liens des articles/vidéos et générez automatiquement le modèle ExternalContent/Line. Exclusivement pour le CBLOL.",
    languageLabel: "Langue",
    linksLabel: "Liens des articles/vidéos",

    urlsPlaceholder: `Collez un lien par ligne.

Exemple :
https://maisesports.com.br/...
https://sheepesports.com/...
https://youtube.com/...`,

    hint: "La publication, le tournoi, le type de contenu, le traducteur et le statut vidéo sont détectés automatiquement.",

    generateButton: "Générer les modèles",
    clearButton: "Effacer",

    apiNote: `Afin d'éviter une utilisation excessive, vous pouvez traiter jusqu'à ${MAX_URLS} liens à la fois.`,

    publication: "Publication",
    type: "Type",
    tournament: "Tournoi",
    players: "Joueur(s)",
    teams: "Équipe(s)",
    date: "Date",
    translator: "Traducteur",
    video: "Vidéo",

    unknownPublication: "Inconnue",
    unknownType: "Inconnu",
    unknownTournament: "Non identifié",
    unknownPlayers: "Non identifié",
    unknownTeams: "Non identifiée",
    unknownDate: "Non identifiée",
    noTranslator: "Aucun",

    yes: "Oui",
    no: "Non",

    copyTemplate: "Copier le modèle",
    copied: "Copié !",

    noUrls: "Collez au moins une URL.",
    tooManyUrls: `La limite est de ${MAX_URLS} liens à la fois.`,
    processing: "Traitement de {count} lien(s)...",
    processingDisabled: "Traitement...",
    processed: "{success} traité(s)",
    withErrors: "; {failed} avec erreur.",
    error: "Erreur : {message}",

    dateHeading: "📅 DATE : {date}",

    urlCount: "{count} / " + MAX_URLS,
    limitWarning: `⚠️ Maximum de ${MAX_URLS} liens par requête.`,

    unsupportedType: "Non identifié"
  }
};


/* =========================================================
   LANGUAGE
========================================================= */

function getLanguage() {
  return localStorage.getItem("leaguepedia-scraper-language") || "pt-BR";
}

function t(key, replacements = {}) {
  const language = getLanguage();
  let text = translations[language]?.[key]
    ?? translations["pt-BR"][key]
    ?? key;

  for (const [keyName, value] of Object.entries(replacements)) {
    text = text.replace(`{${keyName}}`, value);
  }

  return text;
}

function applyLanguage() {
  const language = getLanguage();

  document.documentElement.lang = language;
  languageSelect.value = language;

  document.querySelectorAll("[data-i18n]").forEach(element => {
    const key = element.dataset.i18n;

    // Mantém o <code>ExternalContent/Line</code intacto
    if (key === "subtitle") {
      element.innerHTML = `${t(key).replace(
        "ExternalContent/Line",
        "<code>ExternalContent/Line</code>"
      )}`;
    } else {
      element.textContent = t(key);
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(element => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });

  updateUrlCount();
}

languageSelect.addEventListener("change", () => {
  localStorage.setItem(
    "leaguepedia-scraper-language",
    languageSelect.value
  );

  applyLanguage();
});


/* =========================================================
   URL LIMIT
========================================================= */

function getUrls() {
  return urlsInput.value
    .split("\n")
    .map(url => url.trim())
    .filter(Boolean);
}

function updateUrlCount() {
  const urls = getUrls();
  const count = urls.length;

  urlCountEl.textContent = t("urlCount", { count });

  if (count > MAX_URLS) {
    urlCountEl.classList.add("limit-exceeded");

    limitWarningEl.textContent = t("tooManyUrls");

    scrapeButton.disabled = true;
  } else {
    urlCountEl.classList.remove("limit-exceeded");

    limitWarningEl.textContent =
      count === MAX_URLS ? t("limitWarning") : "";

    scrapeButton.disabled = isProcessing;
  }
}

urlsInput.addEventListener("input", updateUrlCount);


/* =========================================================
   DETECTED INFO
========================================================= */

function addDetectedInfo(wrapper, item) {
  const info = document.createElement("div");
  info.className = "detected-info";

  const values = [
    ["publication", item.publication || t("unknownPublication")],
    ["type", item.type || t("unknownType")],
    ["tournament", item.tournament || t("unknownTournament")],
    ["players", item.players || t("unknownPlayers")],
    ["teams", item.teams || t("unknownTeams")],
    ["date", item.date || t("unknownDate")],
    ["translator", item.translator || t("noTranslator")],
    ["video", item.isvideo === "Yes" ? t("yes") : t("no")]
  ];

  for (const [labelKey, value] of values) {
    const span = document.createElement("span");

    const strong = document.createElement("strong");
    strong.textContent = `${t(labelKey)}: `;

    span.appendChild(strong);
    span.appendChild(document.createTextNode(value));

    info.appendChild(span);
  }

  wrapper.appendChild(info);
}


/* =========================================================
   SCRAPE
========================================================= */

scrapeButton.addEventListener("click", async () => {

  if (isProcessing) {
    return;
  }

  const urls = getUrls();

  if (!urls.length) {
    statusEl.textContent = t("noUrls");
    return;
  }

  if (urls.length > MAX_URLS) {
    statusEl.textContent = t("tooManyUrls");
    return;
  }

  isProcessing = true;

  scrapeButton.disabled = true;
  scrapeButton.textContent = t("processingDisabled");

  statusEl.textContent = t("processing", {
    count: urls.length
  });

  resultsEl.innerHTML = "";

  try {

    const response = await fetch(`${API_URL}/api/scrape`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ urls })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error || "Unknown error."
      );
    }

    const failed = data.results.filter(item => item.error);
    const successful = data.results.filter(item => !item.error);

    statusEl.textContent =
      t("processed", {
        success: successful.length
      }) +
      (failed.length
        ? t("withErrors", {
            failed: failed.length
          })
        : ".");


    /* Results grouped by date */

    for (const [date, items] of Object.entries(data.grouped)) {

      const section = document.createElement("section");
      section.className = "result-card";

      const heading = document.createElement("h2");
      heading.textContent = t("dateHeading", { date });

      section.appendChild(heading);


      for (const item of items) {

        const wrapper = document.createElement("div");
        wrapper.className = "result";


        /* Title */

        const title = document.createElement("strong");
        title.textContent = item.title || item.url;

        wrapper.appendChild(title);


        /* Detected information */

        addDetectedInfo(wrapper, item);


        /* Template */

        const textarea = document.createElement("textarea");

        textarea.readOnly = true;
        textarea.value = item.template;

        wrapper.appendChild(textarea);


        /* Copy button */

        const copy = document.createElement("button");

        copy.className = "copy";
        copy.textContent = t("copyTemplate");

        copy.addEventListener("click", async () => {

          await navigator.clipboard.writeText(item.template);

          copy.textContent = t("copied");

          setTimeout(() => {
            copy.textContent = t("copyTemplate");
          }, 1200);

        });

        wrapper.appendChild(copy);

        section.appendChild(wrapper);

      }

      resultsEl.appendChild(section);

    }


    /* Failed URLs */

    for (const item of failed) {

      const error = document.createElement("div");

      error.className = "error";

      error.textContent =
        `${item.url}: ${item.error}`;

      resultsEl.appendChild(error);

    }

  } catch (error) {

    statusEl.textContent = t("error", {
      message: error.message
    });

  } finally {

    isProcessing = false;

    scrapeButton.textContent = t("generateButton");

    updateUrlCount();

  }

});


/* =========================================================
   CLEAR
========================================================= */

clearButton.addEventListener("click", () => {

  urlsInput.value = "";

  resultsEl.innerHTML = "";

  statusEl.textContent = "";

  limitWarningEl.textContent = "";

  updateUrlCount();

});


/* =========================================================
   INITIALIZATION
========================================================= */

applyLanguage();
