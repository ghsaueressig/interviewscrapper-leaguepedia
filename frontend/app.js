const apiInput = document.getElementById("api-url");
const urlsInput = document.getElementById("urls");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

const fields = {
  tournament: document.getElementById("tournament"),
  publication: document.getElementById("publication"),
  type: document.getElementById("type"),
  isvideo: document.getElementById("isvideo"),
  translator: document.getElementById("translator")
};

apiInput.value = localStorage.getItem("leaguepedia_api_url") || "";

document.getElementById("scrape").addEventListener("click", async () => {
  const api = apiInput.value.trim().replace(/\/+$/, "");
  const urls = urlsInput.value
    .split("\n")
    .map(x => x.trim())
    .filter(Boolean);

  if (!api) {
    statusEl.textContent = "Informe a URL da API.";
    return;
  }

  if (!urls.length) {
    statusEl.textContent = "Cole pelo menos uma URL.";
    return;
  }

  localStorage.setItem("leaguepedia_api_url", api);
  statusEl.textContent = `Processando ${urls.length} link(s)...`;
  resultsEl.innerHTML = "";

  try {
    const response = await fetch(`${api}/api/scrape`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        urls,
        config: {
          tournament: fields.tournament.value,
          publication: fields.publication.value,
          type: fields.type.value,
          isvideo: fields.isvideo.value,
          translator: fields.translator.value
        }
      })
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
