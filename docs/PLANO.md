# Plano de execução: TalentMatch para o CIEE

O plano tem dois trilhos:

- **Trilho 1, construir agora.** Tudo o que não depende de ter dados. Seis sprints de cerca de 1 semana, com 1 desenvolvedor. Termina numa demo pronta para o pitch.
- **Trilho 2, alimentar com dados.** O que melhora com o uso. Cada passo tem um gatilho de volume. A coleta começa no Sprint 1, e o modelo melhora sozinho a partir daí.

O plano tem como base:

- [pesquisa-ciee.md](pesquisa-ciee.md), sobre como funciona o CIEE.
- O código atual: `match/utils.py`, `accounts/models.py`, `jobs/models.py`, `courses/models.py` e `templates/base.html`.

Prioridade: **P0** é obrigatório para a demo. **P1** é importante. **P2** fica para depois, se der tempo.

---

## O app de celular (PWA) e as dores do "Meu CIEE"

O app do CIEE tem **nota 1,6 no Google Play** (2,56 mil avaliações) e **1,8 na App Store**, onde não é atualizado desde out/2023. Cada reclamação abaixo tem uma resposta no nosso PWA.

| Reclamação real (lojas) | Resposta no PWA | Sprint |
|---|---|---|
| "Sempre aparece **não há vagas**" | Tela vazia útil: vagas próximas, vagas de áreas parecidas, botão "me avise quando surgir" (alerta salvo + push) e cursos para ampliar o leque | S3 |
| "**Ops, deu algo errado**" | Erros com mensagem clara e botão "tentar de novo", sem perder o que foi digitado. Erros enviados ao Sentry com contexto, e painel de falhas olhado toda semana | S1 |
| "**Não consigo anexar documentos**" | Upload que aceita PDF, JPG e PNG e **foto pela câmera** (`capture`). A imagem é comprimida no celular antes de subir, com barra de progresso, nova tentativa automática e limite de tamanho explicado antes do envio | S2 |
| "**Fecha quando vou me candidatar**" | Candidatura em 1 toque que não duplica se o botão for apertado duas vezes. **Sem internet, a candidatura fica na fila** e é enviada quando a conexão volta (Background Sync), e o app avisa | S4 |
| "**Não consigo concluir o cadastro**" / "**minha escola não aparece**" | Cadastro em etapas curtas, **salvo automaticamente** a cada campo. Busca de escola e curso nas listas oficiais (INEP e e-MEC). Opção "não encontrei" com campo livre, que vai para revisão. Endereço preenchido pelo CEP | S2 |
| "**Não consigo agendar horário**" | Agenda com horários livres, confirmação em 1 toque, arquivo .ics para o calendário e lembrete por push 24h e 1h antes | S4 |
| "**Esta vaga não possui etapas**" / falta de retorno | **Linha do tempo da candidatura** sempre visível, usando o `ApplicationStatusHistory` que já existe, com próximo passo e prazo. Push a cada mudança. Na recusa, um motivo e o que melhorar | S4 |
| App parado desde 2023 no iOS | O PWA **se atualiza sozinho** e roda igual em Android e iOS. No iOS 16.4 ou mais recente, recebe push quando instalado na tela inicial | S1 |
| Celular simples e pouco pacote de dados (71% dos aprendizes vêm de famílias com renda de até 2 salários mínimos) | Limite de peso: no máximo 200 KB de JS na primeira carga e menos de 3 s num 3G lento. Vagas salvas e cursos já abertos funcionam offline | S1–S4 |

**Metas do PWA**, que mostram ao CIEE o contraste com o app dele:

- Lighthouse 90 ou mais em Performance, Acessibilidade e Boas Práticas.
- Mais de 99,5% das sessões sem erro (Sentry).
- Mais de 70% dos cadastros iniciados são concluídos.
- Candidatura em menos de 30 s a partir da vaga.

---

# Trilho 1: construir agora

## Sprint 1: Fundação e base do PWA

**Backend**
- [ ] **P0 Postgres com pgvector**
  - Em dev e em produção. O Railway tem template com pgvector.
  - Aposentar o `db.sqlite3`, para o dev ser igual à produção.
- [ ] **P0 Fila de tarefas com Celery e Redis**
  - Serviço Redis no Railway e um worker no `Procfile`.
