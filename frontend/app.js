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
   THEME
========================================================= */

const themeToggle = document.getElementById(
  "theme-toggle"
);


function applyTheme(theme) {
  const nextTheme = theme === "light"
    ? "light"
    : "dark";

  document.body.classList.remove(
    "dark-theme",
    "light-theme"
  );

  document.body.classList.add(
    nextTheme === "light"
      ? "light-theme"
      : "dark-theme"
  );

  localStorage.setItem(
    "theme",
    nextTheme
  );

  updateThemeButton();
}


function updateThemeButton() {
  if (!themeToggle) {
    return;
  }

  const isLight = document.body.classList.contains(
    "light-theme"
  );

  const label = t(
    isLight
      ? "themeToDark"
      : "themeToLight"
  );

  themeToggle.setAttribute(
    "aria-label",
    label
  );

  themeToggle.title = label;

  themeToggle.setAttribute(
    "aria-pressed",
    isLight
      ? "false"
      : "true"
  );
}


function loadTheme() {
  const savedTheme = localStorage.getItem(
    "theme"
  );

  applyTheme(
    savedTheme === "light"
      ? "light"
      : "dark"
  );
}


if (themeToggle) {
  themeToggle.addEventListener(
    "click",
    () => {
      const isLight = document.body.classList.contains(
        "light-theme"
      );

      applyTheme(
        isLight
          ? "dark"
          : "light"
      );
    }
  );
}


