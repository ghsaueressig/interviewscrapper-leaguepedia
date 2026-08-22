const API_URL = "https://interviewscrapper-leaguepedia.onrender.com";

const urlsInput = document.getElementById("urls");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function addDetectedInfo(wrapper, item) {
  const info = document.createElement("div");
  info.className = "detected-info";

  const values = [
    ["Publicação", item.publication || "Desconhecida"],
    ["Tipo", item.type || "Desconhecido"],
    ["Torneio", item.tournament || "Não identificado"],
    ["Jogador(es)", item.players || "Não identificado"],
    ["Equipe(s)", item.teams || "Não identificada"],
    ["Data", item.date || "Não identificada"],
    ["Tradutor", item.translator || "Nenhum"],
    ["Vídeo", item.isvideo === "Yes" ? "Sim" : "Não"]
  ];

  for (const [label, value] of values) {
    const span = document.createElement("span");
    span.innerHTML = `<strong>${label}:</strong> `;
    span.appendChild(document.createTextNode(value));
    info.appendChild(span);
  }

  wrapper.appendChild(info);
}

document.getElementById("scrape").addEventListener("click", async () => {
  const urls = urlsInput.value
    .split("\n")
    .map(x => x.trim())
    .filter(Boolean);

  if (!urls.length) {
    statusEl.textContent = "Cole pelo menos uma URL.";
    return;
  }

  statusEl.textContent = `Processando ${urls.length} link(s)...`;
  resultsEl.innerHTML = "";

  try {
    const response = await fetch(`${API_URL}/api/scrape`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({urls})
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Erro desconhecido.");
    }

    const failed = data.results.filter(r => r.error);
    const successful = data.results.filter(r => !r.error);

    statusEl.textContent =
      `${successful.length} processado(s)` +
      (failed.length ? `; ${failed.length} com erro.` : ".");

    for (const [date, items] of Object.entries(data.grouped)) {
      const section = document.createElement("section");
      section.className = "result-card";

      const heading = document.createElement("h2");
      heading.textContent = `📅 DATA: ${date}`;
      section.appendChild(heading);

      for (const item of items) {
        const wrapper = document.createElement("div");
        wrapper.className = "result";

        const title = document.createElement("strong");
        title.textContent = item.title || item.url;
        wrapper.appendChild(title);

        addDetectedInfo(wrapper, item);

        const textarea = document.createElement("textarea");
        textarea.readOnly = true;
        textarea.value = item.template;
        wrapper.appendChild(textarea);

        const copy = document.createElement("button");
        copy.className = "copy";
        copy.textContent = "Copiar template";
        copy.addEventListener("click", async () => {
          await navigator.clipboard.writeText(item.template);
          copy.textContent = "Copiado!";
          setTimeout(() => copy.textContent = "Copiar template", 1200);
        });
        wrapper.appendChild(copy);

        section.appendChild(wrapper);
      }

      resultsEl.appendChild(section);
    }

    for (const item of failed) {
      const error = document.createElement("div");
      error.className = "error";
      error.textContent = `${item.url}: ${item.error}`;
      resultsEl.appendChild(error);
    }

  } catch (error) {
    statusEl.textContent = `Erro: ${error.message}`;
  }
});

document.getElementById("clear").addEventListener("click", () => {
  urlsInput.value = "";
  resultsEl.innerHTML = "";
  statusEl.textContent = "";
});