- [ ] **P0 Parar de calcular o match a cada acesso**
  - Hoje `get_recommended_jobs_for_candidate` e `get_recommended_candidates_for_job` percorrem tudo e gravam no banco a cada pedido.
  - Isso acontece em `dashboard/views.py`, `match/views.py`, `api/views.py` e `chatbot/ai_engine.py`.
  - Passam a ler o `MatchResult` já pronto.
  - Uma tarefa recalcula quando uma vaga é criada ou editada, ou quando um perfil é salvo, via signals.
- [ ] **P0 `model_version` em `MatchResult`**
  - Para comparar versões do algoritmo.
- [ ] **P0 Model `MatchEvent`**: é o nosso dataset.
  - Campos: `candidate`, `job`, `event`, `score`, `rank_position`, `model_version`, `reason`, `created_at`.
  - Eventos: `impression`, `click`, `save`, `apply`, `company_view`, `shortlist`, `reject`, `interview`, `hire`.
  - Na rejeição, o motivo vem de uma lista curta: curso, horário, distância, perfil incompleto, outro.
- [ ] **P0 Sentry** no backend e no frontend (o plano gratuito basta).

**PWA**
- [ ] **P0 Tirar o Tailwind do CDN**
  - O Play CDN não é para produção e impede o cache offline.
  - Gerar o CSS com o Tailwind standalone CLI no build, servido pelo WhiteNoise.
- [ ] **P0 Fixar a versão do Chart.js**
  - Hoje vem de `cdn.jsdelivr.net/npm/chart.js`, sem versão.
  - Servir uma cópia local e carregar **só nas páginas de dashboard**.
- [ ] **P0 `manifest.webmanifest`**
  - `name`, `short_name`, ícones 192/512 e maskable, `theme_color`, `display: standalone`, `start_url: /?source=pwa`.
  - Atalhos para Vagas, Minhas candidaturas e Chat.
- [ ] **P0 Service worker servido em `/sw.js`** por uma view Django, para valer no site inteiro. Estratégias de cache:
  - Arquivos estáticos (CSS, JS, ícones): cache primeiro, com versão no nome do arquivo.
  - Páginas HTML: rede primeiro. Sem conexão, mostra a página offline (`templates/offline.html`).
  - Lista e detalhe de vagas, cursos: mostra o que está em cache e atualiza em segundo plano.
- [ ] **P0 Atualização do app**: quando sai uma versão nova, aparece "Nova versão disponível, toque para atualizar".
- [ ] **P1 Instalação**
  - Android: botão próprio usando o `beforeinstallprompt`.
  - iOS: instrução visual de "Compartilhar → Adicionar à Tela de Início".
- [ ] **P1 Navegação de celular**
  - Barra inferior fixa: Vagas, Candidaturas, Cursos, Chat e Perfil.
  - Áreas de toque de pelo menos 44 px.
- [ ] **P1 Lighthouse CI** no `.github/workflows/ci.yml`, com metas mínimas de pontuação.

**Pronto quando:** o app instala no Android e no iOS, abre offline com uma página amigável, o dashboard não dispara nenhum cálculo e cada visualização de vaga gera um evento.

---

## Sprint 2: Cadastro, perfil estruturado e upload resiliente

**Dados**

- [ ] **P0 Novos campos em `CandidateProfile`**
  - `education_level`, `course` (FK), `institution` (FK, com campo livre de reserva)
  - `semester`, `expected_graduation`, `study_shift` (manhã, tarde, noite ou EAD)
  - `available_hours`
  - `birth_date`, no lugar de `age`
  - `cep`, `lat`, `lon`
  - `is_pcd`, `languages`
- [ ] **P0 Novos campos em `Job`**
  - `job_type` ganha `apprentice`.
  - `accepted_courses` (M2M).
  - `min_semester` e `max_semester`.
  - `shift` e `hours_per_day`, validando no máximo 6h/dia e 30h/semana.
  - `cep`, `lat`, `lon`.
  - `stipend` (bolsa).
  - `pcd_exclusive`.
  - `required_skills` e `desired_skills`, separando obrigatórias de desejáveis.
- [ ] **P0 Model `Skill`**
  - Nome canônico, sinônimos, categoria e embedding.
  - Carga inicial pelo **ESCO**, que tem rótulos em português e download gratuito.
- [ ] **P0 Models `CourseOfStudy` e `Institution`**
  - Carga pelas listas oficiais: **e-MEC** (superior), **Catálogo Nacional de Cursos Técnicos** e o **Catálogo de Escolas do INEP** (ensino médio).
  - Comando de management `load_reference_data`.