/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {
  "pt-BR": {
    subtitle: "Cole os links das matérias/vídeos e gere automaticamente o template ExternalContent/Line.",
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

    apiNote: `Para evitar uso excessivo da ferramenta, é possível processar até ${MAX_URLS} links por vez. Atualmente exclusivamente para CBLOL.`,

    publication: "Publicação",
    type: "Tipo",
    tournament: "Torneio",
    series: "Série / Quadro",
    players: "Jogador(es)",
    teams: "Equipe(s)",
    date: "Data",
    translator: "Tradutor",
    video: "Vídeo",
    author: "Autor",
    title: "Título",
    url: "URL",

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

    edit: "Editar informações",
    save: "Salvar alterações",
    cancel: "Cancelar",
    editing: "Edição manual",
    editHint: "As alterações são aplicadas somente a este template.",

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

    unsupportedType: "Não identificado",

    usedUrlTitle: "URL já processada",
    usedUrlsTitle: "{count} URLs já processadas",
    usedUrlLead: "Esta URL já foi processada anteriormente:",
    usedUrlsLead: "Estas URLs já foram processadas anteriormente:",
    usedUrlQuestion: "Deseja processá-la novamente?",
    usedUrlsQuestion: "Deseja processá-las novamente?",
    confirmProcessAgain: "Processar novamente",
    processingCancelled: "Processamento cancelado.",

    fuzzyTitle: "Possível nickname encontrado",
    fuzzyLead: "O termo \"{term}\" pode ser um nickname de jogador.",
    fuzzyQuestion: "Selecione a opção correta:",
    fuzzyNone: "Nenhum desses",
    fuzzyConfirm: "Confirmar",
    fuzzyTeam: "Equipe",
    fuzzyConfidence: "Confiança",
    fuzzyUseDetected: "Usar o nickname encontrado",

    rememberPlayerAliasTitle: "Memorizar correção de jogador?",
    rememberPlayerAliasQuestion: "Deseja lembrar esta correção para resultados futuros?",
    rememberPlayerAliasNo: "Agora não",
    rememberPlayerAliasYes: "Memorizar",

    rememberKnownPlayer: "🧠 Memorizar",
    knownPlayerRemembered: "✓ Memorizado",
    knownPlayerTitle: "Memorizar jogador?",
    knownPlayersTitle: "Memorizar jogadores?",
    knownPlayerQuestion: "Este jogador será reconhecido como um valor validado no futuro.",
    knownPlayersQuestion: "Estes jogadores serão reconhecidos como valores validados no futuro.",
    knownPlayerCancel: "Cancelar",

    appTools: "TOOLS",
    heroEyebrow: "EXTERNAL CONTENT",
    heroTitle: "Interview Scraper",
    heroDescription: "Cole os links das matérias/vídeos e gere automaticamente o template ExternalContent/Line.",
    workflowProcess: "PROCESSAR",
    workflowProcessDesc: "Cole os links e extraia as informações automaticamente.",
    workflowReview: "REVISAR",
    workflowReviewDesc: "Confira os dados detectados e faça ajustes se necessário.",
    workflowGenerate: "GERAR",
    workflowGenerateDesc: "Exporte os templates prontos para copiar na wiki.",
    workflowFinish: "FINALIZAR",
    workflowFinishDesc: "Revise o resultado final antes de utilizar o template.",
    processingHeading: "PROCESSAMENTO",
    resultsHeading: "RESULTADOS",
    resultsCountEmpty: "0 entrevistas",
    resultsEmptyDescription: "Nenhuma entrevista processada ainda.",
    resultsCountZero: "{count} entrevistas",
    resultsCountOne: "{count} entrevista",
    resultsCountOther: "{count} entrevistas",
    resultsEmptyHint: "Adicione os links no painel ao lado e clique em Gerar Templates.",
    themeToLight: "Ativar modo claro",
    themeToDark: "Ativar modo escuro",
    knownPlayerConfirm: "Memorizar"
  },


  en: {
    subtitle: "Paste article/video links and automatically generate the ExternalContent/Line template.",
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

    apiNote: `To help prevent excessive use, you can process up to ${MAX_URLS} links at a time. Currently CBLOL exclusive.`,

    publication: "Publication",
    type: "Type",
    tournament: "Tournament",
    series: "Series / Show",
    players: "Player(s)",
    teams: "Team(s)",
    date: "Date",
    translator: "Translator",
    video: "Video",
    author: "Author",
    title: "Title",
    url: "URL",

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

    edit: "Edit information",
    save: "Save changes",
    cancel: "Cancel",
    editing: "Manual editing",
    editHint: "Changes apply only to this template.",

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

    unsupportedType: "Not identified",

    usedUrlTitle: "URL already processed",
    usedUrlsTitle: "{count} URLs already processed",
    usedUrlLead: "This URL was already processed before:",
    usedUrlsLead: "These URLs were already processed before:",
    usedUrlQuestion: "Do you want to process it again?",
    usedUrlsQuestion: "Do you want to process them again?",
    confirmProcessAgain: "Process again",
    processingCancelled: "Processing cancelled.",

    fuzzyTitle: "Possible nickname found",
    fuzzyLead: "The term \"{term}\" may be a player nickname.",
    fuzzyQuestion: "Select the correct option:",
    fuzzyNone: "None of these",
    fuzzyConfirm: "Confirm",
    fuzzyTeam: "Team",
    fuzzyConfidence: "Confidence",
    fuzzyUseDetected: "Use detected nickname",

    rememberPlayerAliasTitle: "Remember player correction?",
    rememberPlayerAliasQuestion: "Would you like to remember this correction for future results?",
    rememberPlayerAliasNo: "Not now",
    rememberPlayerAliasYes: "Remember",

    rememberKnownPlayer: "🧠 Remember",
    knownPlayerRemembered: "✓ Remembered",
    knownPlayerTitle: "Remember player?",
    knownPlayersTitle: "Remember players?",
    knownPlayerQuestion: "This player will be recognized as a validated value in the future.",
    knownPlayersQuestion: "These players will be recognized as validated values in the future.",
    knownPlayerCancel: "Cancel",

    appTools: "TOOLS",
    heroEyebrow: "EXTERNAL CONTENT",
    heroTitle: "Interview Scraper",
    heroDescription: "Paste article/video links and automatically generate the ExternalContent/Line template.",
    workflowProcess: "PROCESS",
    workflowProcessDesc: "Paste links and automatically extract their information.",
    workflowReview: "REVIEW",
    workflowReviewDesc: "Review the detected data and make adjustments if necessary.",
    workflowGenerate: "GENERATE",
    workflowGenerateDesc: "Export templates ready to copy to the wiki.",
    workflowFinish: "FINISH",
    workflowFinishDesc: "Review the final result before using the template.",
    processingHeading: "PROCESSING",
    resultsHeading: "RESULTS",
    resultsCountEmpty: "0 interviews",
    resultsEmptyDescription: "No interviews processed yet.",
    resultsCountZero: "{count} interviews",
    resultsCountOne: "{count} interview",
    resultsCountOther: "{count} interviews",
    resultsEmptyHint: "Add the links in the side panel and click Generate Templates.",
    themeToLight: "Switch to light mode",
    themeToDark: "Switch to dark mode",
    knownPlayerConfirm: "Remember"
  },


  es: {
    subtitle: "Pega los enlaces de artículos/videos y genera automáticamente la plantilla ExternalContent/Line.",
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
    series: "Serie / Programa",
    players: "Jugador(es)",
    teams: "Equipo(s)",
    date: "Fecha",
    translator: "Traductor",
    video: "Vídeo",
    author: "Autor",
    title: "Título",
    url: "URL",

    unknownPublication: "Desconocida",
    unknownType: "Desconocido",
    unknownTournament: "No identificado",
    unknownPlayers: "No identificado",
    unknownTeams: "No identificados",
    unknownDate: "No identificada",
    noTranslator: "Ninguno",

    yes: "Sí",
    no: "No",

    copyTemplate: "Copiar plantilla",
    copied: "¡Copiado!",

    edit: "Editar información",
    save: "Guardar cambios",
    cancel: "Cancelar",
    editing: "Edición manual",
    editHint: "Los cambios se aplican solamente a esta plantilla.",

    noUrls: "Pega al menos una URL.",
    tooManyUrls: `El límite es ${MAX_URLS} enlaces a la vez.`,
    processing: "Procesando {count} enlace(s)...",
    processingDisabled: "Procesando...",
    processed: "{success} procesado(s)",
    withErrors: "; {failed} con errores.",
    error: "Error: {message}",

    dateHeading: "📅 FECHA: {date}",

    urlCount: "{count} / " + MAX_URLS,
    limitWarning: `⚠️ Máximo de ${MAX_URLS} enlaces por solicitud.`,

    unsupportedType: "No identificado",

    usedUrlTitle: "URL ya procesada",
    usedUrlsTitle: "{count} URLs ya procesadas",
    usedUrlLead: "Esta URL ya fue procesada anteriormente:",
    usedUrlsLead: "Estas URLs ya fueron procesadas anteriormente:",
    usedUrlQuestion: "¿Deseas procesarla de nuevo?",
    usedUrlsQuestion: "¿Deseas procesarlas de nuevo?",
    confirmProcessAgain: "Procesar de nuevo",
    processingCancelled: "Procesamiento cancelado.",

    fuzzyTitle: "Posible nickname encontrado",
    fuzzyLead: "El término \"{term}\" puede ser un nickname de jugador.",
    fuzzyQuestion: "Selecciona la opción correcta:",
    fuzzyNone: "Ninguno de estos",
    fuzzyConfirm: "Confirmar",
    fuzzyTeam: "Equipo",
    fuzzyConfidence: "Confianza",
    fuzzyUseDetected: "Usar el apodo encontrado",

    rememberPlayerAliasTitle: "¿Recordar la corrección del jugador?",
    rememberPlayerAliasQuestion: "¿Quieres recordar esta corrección para futuros resultados?",
    rememberPlayerAliasNo: "Ahora no",
    rememberPlayerAliasYes: "Recordar",

    rememberKnownPlayer: "🧠 Recordar",
    knownPlayerRemembered: "✓ Recordado",
    knownPlayerTitle: "¿Recordar al jugador?",
    knownPlayersTitle: "¿Recordar a los jugadores?",
    knownPlayerQuestion: "Este jugador se reconocerá como un valor validado en el futuro.",
    knownPlayersQuestion: "Estos jugadores se reconocerán como valores validados en el futuro.",
    knownPlayerCancel: "Cancelar",

    appTools: "TOOLS",
    heroEyebrow: "CONTENIDO EXTERNO",
    heroTitle: "Interview Scraper",
    heroDescription: "Pega los enlaces de artículos/videos y genera automáticamente la plantilla ExternalContent/Line.",
    workflowProcess: "PROCESAR",
    workflowProcessDesc: "Pega los enlaces y extrae la información automáticamente.",
    workflowReview: "REVISAR",
    workflowReviewDesc: "Revisa los datos detectados y realiza ajustes si es necesario.",
    workflowGenerate: "GENERAR",
    workflowGenerateDesc: "Exporta las plantillas listas para copiar en la wiki.",
    workflowFinish: "FINALIZAR",
    workflowFinishDesc: "Revisa el resultado final antes de utilizar la plantilla.",
    processingHeading: "PROCESAMIENTO",
    resultsHeading: "RESULTADOS",
    resultsCountEmpty: "0 entrevistas",
    resultsEmptyDescription: "Todavía no se ha procesado ninguna entrevista.",
    resultsCountZero: "{count} entrevistas",
    resultsCountOne: "{count} entrevista",
    resultsCountOther: "{count} entrevistas",
    resultsEmptyHint: "Añade los enlaces en el panel de al lado y haz clic en Generar plantillas.",
    themeToLight: "Activar modo claro",
    themeToDark: "Activar modo oscuro",
    knownPlayerConfirm: "Recordar"
  },


  fr: {
    subtitle: "Collez les liens des articles/vidéos et générez automatiquement le modèle ExternalContent/Line.",
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
    series: "Série / Émission",
    players: "Joueur(s)",
    teams: "Équipe(s)",
    date: "Date",
    translator: "Traducteur",
    video: "Vidéo",
    author: "Auteur",
    title: "Titre",
    url: "URL",

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

    edit: "Modifier les informations",
    save: "Enregistrer les modifications",
    cancel: "Annuler",
    editing: "Modification manuelle",
    editHint: "Les modifications s'appliquent uniquement à ce modèle.",

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

    unsupportedType: "Non identifié",

    usedUrlTitle: "URL déjà traitée",
    usedUrlsTitle: "{count} URLs déjà traitées",
    usedUrlLead: "Cette URL a déjà été traitée auparavant :",
    usedUrlsLead: "Ces URLs ont déjà été traitées auparavant :",
    usedUrlQuestion: "Voulez-vous la traiter à nouveau ?",
    usedUrlsQuestion: "Voulez-vous les traiter à nouveau ?",
    confirmProcessAgain: "Traiter à nouveau",
    processingCancelled: "Traitement annulé.",

    fuzzyTitle: "Surnom possible trouvé",
    fuzzyLead: "Le terme « {term} » peut être un surnom de joueur.",
    fuzzyQuestion: "Sélectionnez la bonne option :",
    fuzzyNone: "Aucun de ceux-là",
    fuzzyConfirm: "Confirmer",
    fuzzyTeam: "Équipe",
    fuzzyConfidence: "Confiance",
    fuzzyUseDetected: "Utiliser le pseudo détecté",

    rememberPlayerAliasTitle: "Mémoriser la correction du joueur ?",
    rememberPlayerAliasQuestion: "Voulez-vous mémoriser cette correction pour les prochains résultats ?",
    rememberPlayerAliasNo: "Pas maintenant",
    rememberPlayerAliasYes: "Mémoriser",

    rememberKnownPlayer: "🧠 Mémoriser",
    knownPlayerRemembered: "✓ Mémorisé",
    knownPlayerTitle: "Mémoriser le joueur ?",
    knownPlayersTitle: "Mémoriser les joueurs ?",
    knownPlayerQuestion: "Ce joueur sera reconnu comme une valeur validée à l'avenir.",
    knownPlayersQuestion: "Ces joueurs seront reconnus comme des valeurs validées à l'avenir.",
    knownPlayerCancel: "Annuler",

    appTools: "TOOLS",
    heroEyebrow: "CONTENU EXTERNE",
    heroTitle: "Interview Scraper",
    heroDescription: "Collez les liens des articles/vidéos et générez automatiquement le modèle ExternalContent/Line.",
    workflowProcess: "TRAITER",
    workflowProcessDesc: "Collez les liens et extrayez automatiquement leurs informations.",
    workflowReview: "VÉRIFIER",
    workflowReviewDesc: "Vérifiez les données détectées et apportez des modifications si nécessaire.",
    workflowGenerate: "GÉNÉRER",
    workflowGenerateDesc: "Exportez les modèles prêts à être copiés sur le wiki.",
    workflowFinish: "FINALISER",
    workflowFinishDesc: "Vérifiez le résultat final avant d'utiliser le modèle.",
    processingHeading: "TRAITEMENT",
    resultsHeading: "RÉSULTATS",
    resultsCountEmpty: "0 entretiens",
    resultsEmptyDescription: "Aucun entretien traité pour le moment.",
    resultsCountZero: "{count} entretien",
    resultsCountOne: "{count} entretien",
    resultsCountOther: "{count} entretiens",
    resultsEmptyHint: "Ajoutez les liens dans le panneau à côté et cliquez sur Générer les modèles.",
    themeToLight: "Activer le mode clair",
    themeToDark: "Activer le mode sombre",
    knownPlayerConfirm: "Mémoriser"
  }
};


