# Leaguepedia Interview Scraper

Ferramenta web para automatizar a criação de templates `{{ExternalContent/Line}}` para a Leaguepedia a partir de links de entrevistas e matérias relacionadas ao cenário de esports.

O projeto nasceu para automatizar uma tarefa repetitiva: identificar manualmente informações como jogador, equipe, data, publicação e torneio antes de adicionar uma entrevista à Leaguepedia.

## Como funciona

Basta colar uma ou mais URLs na ferramenta:

```text
https://maisesports.com.br/...
https://sheepesports.com/...
```

O scraper processa as páginas e tenta identificar automaticamente:

- Título
- Data de publicação
- Jogador(es)
- Equipe(s)
- Autor
- Publicação
- Tipo de conteúdo
- Torneio
- Tradutor
- Se o conteúdo é vídeo

Depois disso, a ferramenta gera o template:

```text
{{ExternalContent/Line
|url=...
|title=...
|players=...
|teams=...
|tournament=...
|publication=...
|author=...
|translator=...
|type=...
|isvideo=...
}}
```

## Detecções automáticas

### Publicação

Atualmente, o projeto possui suporte direcionado para:

- Mais Esports
- Sheep Esports

A publicação é identificada automaticamente a partir do domínio da URL.

### Conteúdo escrito e vídeo

Como o principal uso da ferramenta é processar matérias escritas:

- URLs de `maisesports.com.br` e `sheepesports.com` são consideradas conteúdo escrito.
- Plataformas conhecidas de vídeo são identificadas como vídeo.
- Outros domínios utilizam uma detecção baseada nos elementos e metadados da página.

Isso evita que embeds presentes em matérias escritas façam uma entrevista ser incorretamente classificada como vídeo.

### Torneio

A ferramenta tenta identificar automaticamente o torneio utilizando informações presentes na URL, no título, no conteúdo e na data de publicação.

O foco atual é o calendário competitivo do CBLOL, incluindo:

- CBLOL Cup
- CBLOL Split 1
- CBLOL Split 2

### Jogadores e equipes

A identificação utiliza uma base interna de jogadores e equipes do cenário analisado.

A URL e o título da matéria são utilizados para encontrar jogadores conhecidos e associá-los às respectivas equipes.

## Interface

A interface foi pensada para ser simples:

1. Cole uma ou mais URLs.
2. Clique em **Gerar Templates**.
3. Confira as informações detectadas.
4. Copie o template gerado.

Antes do template, a ferramenta mostra uma prévia das informações identificadas, permitindo conferir rapidamente possíveis erros de detecção.

## Tecnologias

### Backend

- Python
- Flask
- Requests
- BeautifulSoup
- Gunicorn

### Frontend

- HTML
- CSS
- JavaScript

## Arquitetura

```text
Usuário
   ↓
GitHub Pages
   ↓
Frontend HTML/CSS/JavaScript
   ↓
API Flask
   ↓
Render
   ↓
Requests + BeautifulSoup
   ↓
Site da publicação
   ↓
Informações extraídas
   ↓
Template da Leaguepedia
```

## Estrutura do projeto

```text
interviewscrapper-leaguepedia/
├── .github/
│   └── workflows/
│       └── deploy-pages.yml
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── render.yaml
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── README.md
└── render.yaml
```

## Rodando localmente

### Backend

Requer Python 3.10 ou superior.

```bash
cd backend
python -m venv .venv
```

Ative o ambiente virtual.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python app.py
```

A API ficará disponível em:

```text
http://localhost:5000
```

Para verificar se está funcionando:

```text
http://localhost:5000/api/health
```

## Deploy

O projeto utiliza duas partes independentes:

### Frontend

O frontend é publicado através do GitHub Pages.

O workflow em:

```text
.github/workflows/deploy-pages.yml
```

publica os arquivos da pasta:

```text
frontend/
```

### Backend

O backend Python pode ser hospedado no Render.

Após cada atualização no repositório conectado, o serviço pode fazer um novo deploy automaticamente.

A URL da API está configurada diretamente no frontend, então o usuário não precisa informar manualmente o endereço do backend.

## Limitações

O projeto utiliza regras e heurísticas para identificar algumas informações automaticamente.

Por isso, é recomendado conferir os dados detectados antes de adicionar o template à Leaguepedia, especialmente em casos como:

- jogadores não presentes na base interna;
- matérias com múltiplas pessoas;
- publicações fora dos sites atualmente suportados;
- conteúdo publicado fora do período regular de um torneio;
- posts de redes sociais;
- conteúdo cujo formato seja ambíguo.

## Objetivo

O objetivo do projeto não é substituir completamente a revisão humana, mas reduzir o trabalho repetitivo envolvido na adição de entrevistas e conteúdos externos à Leaguepedia.

Com isso, o fluxo passa de:

```text
Abrir matéria
↓
Ler e identificar informações
↓
Descobrir jogador
↓
Descobrir equipe
↓
Descobrir data
↓
Selecionar torneio
↓
Formatar template manualmente
```

para:

```text
Colar URL
↓
Gerar template
↓
Conferir informações
↓
Copiar para a Leaguepedia
```