- [ ] **P0 Migração dos dados antigos**: o texto livre de `skills` e `requirements` passa para `Skill` (sinônimo exato → embedding mais próximo → fila de revisão).

**Cadastro (PWA)**

- [ ] **P0 Cadastro em 4 etapas curtas**: conta → escola e curso → disponibilidade e endereço → habilidades.
  - Rascunho salvo no servidor a cada etapa.
  - Barra de progresso visível.
- [ ] **P0 Busca de escola e curso** enquanto o usuário digita.
- [ ] **P0 Endereço pelo CEP** (ViaCEP ou BrasilAPI), com coordenadas pelo centroide do município do IBGE.
- [ ] **P0 Teclado e preenchimento certos em cada campo**: `inputmode` e `autocomplete` adequados, e a máscara de telefone que já existe.

**Upload**

- [ ] **P0 Componente de upload único**, usado para currículo e documentos:
  - Aceita PDF, JPG e PNG, inclusive foto pela câmera.
  - A imagem é comprimida no celular.
  - Barra de progresso, nova tentativa automática e mensagem clara de erro.
  - Valida o tipo de arquivo pelo conteúdo, ampliando o `validate_pdf_upload`.

**Extração por IA**

- [ ] **P0 Currículo → JSON validado** (Pydantic): habilidades, curso, experiências, projetos e idiomas.
  - Tela "Encontramos isto no seu currículo: confirma?".
  - Cada correção do candidato vira um rótulo grátis.
- [ ] **P1 Descrição da vaga → campos estruturados**, com confirmação da empresa.

**Pronto quando:** dá para completar o cadastro num Android simples em 3G lento, a escola é encontrada pela busca ou entra como texto livre, e o currículo enviado preenche as habilidades.

---

## Sprint 3: Matching v2 com explicação, lacunas e cursos

O matching passa a funcionar em quatro etapas. As três primeiras ficam prontas neste sprint, sem nenhum dado de treino:

```
A. Filtros legais e obrigatórios  →  B. Busca semântica top-200  →  C. Score por critérios  →  D. Reranqueamento (Sprint 5)
```

- [ ] **P0 Etapa A: filtros**, num módulo novo `match/filters.py`:
  - Aprendiz: idade de 14 a 24 anos, sem limite para PcD.
  - Estágio: matrícula ativa e curso entre os aceitos.
  - Turno da vaga sem conflito com o da escola.
  - Carga horária legal.
  - Vaga exclusiva para PcD.
- [ ] **P0 Etapa B: busca semântica**
  - Embeddings com `intfloat/multilingual-e5-small`, que roda em CPU, gerados pela fila.
  - Índice HNSW no pgvector.
  - Os 200 mais próximos em milissegundos.
- [ ] **P0 Etapa C: score explicável**, em `match/scoring.py`, substituindo o `calculate_match_score`. Critérios:
  - Cobertura das habilidades obrigatórias, por semelhança semântica e não por texto exato.
  - Cobertura das desejáveis.
  - Afinidade do curso com a vaga.
  - Semestre dentro da faixa.
  - Deslocamento em km.
  - Bolsa compatível.
  - Cursos relevantes já concluídos.
  - Perfil completo.
- [ ] **P0 Pesos iniciais escritos à mão e documentados**, até a calibração do Trilho 2. `experience_years` e `desired_salary` deixam de pesar 35%.
- [ ] **P0 Explicação gerada pelos próprios critérios**, sem LLM:
  - Para o jovem: "72%: curso compatível, turno OK, 4 km. Falta Excel → curso X."
  - Para a empresa: os pontos fortes primeiro.
- [ ] **P0 Lacunas por vaga-alvo**, substituindo o `get_skill_gaps`, que hoje olha as 100 primeiras vagas do país. Duas visões:
  - O que falta para *esta* vaga.
  - O que mais se pede na cidade e na área do jovem.
- [ ] **P0 Recomendação de cursos**
  - Ligação entre curso e habilidade pelo embedding do conteúdo das lições.
  - Ordem: importância da lacuna × demanda local ÷ carga horária, com preferência por cursos gratuitos.
- [ ] **P1 Catálogo externo**: links para Saber Virtual, Coursera/Google, IBM SkillsBuild e Fundação Bradesco. O sistema recomenda, não precisa hospedar.
- [ ] **P0 Tela vazia útil** em vez de "não há vagas".

**Pronto quando:** toda vaga e todo candidato recomendado mostram o percentual com o porquê e o curso que fecha a lacuna.

---