/* =========================================================
   LANGUAGE
========================================================= */

function getLanguage() {
  return localStorage.getItem(
    "leaguepedia-scraper-language"
  ) || "pt-BR";
}

function t(key, replacements = {}) {
  const language = getLanguage();

  let text =
    translations[language]?.[key]
    ?? translations["pt-BR"][key]
    ?? key;

  for (const [keyName, value] of Object.entries(replacements)) {
    text = text.replace(
      `{${keyName}}`,
      value
    );
  }

  return text;
}

function applyLanguage() {
  const language = getLanguage();

  document.documentElement.lang = language;

  languageSelect.value = language;

  document.querySelectorAll(
    "[data-i18n]"
  ).forEach(element => {

    const key = element.dataset.i18n;

    if (key === "subtitle") {

      element.innerHTML = `${t(key).replace(
        "ExternalContent/Line",
        "<code>ExternalContent/Line</code>"
      )}`;

    } else {

      element.textContent = t(key);

    }

  });

  document.querySelectorAll(
    "[data-i18n-placeholder]"
  ).forEach(element => {

    element.placeholder = t(
      element.dataset.i18nPlaceholder
    );

  });

  updateUrlCount();
  updateResultsCount(renderedResultCount);
  updateThemeButton();
}

languageSelect.addEventListener(
  "change",
  () => {

    localStorage.setItem(
      "leaguepedia-scraper-language",
      languageSelect.value
    );

    applyLanguage();

  }
);



let renderedResultCount = 0;

function updateResultsCount(count) {
  renderedResultCount = count;

  const resultsCountEl = document.getElementById("results-count");
  const emptyEl = document.getElementById("results-empty");

  if (resultsCountEl) {
    const key = count === 1
      ? "resultsCountOne"
      : count === 0
        ? "resultsCountZero"
        : "resultsCountOther";

    resultsCountEl.textContent = t(key, { count });
  }

  if (emptyEl) {
    emptyEl.hidden = count > 0;
  }
}

/* =========================================================
   URL LIMIT
========================================================= */

function getUrls() {
  return urlsInput.value
    .split("\n")
    .map(url => url.trim())
    .filter(Boolean);
}

const USED_URLS_KEY = "leaguepedia-scraper-used-urls";

function getUsedUrls() {
  try {
    return JSON.parse(
      localStorage.getItem(USED_URLS_KEY) || "[]"
    );
  } catch {
    return [];
  }
}

function saveUsedUrls(urls) {
  localStorage.setItem(
    USED_URLS_KEY,
    JSON.stringify(urls)
  );
}

function normalizeUrl(url) {
  return url
    .trim()
    .replace(/\/+$/, "");
}

function getNewUrls(urls) {
  const usedUrls = getUsedUrls();

  return urls.filter(
    url => !usedUrls.includes(normalizeUrl(url))
  );
}

function getAlreadyUsedUrls(urls) {
  const usedUrls = getUsedUrls();

  return urls.filter(
    url => usedUrls.includes(normalizeUrl(url))
  );
}

const IGNORED_NICKNAMES_KEY =
  "leaguepedia-scraper-ignored-nicknames";

const CONFIRMED_ALIASES_KEY =
  "leaguepedia-scraper-confirmed-aliases";

const MANUAL_PLAYER_ALIASES_KEY =
  "leaguepedia-scraper-manual-player-aliases";

const KNOWN_PLAYER_VALUES_KEY =
  "leaguepedia-scraper-known-player-values";

function normalizeManualPlayerAlias(value) {
  return String(value || "").trim().toLowerCase();
}

function normalizeKnownPlayerValue(value) {
  return String(value || "").trim().toLowerCase();
}

function getKnownPlayerValues() {
  try {
    const values = JSON.parse(
      localStorage.getItem(KNOWN_PLAYER_VALUES_KEY) || "[]"
    );

    if (!Array.isArray(values)) {
      return [];
    }

    return [...new Set(
      values
        .map(normalizeKnownPlayerValue)
        .filter(Boolean)
    )];
  } catch {
    return [];
  }
}

function saveKnownPlayerValues(values) {
  const normalizedValues = Array.isArray(values)
    ? [...new Set(
        values
          .map(normalizeKnownPlayerValue)
          .filter(Boolean)
      )]
    : [];

  localStorage.setItem(
    KNOWN_PLAYER_VALUES_KEY,
    JSON.stringify(normalizedValues)
  );
}

function rememberKnownPlayerValue(value) {
  const normalized = normalizeKnownPlayerValue(value);

  if (!normalized) {
    return;
  }

  saveKnownPlayerValues([
    ...getKnownPlayerValues(),
    normalized
  ]);
}

function isKnownPlayerValue(value) {
  const normalized = normalizeKnownPlayerValue(value);

  return Boolean(normalized) &&
    getKnownPlayerValues().includes(normalized);
}

function getManualPlayerAliases() {
  try {
    const aliases = JSON.parse(
      localStorage.getItem(MANUAL_PLAYER_ALIASES_KEY) || "{}"
    );

    if (!aliases || typeof aliases !== "object" || Array.isArray(aliases)) {
      return {};
    }

    return Object.fromEntries(
      Object.entries(aliases)
        .map(([original, corrected]) => [
          normalizeManualPlayerAlias(original),
          String(corrected || "").trim()
        ])
        .filter(([original, corrected]) => original && corrected)
    );
  } catch {
    return {};
  }
}

