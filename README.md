<!--
Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Bilingual guide to the QGSS26-team07 project, its quantum-computing work, data collection, and setup.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
-->

# QGSS26-team07

> **Languages:** [English](#english) | [Português](#português)

## English

### Project overview

`QGSS26-team07` is a participant project associated with the **Qiskit Global Summer School 2026 (QGSS26)**. It brings together local lab work, reproducibility utilities, reference material, and optional collection tools for publicly accessible course resources.

The repository name identifies this team's project. **QGSS26** remains the official event identifier and is intentionally retained in event-specific filenames, paths, grader module names, and references. Renaming the project folder does not change those upstream identifiers.

### Learning and development approach

The work was developed using a combination of:

- Human mental calculations and reasoning.
- Paper-and-pencil work for working through quantum circuits, states, and problem constraints.
- AI-assisted programming and review using GitHub Copilot and Claude versions available at the time of the event.

AI assistance was used as a development aid; calculations, code, and grader results were reviewed by the participant. Reported outcomes are snapshots recorded in the project documentation, not a promise of current access to IBM services or a live grader result.

### What is in this project

- **Lab solutions and helpers:** Local implementations for exercises across Labs 0–4, including circuit construction, backend information, error mitigation, QAOA, and SQD post-processing. The solutions folder is ignored by Git under the event FAQ's restriction on publishing solutions; local files may therefore not be present in a public clone.
- **Lab verification:** [`run_all_labs.py`](./run_all_labs.py) compares locally rerun exercises with official grader progress. Local solution modules are deliberately not published; the script therefore needs those modules supplied in the local ignored folder, plus the required packages and account access.
- **Resource collection:** Scripts gather publicly accessible ON24 and IBM Quantum Learning pages and assets. Login-dependent ON24 video downloads are attempted only with an existing authenticated browser session; no authentication bypass is intended.
- **Discord automation:** Optional collection through the official Discord bot API. It uses a bot token and explicit channel permissions, not browser cookies or a personal user token.
- **Catalog and reports:** Generated resource indexes plus project reports and a causal-analysis notebook.

### Repository layout

| Path | Purpose |
|---|---|
| `run_all_labs.py` | Run the local/official lab verification workflow. |
| `data/labs/solutions/` | Local lab implementations and IBM credential helper; intentionally Git-ignored. |
| `data/labs/extract_lab_map.py` | Extract the installed grader's lab/exercise map. |
| `data/labs/qgss-2026-official/` | Upstream course/lab material; treat as third-party content and retain its original terms. |
| `data/qgss26/scripts/` | ON24 public-asset collection and authenticated-session video attempts. |
| `data/ibm_learning/scripts/` | IBM Quantum Learning asset collection. |
| `data/run_all_collection.sh` | Run the available collection workflows in sequence. |
| `data/scripts/build_catalog.py` | Generate the catalog from collected data and manifests. |
| `discord_automation/` | Official-API Discord collector, configuration templates, and usage guide. |
| `environment-qgss26-conda.yml` | Conda environment definition. |
| `requirements-qgss26.txt` | Pinned pip requirements. |
| `requirements-conda-qgss26.txt` | Pinned requirements used by the Conda environment definition. |
| `links.md` | External project and event links. |

Collected downloads, HTML snapshots, generated catalog outputs, account-specific reports, environments, caches, local credentials, and lab solutions are not included in this public source snapshot. See [`.gitignore`](./.gitignore).

### Requirements

- Python 3.12 is specified in the Conda environment file.
- Conda is recommended for reproducing the pinned environment.
- Some lab checks require IBM/Qiskit packages, `qc_grader`, and network access.
- Submitting or checking official grades may require an active IBM Quantum account and valid credentials.
- Discord collection is optional and requires a Discord application/bot, an authorized bot token, the needed intents, and access to the target server/channels.
- Collection scripts require network access; some sources may restrict access or change their page/API behavior.

### Setup

Clone the repository from GitHub, then run the following commands from its root:

```bash
conda env create --prefix ./.conda -f environment-qgss26-conda.yml
```

If you moved or renamed an existing environment directory along with the
project, recreate the environment at the new location rather than editing
old absolute paths embedded in installed launchers.

Activate the environment:

```bash
conda activate "$(pwd)/.conda"
```

Alternatively, use the environment's Python executable directly:

```bash
.conda/bin/python --version
```

To install the pinned requirements into an already-created environment:

```bash
python -m pip install -r requirements-qgss26.txt
```

The requirements are pinned to versions recorded for this project and may need adjustment if upstream APIs or platforms have changed since the event.

### IBM Quantum credentials

Never put API keys or access tokens in source files, notebooks, screenshots, or commits. The project ignores the local `api-key/` directory and `.env` files.

For the local credential helper, create `api-key/apikey.json` privately with an `apikey` field, or configure the `QISKIT_IBM_TOKEN` environment variable. An IBM instance identifier can also be supplied as `instance`/`crn` in the private JSON or through `QISKIT_IBM_INSTANCE`. The helper also supports `GITHUB_TOKEN` or a local token file for its GitHub token operations.

Example environment setup (enter secrets interactively; do not paste them into shell history):

```bash
read -rsp "IBM Quantum token: " QISKIT_IBM_TOKEN
printf '\n'
export QISKIT_IBM_TOKEN
# Optional; set this only if your account requires an instance identifier.
export QISKIT_IBM_INSTANCE="<instance-crn>"
```

`data/labs/solutions/ibm_credentials.py` masks credential values when represented or printed and exposes a status check that reports credential presence without returning the token.

### Run lab verification

From the repository root:

```bash
.conda/bin/python run_all_labs.py
```

The workflow reads official progress through `qc_grader` and reruns supported exercises locally without requiring a QPU for every check. Exercises that are already marked successful by the official service but cannot be rerun locally are reported as server-verified. An official grader check is a remote request and can fail if authentication, network access, package compatibility, or the service is unavailable.

Extract or refresh the lab map when `qc_grader` is installed:

```bash
.conda/bin/python data/labs/extract_lab_map.py
```

### Collect public learning materials

Run all configured collection workflows:

```bash
bash data/run_all_collection.sh
```

Or run individual collectors:

```bash
bash data/qgss26/scripts/collect_public_assets.sh
bash data/ibm_learning/scripts/collect_ibm_learning_assets.sh
```

The ON24 video helper accepts a browser name and attempts downloads using an existing login session:

```bash
bash data/qgss26/scripts/download_videos_with_login.sh firefox
```

Access-controlled streams may not be downloadable. The helper does not bypass authentication. Collection status, known limitations, and the historical run summary are documented in [`data/COLLECTION_STATUS.md`](./data/COLLECTION_STATUS.md).

Regenerate the catalog after collection:

```bash
.conda/bin/python data/scripts/build_catalog.py
```

This writes machine-readable and Markdown catalog outputs under `data/catalog/`. Those generated outputs are excluded from the public source snapshot because their links depend on the collected files available in the local workspace.

### Discord collection (optional)

See [`discord_automation/README.md`](./discord_automation/README.md) for complete bot setup and operation. In brief:

1. Create a Discord application and bot in the Discord Developer Portal.
2. Enable Message Content Intent if message text is required; grant only the permissions needed for the target server.
3. Copy `discord_automation/config/discord_config.example.yaml` to `discord_automation/config/discord_config.yaml`.
4. Copy `discord_automation/.env.example` to `discord_automation/.env` and set `DISCORD_BOT_TOKEN` locally.
5. Run `bash discord_automation/run_discord_collection.sh`.

To enumerate the guilds available to the bot:

```bash
bash discord_automation/get_guild_id.sh
```

To set a target from a Discord channel URL:

```bash
bash discord_automation/set_target_from_url.sh "https://discord.com/channels/<guild_id>/<channel_id>"
```

Use the recurring daemon only when continuous collection is intended:

```bash
bash discord_automation/run_discord_daemon.sh 900
```

The interval is in seconds. Collection is limited to data visible to the bot; respect server rules, user privacy, and applicable policies. Output is written under the Git-ignored `discord_automation/output/`.

### Project name and paths

The working directory/repository is now named `QGSS26-team07`. Documentation commands use paths relative to the repository root instead of the previous machine-specific absolute path. Event-owned identifiers such as `QGSS26`, `qgss_2026`, and `qgss26` are retained where they refer to the event, official grader, or established filenames. The Conda environment name is `qgss26-team07`.

When sharing commands, start from the repository root. Do not copy old absolute paths from prior local notes; use repository-relative paths such as `data/run_all_collection.sh`.

### Documentation and recorded outcomes

- [`data/COLLECTION_STATUS.md`](./data/COLLECTION_STATUS.md) describes collected resources and limitations.

Account-specific grading analysis and execution records are kept out of this public repository to avoid disclosing private job identifiers and workspace details.

### Licensing and third-party material

Project-authored code and documentation carry an MIT notice in their headers; the full text is in [`LICENSE`](./LICENSE). Course materials, IBM/Qiskit resources, copied or downloaded assets, and other third-party content remain subject to their original licenses and terms; an MIT header in this project does not relicense third-party material. Check source terms before redistribution.

---

## Português

### Visão geral

`QGSS26-team07` é um projeto de participante associado à **Qiskit Global Summer School 2026 (QGSS26)**. Ele reúne atividades locais dos laboratórios, ferramentas de reprodutibilidade, materiais de referência e ferramentas opcionais de coleta de recursos públicos do curso.

O nome do repositório identifica o projeto desta equipe. **QGSS26** continua sendo o identificador oficial do evento e foi mantido intencionalmente em nomes de arquivos, caminhos, módulos do corretor e referências vinculadas ao evento. Renomear a pasta do projeto não altera os identificadores usados pela organização.

### Abordagem de estudo e desenvolvimento

O trabalho foi desenvolvido combinando:

- Cálculos mentais e raciocínio humano.
- Papel e lápis para trabalhar circuitos quânticos, estados e restrições dos exercícios.
- Programação e revisão assistidas por IA usando GitHub Copilot e versões do Claude disponíveis na época do evento.

A IA foi usada como apoio ao desenvolvimento; os cálculos, o código e os resultados do corretor foram revisados pelo participante. Os resultados documentados são registros históricos do projeto, não uma garantia de acesso atual aos serviços da IBM nem um resultado ao vivo do corretor.

### Conteúdo do projeto

- **Soluções e auxiliares dos labs:** Implementações locais para exercícios dos Labs 0–4, incluindo construção de circuitos, informações de backends, mitigação de erros, QAOA e pós-processamento SQD. A pasta de soluções é ignorada pelo Git, de acordo com a restrição do FAQ do evento sobre publicação das soluções; portanto, esses arquivos locais podem não estar disponíveis em um clone público.
- **Verificação dos labs:** [`run_all_labs.py`](./run_all_labs.py) compara reexecuções locais com o progresso oficial. Os módulos de soluções locais não são publicados intencionalmente; portanto, o script precisa desses módulos fornecidos na pasta local ignorada, além dos pacotes e do acesso à conta necessários.
- **Coleta de recursos:** Scripts coletam páginas e arquivos públicos do ON24 e do IBM Quantum Learning. Tentativas de baixar vídeos que exigem login usam apenas uma sessão autenticada já existente no navegador; não se pretende contornar a autenticação.
- **Automação do Discord:** Coleta opcional pela API oficial de bot do Discord. Usa token de bot e permissões explícitas nos canais, sem cookies do navegador ou token de usuário pessoal.
- **Catálogo e relatórios:** Índices gerados dos recursos, relatórios do projeto e um notebook de análise causal.

### Estrutura do repositório

| Caminho | Finalidade |
|---|---|
| `run_all_labs.py` | Executar o fluxo de verificação local/oficial dos labs. |
| `data/labs/solutions/` | Implementações locais e auxiliar de credenciais IBM; ignorada pelo Git intencionalmente. |
| `data/labs/extract_lab_map.py` | Extrair o mapa de labs/exercícios do corretor instalado. |
| `data/labs/qgss-2026-official/` | Material upstream do curso/labs; tratar como conteúdo de terceiros e manter os termos originais. |
| `data/qgss26/scripts/` | Coleta de recursos públicos ON24 e tentativas de vídeo com sessão autenticada. |
| `data/ibm_learning/scripts/` | Coleta de recursos do IBM Quantum Learning. |
| `data/run_all_collection.sh` | Executar sequencialmente os fluxos de coleta disponíveis. |
| `data/scripts/build_catalog.py` | Gerar o catálogo a partir dos dados coletados e manifestos. |
| `discord_automation/` | Coletor Discord pela API oficial, modelos de configuração e instruções. |
| `environment-qgss26-conda.yml` | Especificação do ambiente Conda. |
| `requirements-qgss26.txt` | Dependências pip fixadas por versão. |
| `requirements-conda-qgss26.txt` | Dependências fixadas usadas pela especificação Conda. |
| `links.md` | Links externos do projeto e do evento. |

Downloads coletados, snapshots HTML, saídas de execução, saídas de catálogo geradas, relatórios associados à conta, ambientes, caches, credenciais locais e soluções dos labs não estão incluídos neste snapshot público do código-fonte. Consulte [`.gitignore`](./.gitignore).

### Requisitos

- O arquivo Conda especifica Python 3.12.
- Conda é recomendado para reproduzir o ambiente com versões fixadas.
- Algumas verificações dos labs exigem pacotes IBM/Qiskit, `qc_grader` e acesso à rede.
- Enviar respostas ou consultar notas oficiais pode exigir uma conta IBM Quantum ativa e credenciais válidas.
- A coleta do Discord é opcional e exige um aplicativo/bot Discord, token autorizado, intents necessárias e acesso ao servidor/canais de destino.
- Os coletores precisam de acesso à rede; algumas fontes podem restringir acesso ou alterar páginas/APIs.

### Configuração

Clone o repositório do GitHub e execute os comandos a seguir a partir da raiz:

```bash
conda env create --prefix ./.conda -f environment-qgss26-conda.yml
```

Ative o ambiente:

```bash
conda activate "$(pwd)/.conda"
```

Como alternativa, execute diretamente o Python do ambiente:

```bash
.conda/bin/python --version
```

Para instalar as dependências fixadas em um ambiente já criado:

```bash
python -m pip install -r requirements-qgss26.txt
```

As dependências refletem as versões registradas para este projeto e podem precisar de ajustes caso APIs ou plataformas upstream tenham mudado desde o evento. Se você moveu ou renomeou um ambiente existente junto com o projeto, recrie-o no novo local em vez de editar caminhos absolutos embutidos nos executáveis instalados.

### Credenciais IBM Quantum

Nunca coloque chaves de API ou tokens em código-fonte, notebooks, capturas de tela ou commits. O projeto ignora a pasta local `api-key/` e arquivos `.env`.

Para o auxiliar local de credenciais, crie privadamente `api-key/apikey.json` com o campo `apikey` ou configure a variável de ambiente `QISKIT_IBM_TOKEN`. O identificador de instância IBM também pode ser informado como `instance`/`crn` no JSON privado ou pela variável `QISKIT_IBM_INSTANCE`. O auxiliar também aceita `GITHUB_TOKEN` ou um arquivo local para operações com token do GitHub.

Exemplo de configuração de ambiente (informe os segredos interativamente; não os cole no histórico do shell):

```bash
read -rsp "Token IBM Quantum: " QISKIT_IBM_TOKEN
printf '\n'
export QISKIT_IBM_TOKEN
# Opcional; configure somente se sua conta exigir um identificador de instância.
export QISKIT_IBM_INSTANCE="<instance-crn>"
```

`data/labs/solutions/ibm_credentials.py` mascara os valores de credenciais quando representados ou impressos e oferece uma consulta de status que informa se há credenciais sem retornar o token.

### Executar a verificação dos labs

Na raiz do repositório:

```bash
.conda/bin/python run_all_labs.py
```

O fluxo consulta o progresso oficial pelo `qc_grader` e reexecuta localmente os exercícios compatíveis, sem exigir QPU para todas as verificações. Exercícios já aprovados pelo serviço oficial, mas que não podem ser reexecutados localmente, são reportados como verificados pelo servidor. A consulta oficial é remota e pode falhar por autenticação, rede, compatibilidade de pacotes ou indisponibilidade do serviço.

Extraia ou atualize o mapa de exercícios quando `qc_grader` estiver instalado:

```bash
.conda/bin/python data/labs/extract_lab_map.py
```

### Coletar materiais públicos de aprendizagem

Execute os fluxos de coleta configurados:

```bash
bash data/run_all_collection.sh
```

Ou execute coletores individualmente:

```bash
bash data/qgss26/scripts/collect_public_assets.sh
bash data/ibm_learning/scripts/collect_ibm_learning_assets.sh
```

O auxiliar de vídeos ON24 recebe o nome do navegador e tenta baixar usando uma sessão de login existente:

```bash
bash data/qgss26/scripts/download_videos_with_login.sh firefox
```

Streams com acesso controlado podem não estar disponíveis para download. O auxiliar não contorna autenticação. O escopo, as limitações conhecidas e o resumo histórico estão em [`data/COLLECTION_STATUS.md`](./data/COLLECTION_STATUS.md).

Gere novamente o catálogo depois da coleta:

```bash
.conda/bin/python data/scripts/build_catalog.py
```

Isso cria saídas de catálogo legíveis por máquina e em Markdown em `data/catalog/`. Essas saídas geradas foram excluídas deste snapshot público porque seus links dependem dos arquivos coletados disponíveis no workspace local.

### Coleta do Discord (opcional)

Consulte [`discord_automation/README.md`](./discord_automation/README.md) para a configuração e operação completas do bot. Em resumo:

1. Crie um aplicativo e bot no Discord Developer Portal.
2. Ative Message Content Intent caso precise do texto das mensagens e conceda apenas as permissões necessárias no servidor de destino.
3. Copie `discord_automation/config/discord_config.example.yaml` para `discord_automation/config/discord_config.yaml`.
4. Copie `discord_automation/.env.example` para `discord_automation/.env` e configure `DISCORD_BOT_TOKEN` localmente.
5. Execute `bash discord_automation/run_discord_collection.sh`.

Para listar os servidores disponíveis ao bot:

```bash
bash discord_automation/get_guild_id.sh
```

Para definir o destino a partir de uma URL de canal:

```bash
bash discord_automation/set_target_from_url.sh "https://discord.com/channels/<guild_id>/<channel_id>"
```

Use o daemon recorrente somente quando a coleta contínua for desejada:

```bash
bash discord_automation/run_discord_daemon.sh 900
```

O intervalo é expresso em segundos. A coleta limita-se aos dados visíveis ao bot; respeite as regras do servidor, a privacidade dos usuários e as políticas aplicáveis. As saídas ficam em `discord_automation/output/`, ignorada pelo Git.

### Nome do projeto e caminhos

O diretório/repositório de trabalho agora se chama `QGSS26-team07`. Os comandos da documentação usam caminhos relativos à raiz do repositório em vez do caminho absoluto específico da máquina anterior. Identificadores pertencentes ao evento, como `QGSS26`, `qgss_2026` e `qgss26`, permanecem onde se referem ao evento, ao corretor oficial ou a nomes de arquivos já estabelecidos. O ambiente Conda se chama `qgss26-team07`.

Ao compartilhar comandos, comece pela raiz do repositório. Não reutilize caminhos absolutos de anotações locais antigas; prefira caminhos relativos como `data/run_all_collection.sh`.

### Documentação e resultados registrados

- [`data/COLLECTION_STATUS.md`](./data/COLLECTION_STATUS.md) descreve os recursos coletados e as limitações.

A análise de avaliação associada à conta e os registros de execução foram mantidos fora deste repositório público para evitar divulgar identificadores privados de jobs e detalhes do workspace.

### Licença e materiais de terceiros

Códigos e documentação produzidos para o projeto contêm indicação MIT em seus cabeçalhos; o texto completo está em [`LICENSE`](./LICENSE). Materiais do curso, recursos IBM/Qiskit, arquivos copiados ou baixados e outros conteúdos de terceiros continuam sujeitos às licenças e termos originais; um cabeçalho MIT neste projeto não relicencia conteúdo de terceiros. Verifique os termos das fontes antes de redistribuir.