## Sprint 4: Candidatura, acompanhamento e notificações

- [ ] **P0 Candidatura em 1 toque**, sem duplicar a candidatura se o pedido chegar duas vezes.
- [ ] **P0 Fila offline**: candidaturas e mensagens ficam guardadas no celular (IndexedDB) e são enviadas pelo Background Sync quando a internet volta. Em navegador sem suporte, o envio é tentado de novo ao reabrir o app.
- [ ] **P0 Linha do tempo da candidatura**, usando o `ApplicationStatusHistory`: etapa atual, próximo passo, prazo e motivo em caso de recusa.
- [ ] **P0 Notificações push**
  - Chaves VAPID e a biblioteca `pywebpush`.
  - Model `PushSubscription`.
  - Envio disparado ao criar uma `Notification` (o model já existe).
  - Preferências por tipo de aviso.
- [ ] **P0 Alertas "me avise"**: busca salva, com push quando surgir uma vaga compatível.
- [ ] **P1 Agenda de entrevista**: a empresa abre horários, o candidato confirma, recebe o .ics e lembretes.
- [ ] **P0 Feedback que alimenta o Trilho 2**
  - 👍/👎 com motivo nos candidatos recomendados para a empresa.
  - "Essa vaga faz sentido?" para o jovem.
- [ ] **P0 Exploração de 10%**
  - 10% das posições da lista mostram bons candidatos com pouca exposição.
  - Ficam marcadas no `MatchEvent`.
  - Evita que o sistema só reforce os mesmos perfis e já gera informação nova.
- [ ] **P2 Chat**: trocar o polling por um polling com intervalo crescente, ou por SSE.

**Pronto quando:** uma candidatura feita no modo avião é enviada ao reconectar, e uma mudança de status chega por push no Android e no iOS instalado.

---

## Sprint 5: Avaliação, reranqueamento e viés

- [ ] **P0 Dados sintéticos** (`manage.py generate_synthetic`)
  - Cerca de 2.000 perfis fictícios e 200 vagas, gerados por LLM, com a distribuição real do público: 85% de escola pública, ensino médio e superior, várias cidades.
  - Servem para demo, teste e teste de carga. **Nunca usar dados reais de menores.**
- [ ] **P0 Conjunto ouro**
  - 50 vagas × 20 candidatos = 1.000 pares, rotulados de 0 a 3 por 2 pessoas.
  - Medir a concordância entre elas (kappa).
  - Leva de 10 a 15 horas.
- [ ] **P0 Conjunto prata**: cerca de 20 mil pares rotulados por um LLM com rubrica fixa, usados só depois de validar a concordância com o ouro.
- [ ] **P0 Métricas no CI**
  - NDCG@10, Recall@50 e Precision@5, comparando o v1 com o v2.
  - O build falha se o NDCG@10 cair mais de 2 pontos.
- [ ] **P0 Auditoria de viés contrafactual**
  - Trocar só nome, gênero, bairro ou tipo de escola: o score não pode mudar.
  - Atributos sensíveis nunca entram no score.
- [ ] **P1 Etapa D: reranqueamento** dos 20–30 primeiros
  - Com `BAAI/bge-reranker-v2-m3`, ou com um LLM e rubrica que devolve JSON com nota e justificativa.
  - Resultado guardado em cache por (vaga, candidato, `model_version`).
  - Só entra se melhorar o NDCG no conjunto ouro.
- [ ] **P1 Teste de carga** com os dados sintéticos multiplicados, por exemplo 200 mil perfis.

**Pronto quando:** existe um relatório de uma página com v1 × v2 nas métricas e o resultado da auditoria de viés.

---

## Sprint 6: Conformidade, entrevista simulada e demo

**Conformidade**
- [ ] **P0 Provedor de LLM e embeddings com dados no Brasil**
  - Embeddings e reranker rodando localmente.
  - LLM em provedor com região em São Paulo, conferindo quais modelos estão disponíveis lá.
  - Sem uso dos dados para treino.
  - Dados pessoais substituídos por códigos antes do envio ao LLM.
  - Sair da Groq, que processa nos EUA.
- [ ] **P0 LGPD**
  - Relatório de impacto (RIPD).
  - Base legal por finalidade.
  - Consentimento do responsável para menores, quando aplicável.
  - Prazo de retenção dos dados.
  - Política de privacidade em linguagem simples.
- [ ] **P0 Botão "contestar este resultado"**
  - Abre um pedido para revisão humana. Exigido pelo PL 2338 para IA usada em seleção.
  - Log auditável de cada recomendação: versão, critérios e score.