function saveManualPlayerAliases(aliases) {
  localStorage.setItem(
    MANUAL_PLAYER_ALIASES_KEY,
    JSON.stringify(aliases || {})
  );
}

function getIgnoredNicknames() {
  try {
    const ignored = JSON.parse(
      localStorage.getItem(IGNORED_NICKNAMES_KEY) || "[]"
    );

    if (!Array.isArray(ignored)) {
      return [];
    }

    return [...new Set(
      ignored
        .map(nickname => String(nickname).trim().toLowerCase())
        .filter(Boolean)
    )];
  } catch {
    return [];
  }
}

function saveIgnoredNicknames(nicknames) {
  localStorage.setItem(
    IGNORED_NICKNAMES_KEY,
    JSON.stringify([
      ...new Set(
        nicknames
          .map(nickname => String(nickname).trim().toLowerCase())
          .filter(Boolean)
      )
    ])
  );
}

function getConfirmedAliases() {
  try {
    const aliases = JSON.parse(
      localStorage.getItem(CONFIRMED_ALIASES_KEY) || "{}"
    );

    if (
      !aliases ||
      typeof aliases !== "object" ||
      Array.isArray(aliases)
    ) {
      return {};
    }

    return aliases;
  } catch {
    return {};
  }
}

function saveConfirmedAliases(aliases) {
  localStorage.setItem(
    CONFIRMED_ALIASES_KEY,
    JSON.stringify(aliases || {})
  );
}

const CONFIRMED_RAW_NICKNAMES_KEY =
  "leaguepedia-scraper-confirmed-raw-nicknames";

function getConfirmedRawNicknames() {
  try {
    const nicknames = JSON.parse(
      localStorage.getItem(CONFIRMED_RAW_NICKNAMES_KEY) || "[]"
    );

    if (!Array.isArray(nicknames)) {
      return [];
    }

    return [...new Set(
      nicknames
        .map(nickname => String(nickname).trim().toLowerCase())
        .filter(Boolean)
    )];
  } catch {
    return [];
  }
}

function saveConfirmedRawNicknames(nicknames) {
  localStorage.setItem(
    CONFIRMED_RAW_NICKNAMES_KEY,
    JSON.stringify([
      ...new Set(
        nicknames
          .map(nickname => String(nickname).trim().toLowerCase())
          .filter(Boolean)
      )
    ])
  );
}

function removeIgnoredNickname(normalized) {
  saveIgnoredNicknames(
    getIgnoredNicknames().filter(nickname => nickname !== normalized)
  );
}

function removeConfirmedAlias(normalized) {
  const aliases = getConfirmedAliases();

  if (Object.prototype.hasOwnProperty.call(aliases, normalized)) {
    delete aliases[normalized];
    saveConfirmedAliases(aliases);
  }
}

function removeConfirmedRawNickname(normalized) {
  saveConfirmedRawNicknames(
    getConfirmedRawNicknames().filter(nickname => nickname !== normalized)
  );
}

function rememberRawNickname(normalized) {
  removeIgnoredNickname(normalized);
  removeConfirmedAlias(normalized);

  const nicknames = getConfirmedRawNicknames();
  nicknames.push(normalized);
  saveConfirmedRawNicknames(nicknames);
}

function rememberAlias(normalized, playerId) {
  removeIgnoredNickname(normalized);
  removeConfirmedRawNickname(normalized);

  const aliases = getConfirmedAliases();
  aliases[normalized] = playerId;
  saveConfirmedAliases(aliases);
}

function rememberIgnoredNickname(normalized) {
  removeConfirmedAlias(normalized);
  removeConfirmedRawNickname(normalized);

  const ignored = getIgnoredNicknames();
  ignored.push(normalized);
  saveIgnoredNicknames(ignored);
}

function updateUrlCount() {

  const urls = getUrls();

  const count = urls.length;

  urlCountEl.textContent = t(
    "urlCount",
    { count }
  );

  if (count > MAX_URLS) {

    urlCountEl.classList.add(
      "limit-exceeded"
    );

    limitWarningEl.textContent = t(
      "tooManyUrls"
    );

    scrapeButton.disabled = true;

  } else {

    urlCountEl.classList.remove(
      "limit-exceeded"
    );

    limitWarningEl.textContent =
      count === MAX_URLS
        ? t("limitWarning")
        : "";

    scrapeButton.disabled = isProcessing;

  }

}
urlsInput.addEventListener(
  "input",
  updateUrlCount
);

/* =========================================================
   TEMPLATE
========================================================= */

function escapeMediaWikiTitle(title) {
  return String(title || "").replace(/\|/g, "{{!}}");
}


function buildTemplate(item) {

  return (
    "{{ExternalContent/Line\n" +
    `|url=${item.url || ""}\n` +
    `|title=${escapeMediaWikiTitle(item.title)}\n` +
    `|players=${item.players || ""}\n` +
    `|teams=${item.teams || ""}\n` +
    `|tournament=${item.tournament || ""}\n` +
    `|series=${item.series || ""}\n` +
    `|publication=${item.publication || ""}\n` +
    `|author=${item.author || ""}\n` +
    `|translator=${item.translator || ""}\n` +
    `|type=${item.type || ""}\n` +
    `|isvideo=${item.isvideo || "No"}\n` +
    "}}"
  );

}


/* =========================================================
   DETECTED INFO
========================================================= */

function createDetectedInfo(item) {

  const info = document.createElement("div");

  info.className = "detected-info";

  const values = [
    [
      "publication",
      item.publication || t("unknownPublication")
    ],
    [
      "type",
      item.type || t("unknownType")
    ],
    [
      "tournament",
      item.tournament || t("unknownTournament")
    ],
    [
      "players",
      item.players || t("unknownPlayers")
    ],
    [
      "teams",
      item.teams || t("unknownTeams")
    ],
    [
      "date",
      item.date || t("unknownDate")
    ],
    [
      "translator",
      item.translator || t("noTranslator")
    ],
    [
      "video",
      item.isvideo === "Yes"
        ? t("yes")
        : t("no")
    ]
  ];

  if (item.series) {
    values.splice(3, 0, [
      "series",
      item.series
    ]);
  }

  for (const [labelKey, value] of values) {
    const span = document.createElement("span");
    const strong = document.createElement("strong");
    strong.textContent = `${t(labelKey)}: `;
    span.appendChild(strong);
    span.appendChild(
      document.createTextNode(value)
    );
    info.appendChild(span);
  }

  return info;
}

function addDetectedInfo(wrapper, item) {
  const info = createDetectedInfo(item);
  wrapper.appendChild(info);
}
/* =========================================================
   MANUAL EDITOR
========================================================= */

function createInputField(
  labelKey,
  value,
  fieldName,
  type = "text"
) {

  const group = document.createElement("div");

  group.className = "edit-field";

  const label = document.createElement("label");

  label.textContent = t(labelKey);

  let input;

  if (type === "textarea") {

    input = document.createElement("textarea");

    input.rows = 3;

  } else {

    input = document.createElement("input");

    input.type = type;

  }

  input.name = fieldName;

  input.value = value || "";

  group.appendChild(label);

  group.appendChild(input);

  return group;

}

