# Leaguepedia Interview Scraper

Ferramenta para extrair informações de entrevistas do Mais Esports e gerar templates `{{ExternalContent/Line}}` para a Leaguepedia.

## Estrutura

```text
leaguepedia-interview-scraper/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── render.yaml
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
└── README.md
```

## 1. Rodar o backend localmente

Requer Python 3.10+.

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Depois:

```bash
pip install -r requirements.txt
python app.py
```

A API ficará em:

```text
http://localhost:5000
```

## 2. Testar o frontend

Abra `frontend/index.html` no navegador e informe:

```text
http://localhost:5000
```

no campo "URL da API".

## 3. Deploy do backend

O projeto já inclui `backend/render.yaml` para facilitar o deploy em um serviço que execute Python, como Render.

O frontend pode ser publicado no GitHub Pages.

Depois do deploy do backend, copie a URL dele para o campo "URL da API" do frontend.

## Observações

- O scraping continua sendo feito em Python com `requests` e `BeautifulSoup`.
- A interface do Colab (`ipywidgets`/`IPython.display`) foi substituída por HTML, CSS e JavaScript.
- O código inclui tratamento de timeout e erros HTTP.
- As URLs são deduplicadas antes do processamento.
- O frontend possui botão individual para copiar cada template.
- A lógica de `TEAM_MAP`, `PLAYER_DATA`, `STOPWORDS`, identificação de autores e geração do `ExternalContent/Line` foi preservada do arquivo original.