- [ ] **P0 ECA Digital**: privacidade por padrão para menores no feed e no chat, moderação e botão de denúncia.
- [ ] **P1 Model card** de uma página: o que o modelo usa, o que não usa, métricas e limites.
- [ ] **P1 Acessibilidade WCAG 2.1 AA** no fluxo do candidato: contraste, leitor de tela e navegação por teclado.

**Produto**
- [ ] **P1 Entrevista simulada v1 (texto)** no chatbot
  - Perguntas da vaga e avaliação por rubrica (método STAR, clareza, aderência).
  - Feedback com exemplo de resposta melhor.

**Demo**
- [ ] **P0 Ambiente de demo** com os dados sintéticos e roteiro de 10 minutos:
  1. Cadastro pelo celular.
  2. Match explicado.
  3. Lacuna → curso.
  4. Candidatura offline.
  5. Push de status.
  6. Painel da empresa.
  7. Relatório de viés.
- [ ] **P2 Publicar o PWA na Play Store como TWA** (Trusted Web Activity, com Bubblewrap). Assim a comparação com a nota 1,6 do "Meu CIEE" fica direta.

**Pronto quando:** a demo roda do começo ao fim no celular, e o pacote do pitch (pesquisa, relatório de métricas, model card e RIPD) está pronto.

---

# Trilho 2: alimentar com dados

A coleta começa no Sprint 1 (`MatchEvent`, feedback, exploração de 10%, correções do extrator). Cada passo abaixo só é dado quando o gatilho acontece.

| Gatilho | Ação |
|---|---|
| **Toda semana, desde o Sprint 2** | Revisar a fila de habilidades e escolas não reconhecidas e transformá-las em sinônimos ou cadastros novos |
| **Toda semana, desde o Sprint 1** | Revisar os principais erros no Sentry e as métricas do PWA (cadastros concluídos, tempo até a candidatura) |
| **3 a 5 recrutadores disponíveis** (pode ser já) | **Calibração dos pesos** com cerca de 150 comparações "entre A e B, quem você chamaria?" e uma regressão logística de preferências par a par. Substitui os pesos escritos à mão |
| **200 correções do extrator** | Medir a precisão e melhorar o prompt usando as correções como exemplos |
| **300 rejeições com motivo** | Analisar os motivos ("horário" muito frequente indica que o filtro de turno está fraco) e ajustar regras e pesos |
| **1.000 a 2.000 interações rotuladas** | **Primeiro modelo aprendido** (regressão logística ou LightGBM ranker com os critérios da Etapa C), misturado aos pesos manuais e testado A/B contra eles |
| **100 contratações registradas** | `hire` vira o rótulo principal: contratação > entrevista > shortlist > candidatura > clique |
| **30 jovens que concluíram o curso recomendado e se candidataram** | **Medir o impacto dos cursos** (score e taxa de entrevista e contratação com curso × sem curso). É o KPI principal do pitch |
| **Volume para retreinar** | Retreino semanal automático. A versão nova só sobe se passar no gate de métricas do Sprint 5 |
| **Piloto com o CIEE ou um regional** | Importar o histórico deles, com contrato e LGPD, e retreinar. A diferença de dados para a Gupy encolhe de vez |
| **Parceiro do piloto exige WhatsApp** | Integrar a WhatsApp Business Cloud API (exige verificação da empresa na Meta): alertas, status e entrevista simulada |
| **Entrevista simulada com uso real** | Versão por voz e pré-entrevista assíncrona para empresas, sempre com decisão humana |

---

## Riscos

| Risco | Mitigação |
|---|---|
| Seis sprints é apertado para uma pessoa | Garantir todos os P0 antes de qualquer P1; o P2 pode ficar para depois da demo |
| Push no iOS só funciona com o app instalado | Instrução de instalação no primeiro acesso; e-mail como alternativa |
| Railway sem memória para o modelo de embeddings | `e5-small`, ou um serviço separado só para embeddings |
| Custo e latência de LLM | LLM só na extração e no top 20–30, com cache; o resto é local |
| LLM-juiz enviesado | Sempre validado contra o conjunto ouro, com rubrica fixa |
| Poucos dados mesmo depois do lançamento | Piloto com cláusula de uso dos dados; exploração de 10% |
| Dados de menores | Dados sintéticos em dev e demo, RIPD, tratamento de dados no Brasil e coleta só do necessário |