function createPlayerInputField(value) {
  const group = createInputField(
    "players",
    value,
    "players"
  );
  const label = group.querySelector("label");
  const input = group.querySelector("input");
  const heading = document.createElement("div");
  const rememberButton = document.createElement("button");

  heading.className = "player-memory-heading";
  rememberButton.type = "button";
  rememberButton.className = "player-memory-button secondary";

  function updateRememberButton() {
    const players = splitFieldList(input.value);
    const unknownPlayers = players.filter(
      player => !isKnownPlayerValue(player)
    );
    const allKnown = players.length > 0 && unknownPlayers.length === 0;

    rememberButton.textContent = t(
      allKnown ? "knownPlayerRemembered" : "rememberKnownPlayer"
    );
    rememberButton.disabled = players.length === 0 || allKnown;
  }

  rememberButton.addEventListener("click", async () => {
    const unknownPlayers = splitFieldList(input.value)
      .filter(player => !isKnownPlayerValue(player));

    if (!unknownPlayers.length) {
      updateRememberButton();
      return;
    }

    rememberButton.disabled = true;

    try {
      if (await confirmKnownPlayerValues(unknownPlayers)) {
        unknownPlayers.forEach(rememberKnownPlayerValue);
      }
    } finally {
      updateRememberButton();
    }
  });

  input.addEventListener("input", updateRememberButton);
  label.parentNode.insertBefore(heading, label);
  heading.appendChild(label);
  heading.appendChild(rememberButton);
  updateRememberButton();

  return group;
}


function createSelectField(
  labelKey,
  value,
  fieldName,
  options
) {

  const group = document.createElement("div");

  group.className = "edit-field";

  const label = document.createElement("label");

  label.textContent = t(labelKey);

  const select = document.createElement("select");

  select.name = fieldName;

  for (const optionData of options) {

    const option = document.createElement("option");

    option.value = optionData.value;

    option.textContent = optionData.label;

    if (optionData.value === value) {
      option.selected = true;
    }

    select.appendChild(option);

  }

  group.appendChild(label);

  group.appendChild(select);

  return group;

}


function openManualEditor(
  item,
  wrapper,
  titleEl,
  infoEl,
  templateTextarea,
  editButton
) {

  if (
    wrapper.querySelector(".manual-editor")
  ) {
    return;
  }

  const originalPlayers = joinFieldList(splitFieldList(item.players));
  const editor = document.createElement("div");

  editor.className = "manual-editor";


  /* Header */

  const editorTitle = document.createElement("h3");

  editorTitle.textContent = t("editing");

  editor.appendChild(editorTitle);


  const hint = document.createElement("p");

  hint.className = "edit-hint";

  hint.textContent = t("editHint");

  editor.appendChild(hint);


  /* Fields */

  const fields = document.createElement("div");

  fields.className = "edit-fields";


  fields.appendChild(
    createInputField(
      "url",
      item.url,
      "url"
    )
  );

  fields.appendChild(
    createInputField(
      "title",
      item.title,
      "title"
    )
  );

  fields.appendChild(
    createPlayerInputField(item.players)
  );

  fields.appendChild(
    createInputField(
      "teams",
      item.teams,
      "teams"
    )
  );

  fields.appendChild(
    createInputField(
      "tournament",
      item.tournament,
      "tournament"
    )
  );

  fields.appendChild(
    createInputField(
      "series",
      item.series,
      "series"
    )
  );

  fields.appendChild(
    createInputField(
      "publication",
      item.publication,
      "publication"
    )
  );

  fields.appendChild(
    createInputField(
      "author",
      item.author,
      "author"
    )
  );

  fields.appendChild(
    createInputField(
      "translator",
      item.translator,
      "translator"
    )
  );

  fields.appendChild(
    createSelectField(
      "type",
      item.type || "",
      "type",
      [
        {
          value: "",
          label: t("unsupportedType")
        },
        {
          value: "Interview",
          label: "Interview"
        },
        {
          value: "Article",
          label: "Article"
        }
      ]
    )
  );

  fields.appendChild(
    createSelectField(
      "video",
      item.isvideo || "No",
      "isvideo",
      [
        {
          value: "Yes",
          label: t("yes")
        },
        {
          value: "No",
          label: t("no")
        }
      ]
    )
  );


  editor.appendChild(fields);


  /* Actions */

  const actions = document.createElement("div");

  actions.className = "edit-actions";


  const saveButton = document.createElement("button");

  saveButton.className = "save-edit";

  saveButton.textContent = t("save");


  const cancelButton = document.createElement("button");

  cancelButton.className = "cancel-edit";

  cancelButton.textContent = t("cancel");


  saveButton.addEventListener(
    "click",
    async () => {
      const formValues = new FormData();

      fields
        .querySelectorAll(
          "input, textarea, select"
        )
        .forEach(input => {

          formValues.append(
            input.name,
            input.value.trim()
          );

        });

      const playerCorrections = detectManualPlayerCorrections(
        originalPlayers,
        formValues.get("players") || ""
      );

      item.url =
        formValues.get("url") || "";

      item.title =
        formValues.get("title") || "";

      item.players =
        formValues.get("players") || "";

      item.teams =
        formValues.get("teams") || "";

      item.tournament =
        formValues.get("tournament") || "";

      item.series =
        formValues.get("series") || "";

      item.publication =
        formValues.get("publication") || "";

      item.author =
        formValues.get("author") || "";

      item.translator =
        formValues.get("translator") || "";

      item.type =
        formValues.get("type") || "";

      item.isvideo =
        formValues.get("isvideo") || "No";


      /* Regenera template */

      item.template = buildTemplate(item);

      templateTextarea.value = item.template;


      /* Atualiza título */

      titleEl.textContent =
        item.title || item.url;


      /* Atualiza informações detectadas */

      const newInfo = createDetectedInfo(item);

      infoEl.replaceWith(newInfo);


      for (const correction of playerCorrections) {
        const shouldRemember = await confirmManualPlayerAlias(correction);

        if (shouldRemember) {
          const aliases = getManualPlayerAliases();
          aliases[normalizeManualPlayerAlias(correction.original)] =
            correction.corrected.trim();
          saveManualPlayerAliases(aliases);
          rememberKnownPlayerValue(correction.corrected);
        }
      }

      /* Fecha editor */

      editor.remove();

      editButton.disabled = false;

    }
  );


  cancelButton.addEventListener(
    "click",
    () => {

      editor.remove();

      editButton.disabled = false;

    }
  );


  actions.appendChild(saveButton);

  actions.appendChild(cancelButton);

  editor.appendChild(actions);


  /* Adiciona depois do template */

  templateTextarea.insertAdjacentElement(
    "afterend",
    editor
  );

  editButton.disabled = true;

}


/* =========================================================
   CONFIRM MODAL
========================================================= */

function confirmUsedUrls(alreadyUsed) {
  const modal = document.getElementById("confirm-modal");
  const titleEl = document.getElementById("confirm-modal-title");
  const leadEl = document.getElementById("confirm-modal-lead");
  const listEl = document.getElementById("confirm-modal-list");
  const questionEl = document.getElementById("confirm-modal-question");
  const cancelButton = document.getElementById("confirm-modal-cancel");
  const okButton = document.getElementById("confirm-modal-ok");
  const backdrop = modal?.querySelector("[data-modal-dismiss]");

  if (!modal || !titleEl || !listEl || !cancelButton || !okButton) {
    return Promise.resolve(window.confirm(
      alreadyUsed.join("\n")
    ));
  }

  const isSingle = alreadyUsed.length === 1;

  titleEl.textContent = isSingle
    ? t("usedUrlTitle")
    : t("usedUrlsTitle", { count: alreadyUsed.length });

  if (leadEl) {
    leadEl.textContent = isSingle
      ? t("usedUrlLead")
      : t("usedUrlsLead");
  }

  if (questionEl) {
    questionEl.textContent = isSingle
      ? t("usedUrlQuestion")
      : t("usedUrlsQuestion");
  }

  listEl.innerHTML = "";

  for (const url of alreadyUsed) {
    const item = document.createElement("li");
    item.textContent = url;
    listEl.appendChild(item);
  }

  cancelButton.textContent = t("cancel");
  okButton.textContent = t("confirmProcessAgain");

  return new Promise(resolve => {
    const previousFocus = document.activeElement;

    function close(result) {
      modal.hidden = true;
      document.body.classList.remove("modal-open");

      cancelButton.removeEventListener("click", onCancel);
      okButton.removeEventListener("click", onConfirm);
      backdrop?.removeEventListener("click", onCancel);
      document.removeEventListener("keydown", onKeyDown);

      if (previousFocus && typeof previousFocus.focus === "function") {
        previousFocus.focus();
      }

      resolve(result);
    }

    function onCancel() {
      close(false);
    }

    function onConfirm() {
      close(true);
    }

    function onKeyDown(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancel();
      }

      if (event.key === "Enter") {
        event.preventDefault();
        onConfirm();
      }
    }

    cancelButton.addEventListener("click", onCancel);
    okButton.addEventListener("click", onConfirm);
    backdrop?.addEventListener("click", onCancel);
    document.addEventListener("keydown", onKeyDown);

    modal.hidden = false;
    document.body.classList.add("modal-open");
    okButton.focus();
  });
}


/* =========================================================
   FUZZY NICKNAMES
========================================================= */

const FUZZY_NONE_VALUE = "__none__";
const FUZZY_RAW_VALUE = "__raw__";

function splitFieldList(value) {
  if (Array.isArray(value)) {
    return value
      .map(item => String(item).trim())
      .filter(Boolean);
  }

  if (!value) {
    return [];
  }

  return String(value)
    .split(",")
    .map(item => item.trim())
    .filter(Boolean);
}

function joinFieldList(values) {
  return values.join(", ");
}

function detectManualPlayerCorrections(originalValue, correctedValue) {
  const originalPlayers = splitFieldList(originalValue);
  const correctedPlayers = splitFieldList(correctedValue);

  if (originalPlayers.length !== correctedPlayers.length) {
    return [];
  }

  const hasReorderedPlayer = originalPlayers.some((player, originalIndex) =>
    correctedPlayers.some((correctedPlayer, correctedIndex) =>
      originalIndex !== correctedIndex &&
      normalizeManualPlayerAlias(player) ===
        normalizeManualPlayerAlias(correctedPlayer)
    )
  );

  if (hasReorderedPlayer) {
    return [];
  }

  return originalPlayers
    .map((original, index) => ({
      original,
      corrected: correctedPlayers[index]
    }))
    .filter(({ original, corrected }) => original !== corrected);
}

function applyManualPlayerAliases(item) {
  if (!item) {
    return;
  }

  const aliases = getManualPlayerAliases();
  const previousPlayers = item.players || "";
  const players = splitFieldList(previousPlayers).map(player =>
    aliases[normalizeManualPlayerAlias(player)] || player
  );
  const nextPlayers = joinFieldList(players);

  if (nextPlayers !== previousPlayers) {
    item.players = nextPlayers;
    item.template = buildTemplate(item);
  }
}

function addUniqueFieldValue(currentValue, addition) {
  const nextValue = String(addition || "").trim();

  if (!nextValue) {
    return currentValue || "";
  }

  const values = splitFieldList(currentValue);
  const alreadyExists = values.some(
    value => value.toLowerCase() === nextValue.toLowerCase()
  );

  if (!alreadyExists) {
    values.push(nextValue);
  }

  return joinFieldList(values);
}

function confirmManualPlayerAlias(correction) {
  const modal = document.getElementById("manual-player-alias-modal");
  const titleEl = document.getElementById("manual-player-alias-title");
  const questionEl = document.getElementById("manual-player-alias-question");
  const originalEl = document.getElementById("manual-player-alias-original");
  const correctedEl = document.getElementById("manual-player-alias-corrected");
  const cancelButton = document.getElementById("manual-player-alias-cancel");
  const okButton = document.getElementById("manual-player-alias-ok");
  const backdrop = modal?.querySelector("[data-modal-dismiss]");

  if (
    !modal || !titleEl || !questionEl || !originalEl || !correctedEl ||
    !cancelButton || !okButton
  ) {
    return Promise.resolve(window.confirm(
      `${correction.original} → ${correction.corrected}\n${t("rememberPlayerAliasQuestion")}`
    ));
  }

  titleEl.textContent = t("rememberPlayerAliasTitle");
  questionEl.textContent = t("rememberPlayerAliasQuestion");
  originalEl.textContent = correction.original;
  correctedEl.textContent = correction.corrected;
  cancelButton.textContent = t("rememberPlayerAliasNo");
  okButton.textContent = t("rememberPlayerAliasYes");

  return new Promise(resolve => {
    const previousFocus = document.activeElement;

    function close(shouldRemember) {
      modal.hidden = true;
      document.body.classList.remove("modal-open");

      cancelButton.removeEventListener("click", onCancel);
      okButton.removeEventListener("click", onConfirm);
      backdrop?.removeEventListener("click", onCancel);
      document.removeEventListener("keydown", onKeyDown);

      if (previousFocus && typeof previousFocus.focus === "function") {
        previousFocus.focus();
      }

      resolve(shouldRemember);
    }

    function onCancel() {
      close(false);
    }

    function onConfirm() {
      close(true);
    }

    function onKeyDown(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancel();
      }

      if (event.key === "Enter") {
        event.preventDefault();
        onConfirm();
      }
    }

    cancelButton.addEventListener("click", onCancel);
    okButton.addEventListener("click", onConfirm);
    backdrop?.addEventListener("click", onCancel);
    document.addEventListener("keydown", onKeyDown);

    modal.hidden = false;
    document.body.classList.add("modal-open");
    okButton.focus();
  });
}

function confirmKnownPlayerValues(players) {
  const modal = document.getElementById("known-player-values-modal");
  const titleEl = document.getElementById("known-player-values-title");
  const listEl = document.getElementById("known-player-values-list");
  const questionEl = document.getElementById("known-player-values-question");
  const cancelButton = document.getElementById("known-player-values-cancel");
  const okButton = document.getElementById("known-player-values-ok");
  const backdrop = modal?.querySelector("[data-modal-dismiss]");

  if (!modal || !titleEl || !listEl || !questionEl || !cancelButton || !okButton) {
    const questionKey = players.length === 1
      ? "knownPlayerQuestion"
      : "knownPlayersQuestion";

    return Promise.resolve(window.confirm(
      `${players.join("\n")}\n\n${t(questionKey)}`
    ));
  }

  const isSingle = players.length === 1;
  titleEl.textContent = t(
    isSingle ? "knownPlayerTitle" : "knownPlayersTitle"
  );
  questionEl.textContent = t(
    isSingle ? "knownPlayerQuestion" : "knownPlayersQuestion"
  );
  cancelButton.textContent = t("knownPlayerCancel");
  okButton.textContent = t("knownPlayerConfirm");
  listEl.replaceChildren();

  players.forEach(player => {
    const item = document.createElement("li");
    item.textContent = player;
    listEl.appendChild(item);
  });

  return new Promise(resolve => {
    const previousFocus = document.activeElement;

    function close(shouldRemember) {
      modal.hidden = true;
      document.body.classList.remove("modal-open");

      cancelButton.removeEventListener("click", onCancel);
      okButton.removeEventListener("click", onConfirm);
      backdrop?.removeEventListener("click", onCancel);
      document.removeEventListener("keydown", onKeyDown);

      if (previousFocus && typeof previousFocus.focus === "function") {
        previousFocus.focus();
      }

      resolve(shouldRemember);
    }

    function onCancel() {
      close(false);
    }

    function onConfirm() {
      close(true);
    }

    function onKeyDown(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancel();
      }

      if (event.key === "Enter") {
        event.preventDefault();
        onConfirm();
      }
    }

    cancelButton.addEventListener("click", onCancel);
    okButton.addEventListener("click", onConfirm);
    backdrop?.addEventListener("click", onCancel);
    document.addEventListener("keydown", onKeyDown);

    modal.hidden = false;
    document.body.classList.add("modal-open");
    okButton.focus();
  });
}

function applyPlayerCandidate(item, candidate) {
  if (!item || !candidate) {
    return;
  }

  const previousPlayers = item.players || "";
  const previousTeams = item.teams || "";

  if (candidate.player) {
    item.players = addUniqueFieldValue(
      item.players,
      candidate.player
    );
  }

  if (candidate.team) {
    item.teams = addUniqueFieldValue(
      item.teams,
      candidate.team
    );
  }

  if (
    item.players !== previousPlayers ||
    item.teams !== previousTeams
  ) {
    item.template = buildTemplate(item);
  }
}

function applyRawNickname(item, displayName) {
  if (!item) {
    return;
  }

  const previousPlayers = item.players || "";

  item.players = addUniqueFieldValue(
    item.players,
    displayName
  );

  if (item.players !== previousPlayers) {
    item.template = buildTemplate(item);
  }
}

function formatConfidence(confidence) {
  const percent = (Number(confidence) || 0) * 100;

  return `${percent.toLocaleString(getLanguage(), {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  })}%`;
}

function confirmFuzzyCandidate(fuzzyItem) {
  const modal = document.getElementById("fuzzy-modal");
  const titleEl = document.getElementById("fuzzy-modal-title");
  const leadEl = document.getElementById("fuzzy-modal-lead");
  const questionEl = document.getElementById("fuzzy-modal-question");
  const optionsEl = document.getElementById("fuzzy-modal-options");
  const cancelButton = document.getElementById("fuzzy-modal-cancel");
  const okButton = document.getElementById("fuzzy-modal-ok");
  const backdrop = modal?.querySelector("[data-modal-dismiss]");

  if (!modal || !optionsEl || !cancelButton || !okButton) {
    return Promise.resolve({ action: "cancel" });
  }

  const term = fuzzyItem.text || fuzzyItem.normalized || "";
  const candidates = Array.isArray(fuzzyItem.candidates)
    ? fuzzyItem.candidates
    : [];

  if (titleEl) {
    titleEl.textContent = t("fuzzyTitle");
  }

  if (leadEl) {
    leadEl.textContent = t("fuzzyLead", { term });
  }

  if (questionEl) {
    questionEl.textContent = t("fuzzyQuestion");
  }

  optionsEl.innerHTML = "";

  if (term) {
    const rawLabel = document.createElement("label");
    rawLabel.className = "fuzzy-option fuzzy-option-raw";
    rawLabel.setAttribute("for", "fuzzy-option-raw");

    const rawRadio = document.createElement("input");
    rawRadio.type = "radio";
    rawRadio.name = "fuzzy-candidate";
    rawRadio.id = "fuzzy-option-raw";
    rawRadio.value = FUZZY_RAW_VALUE;
    rawRadio.checked = true;

    const rawContent = document.createElement("span");
    rawContent.className = "fuzzy-option-content";

    const rawName = document.createElement("strong");
    rawName.textContent = term;

    const rawDetails = document.createElement("span");
    rawDetails.className = "fuzzy-option-details";
    rawDetails.textContent = t("fuzzyUseDetected");

    rawContent.appendChild(rawName);
    rawContent.appendChild(rawDetails);
    rawLabel.appendChild(rawRadio);
    rawLabel.appendChild(rawContent);
    optionsEl.appendChild(rawLabel);
  }

  candidates.forEach((candidate, index) => {
    const optionId = `fuzzy-option-${index}`;
    const label = document.createElement("label");
    label.className = "fuzzy-option";
    label.setAttribute("for", optionId);

    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "fuzzy-candidate";
    radio.id = optionId;
    radio.value = candidate.player_id || "";
    radio.checked = !term && index === 0;

    const content = document.createElement("span");
    content.className = "fuzzy-option-content";

    const name = document.createElement("strong");
    name.textContent = candidate.player || candidate.player_id || "";

    const details = document.createElement("span");
    details.className = "fuzzy-option-details";
    details.textContent =
      `${t("fuzzyTeam")}: ${candidate.team || "—"} · ${t("fuzzyConfidence")}: ${formatConfidence(candidate.confidence)}`;

    content.appendChild(name);
    content.appendChild(details);
    label.appendChild(radio);
    label.appendChild(content);
    optionsEl.appendChild(label);
  });

  const noneLabel = document.createElement("label");
  noneLabel.className = "fuzzy-option fuzzy-option-none";
  noneLabel.setAttribute("for", "fuzzy-option-none");

  const noneRadio = document.createElement("input");
  noneRadio.type = "radio";
  noneRadio.name = "fuzzy-candidate";
  noneRadio.id = "fuzzy-option-none";
  noneRadio.value = FUZZY_NONE_VALUE;
  noneRadio.checked = !term && candidates.length === 0;

  const noneContent = document.createElement("span");
  noneContent.className = "fuzzy-option-content";

  const noneName = document.createElement("strong");
  noneName.textContent = t("fuzzyNone");

  noneContent.appendChild(noneName);
  noneLabel.appendChild(noneRadio);
  noneLabel.appendChild(noneContent);
  optionsEl.appendChild(noneLabel);

  cancelButton.textContent = t("cancel");
  okButton.textContent = t("fuzzyConfirm");

  return new Promise(resolve => {
    const previousFocus = document.activeElement;

    function close(result) {
      modal.hidden = true;
      document.body.classList.remove("modal-open");

      cancelButton.removeEventListener("click", onCancel);
      okButton.removeEventListener("click", onConfirm);
      backdrop?.removeEventListener("click", onCancel);
      document.removeEventListener("keydown", onKeyDown);

      if (previousFocus && typeof previousFocus.focus === "function") {
        previousFocus.focus();
      }

      resolve(result);
    }

    function onCancel() {
      close({ action: "cancel" });
    }

    function onConfirm() {
      const selected = optionsEl.querySelector(
        "input[name='fuzzy-candidate']:checked"
      );

      if (!selected || selected.value === FUZZY_NONE_VALUE) {
        close({ action: "ignore" });
        return;
      }

      if (selected.value === FUZZY_RAW_VALUE) {
        close({ action: "raw" });
        return;
      }

      const candidate = candidates.find(
        item => item.player_id === selected.value
      );

      if (!candidate) {
        close({ action: "ignore" });
        return;
      }

      close({
        action: "confirm",
        candidate
      });
    }

    function onKeyDown(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancel();
      }

      if (event.key === "Enter") {
        event.preventDefault();
        onConfirm();
      }
    }

    cancelButton.addEventListener("click", onCancel);
    okButton.addEventListener("click", onConfirm);
    backdrop?.addEventListener("click", onCancel);
    document.addEventListener("keydown", onKeyDown);

    modal.hidden = false;
    document.body.classList.add("modal-open");
    okButton.focus();
  });
}

async function resolveFuzzyCandidates(item) {
  const fuzzyCandidates = Array.isArray(item?.fuzzy_candidates)
    ? item.fuzzy_candidates
    : [];

  for (const fuzzyItem of fuzzyCandidates) {
    const normalized = String(
      fuzzyItem?.normalized || ""
    )
      .trim()
      .toLowerCase();

    if (!normalized) {
      continue;
    }

    if (getManualPlayerAliases()[normalizeManualPlayerAlias(normalized)]) {
      continue;
    }

    if (isKnownPlayerValue(fuzzyItem.text || fuzzyItem.normalized)) {
      applyRawNickname(
        item,
        fuzzyItem.text || fuzzyItem.normalized
      );
      continue;
    }

    const ignoredNicknames = getIgnoredNicknames();

    if (ignoredNicknames.includes(normalized)) {
      continue;
    }

    const aliases = getConfirmedAliases();
    const savedPlayerId = aliases[normalized];

    if (savedPlayerId) {
      const matchedCandidate = (fuzzyItem.candidates || []).find(
        candidate => candidate.player_id === savedPlayerId
      );

      if (matchedCandidate) {
        applyPlayerCandidate(item, matchedCandidate);
        continue;
      }

      delete aliases[normalized];
      saveConfirmedAliases(aliases);
    }

    const rawNicknames = getConfirmedRawNicknames();

    if (rawNicknames.includes(normalized)) {
      applyRawNickname(
        item,
        fuzzyItem.text || fuzzyItem.normalized
      );
      continue;
    }

    const decision = await confirmFuzzyCandidate(fuzzyItem);

    if (decision.action === "cancel") {
      continue;
    }

    if (decision.action === "ignore") {
      rememberIgnoredNickname(normalized);
      continue;
    }

    if (decision.action === "raw") {
      rememberRawNickname(normalized);
      applyRawNickname(
        item,
        fuzzyItem.text || fuzzyItem.normalized
      );
      continue;
    }

    if (decision.action === "confirm" && decision.candidate) {
      rememberAlias(
        normalized,
        decision.candidate.player_id
      );
      applyPlayerCandidate(item, decision.candidate);
    }
  }
}


/* =========================================================
   SCRAPE
========================================================= */

scrapeButton.addEventListener(
  "click",
  async () => {
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

    const alreadyUsed = getAlreadyUsedUrls(urls);

    /*
     * Se houver URLs já processadas, avisa o usuário,
     * mas permite processá-las novamente.
     */
    if (alreadyUsed.length > 0) {
      const shouldContinue = await confirmUsedUrls(alreadyUsed);

      if (!shouldContinue) {
        statusEl.textContent = t("processingCancelled");
        return;
      }
    }

    isProcessing = true;
    scrapeButton.disabled = true;
    scrapeButton.textContent =
      t("processingDisabled");

    statusEl.textContent =
      alreadyUsed.length
        ? `Processando ${urls.length} link(s), incluindo ${alreadyUsed.length} já utilizado(s)...`
        : t(
            "processing",
            {
              count: urls.length
            }
          );

    resultsEl.innerHTML = "";
    updateResultsCount(0);

    try {

      const response = await fetch(
        `${API_URL}/api/scrape`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            urls: urls
         })
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.error || "Unknown error."
        );

      }

      const failed = data.results.filter(
        item => item.error
      );

      const successful = data.results.filter(
        item => !item.error
      );
       
      const successfulUrls = successful
     .map(item => item.url)
     .filter(Boolean)
     .map(normalizeUrl);

      if (successfulUrls.length) {
     const usedUrls = getUsedUrls();

     saveUsedUrls([
       ...new Set([
         ...usedUrls,
         ...successfulUrls
          ])
     ]);
   }

      for (const items of Object.values(data.grouped || {})) {
        for (const item of items) {
          if (!item.error) {
            applyManualPlayerAliases(item);
            await resolveFuzzyCandidates(item);
          }
        }
      }

      statusEl.textContent =
        t(
          "processed",
          {
            success: successful.length
          }
        ) +
        (
          failed.length
            ? t(
                "withErrors",
                {
                  failed: failed.length
                }
              )
            : "."
        );


      /* Results grouped by date */

      for (
        const [date, items]
        of Object.entries(data.grouped)
      ) {

        const section =
          document.createElement("section");

        section.className = "result-card";


        const heading =
        document.createElement("h2");

         heading.className = "date-heading";

         const dateLink = document.createElement("a");

         dateLink.href = `https://lol.fandom.com/wiki/Data:ExternalContent/${date}`;

         dateLink.target = "_blank";

         dateLink.rel =
         "noopener noreferrer";

         dateLink.textContent = t(
           "dateHeading",
           {
             date
           }
         );
         heading.appendChild(dateLink);
         section.appendChild(heading);
        for (const item of items) {
          const wrapper =
            document.createElement("div");
          wrapper.className = "result";

          /* Title */

          const title =
            document.createElement("strong");

          title.className = "result-title";

          title.textContent =
            item.title || item.url;

          wrapper.appendChild(title);


          /* Detected information */

          const info =
            createDetectedInfo(item);

          wrapper.appendChild(info);


          /* Template */

          const textarea =
            document.createElement("textarea");

          textarea.className = "template-output";

          textarea.readOnly = true;

          textarea.value = item.template;

          wrapper.appendChild(textarea);


          /* Actions */

          const resultActions =
            document.createElement("div");

          resultActions.className =
            "result-actions";


          /* Copy button */

          const copy =
            document.createElement("button");

          copy.className = "copy";

          copy.textContent = t(
            "copyTemplate"
          );

          copy.addEventListener(
            "click",
            async () => {

              await navigator.clipboard.writeText(
                item.template
              );

              copy.textContent = t(
                "copied"
              );

              setTimeout(
                () => {

                  copy.textContent = t(
                    "copyTemplate"
                  );

                },
                1200
              );

            }
          );


          /* Edit button */

          const edit =
            document.createElement("button");

          edit.className = "edit";

          edit.textContent = t(
            "edit"
          );

          edit.addEventListener(
            "click",
            () => {

              const currentInfo =
                wrapper.querySelector(
                  ".detected-info"
                );

              openManualEditor(
                item,
                wrapper,
                title,
                currentInfo,
                textarea,
                edit
              );

            }
          );


          resultActions.appendChild(copy);

          resultActions.appendChild(edit);

          wrapper.appendChild(resultActions);

          section.appendChild(wrapper);

        }

        resultsEl.appendChild(section);

      }


      updateResultsCount(successful.length);

      /* Failed URLs */

      for (const item of failed) {

        const error =
          document.createElement("div");

        error.className = "error";

        error.textContent =
          `${item.url}: ${item.error}`;

        resultsEl.appendChild(error);

      }

    } catch (error) {

      statusEl.textContent = t(
        "error",
        {
          message: error.message
        }
      );

    } finally {

      isProcessing = false;

      scrapeButton.textContent = t(
        "generateButton"
      );

      updateUrlCount();

    }

  }
);


/* =========================================================
   CLEAR
========================================================= */

clearButton.addEventListener(
  "click",
  () => {

    urlsInput.value = "";

    resultsEl.innerHTML = "";

    updateResultsCount(0);

    statusEl.textContent = "";

    limitWarningEl.textContent = "";

    updateUrlCount();

  }
);


/* =========================================================
   INITIALIZATION
========================================================= */

loadTheme();
applyLanguage();
