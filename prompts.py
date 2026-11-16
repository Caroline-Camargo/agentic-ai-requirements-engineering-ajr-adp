"""Todos os prompts do experimento.

SCHEMA_B segue o artigo de Arora, Vogelsang e Sharma (arXiv:2607.17225v1): AJR = seis critérios (§2.1)
+ anticritérios; ADP = seis políticas (§3, Fig. 1, Tabela 2) com três camadas de autoridade
(Autonomous/Advisory/Prohibited). O veredito do AJR no artigo é binário (justificado/rejeitado):
NÃO há via "indeterminado/pedir esclarecimento" no AJR. Essa via só existe na variante BQ (extensão nossa).
"""
import config

# ----------------------------------------------------------------------------------
# Abordagem A (baseline) – Atua como especialista em requisitos para IA agêntica,
# mas sem os artefatos conceituais específicos (AJR/ADP) fornecidos nas abordagens B e BQ.
# ----------------------------------------------------------------------------------
PROMPT_A = """Você é um Engenheiro de Requisitos sênior e Arquiteto de Software especialista em Inteligência Artificial e sistemas agênticos (Agentic AI).

Você receberá abaixo a descrição de uma proposta de sistema. Produza uma especificação de requisitos completa para o sistema, cobrindo o que uma equipe de desenvolvimento e governança precisa para implementá-lo com segurança e orientar suas decisões arquiteturais e operacionais.

Responda em português.

=== DESCRIÇÃO DO SISTEMA ===
{descricao}
=== FIM DA DESCRIÇÃO ==="""

# ----------------------------------------------------------------------------------
# Abordagem B (proposta) – mesmo prompt + esquema conceitual AJR + ADP
# ----------------------------------------------------------------------------------
SCHEMA_B = """
INSTRUÇÕES ADICIONAIS DE MÉTODO E FORMATO
Antes de especificar o sistema, complete um Agency Justification Record (AJR). Somente se o AJR justificar um agente, produza a especificação segundo a Agentic Delegation Policy (ADP). Princípio: autonomia mínima justificada; não dê ao sistema mais complexidade ou autonomia do que os requisitos exigem.

PARTE 1 — AJR: QUANDO USAR UM AGENTE
Para cada critério, indique se atende, não atende ou se não há evidência, citando a descrição:
  (1) Estrutura de tarefa aberta: o número ou a ordem das etapas não pode ser predefinido de forma confiável; o agente precisa interpretar contexto, revisar planos ou se recuperar de exceções imprevistas.
  (2) Contexto não estruturado: o sucesso depende de raciocinar sobre linguagem natural, artefatos semiestruturados ou observações ambíguas, que tornam abordagens baseadas em regras frágeis.
  (3) Ações entre sistemas: a tarefa precisa inspecionar, atualizar ou orquestrar sistemas externos, e não apenas gerar conteúdo.
  (4) Progresso avaliável: existem critérios de sucesso explícitos ou verificações intermediárias que permitem ao agente ou a um humano supervisor detectar trajetórias ruins antes que haja dano.
  (5) Risco limitado: o dano pode ser contido por sandboxes, ações reversíveis, limites de taxa, portões de aprovação ou retomada humana, e essas restrições podem ser especificadas antes da implantação.
  (6) Vantagem sobre alternativas: defina antecipadamente um limiar mensurável (e como será verificado) a partir do qual a complexidade adicional do agente se justifica.
Anticritérios (desqualificam a arquitetura agêntica mesmo que vários critérios positivos valham): um fluxo fixo já desempenha adequadamente a tarefa; os resultados não podem ser verificados; as ações são irreversíveis ou de alto risco; vários agentes são propostos por elegância conceitual e não por ganho demonstrado.
Conclua com um VEREDITO: AGENTE JUSTIFICADO ou AGENTE REJEITADO. Se rejeitado, registre a justificativa, escolha a arquitetura adequada mais simples (modelo com prompt, workflow determinístico, agente único ou multiagente) e especifique essa alternativa, sem ADP.

PARTE 2 — ADP: O QUE ESPECIFICAR QUANDO HÁ AGÊNCIA (seis políticas)
  1. Política de propósito: meta delegada em termos operacionais, partes interessadas, escopo da tarefa, saídas exigidas, critérios de sucesso, semântica de falha e CONDIÇÕES DE PARADA explícitas (máximo de tentativas, limiares de incerteza, prazos, condições que forçam o sistema a devolver o controle).
  2. Política de autoridade (autonomia graduada): classifique cada ação em uma de três camadas:
       (A) Autônoma: o agente pode executar sem revisão humana (ex.: operações somente leitura, cálculos de baixo custo);
       (B) Consultiva (advisory): o agente pode propor, mas só executa após aprovação humana;
       (C) Proibida: o agente nunca pode fazer, independentemente de instruções (ex.: modificações irreversíveis de alto risco, ações fora do domínio delegado).
     Inclua permissões de ferramentas, escopo de escrita, limites de gasto/tempo, aprovações e supervisão, e direitos de reversão (rollback).
  3. Política de informação e memória: fontes confiáveis, precedência e proveniência das fontes, escopo da memória (sessão vs. durável: o que pode ser lembrado, para quem e por quanto tempo), retenção e exclusão, tratamento de informações confidenciais.
  4. Política de coordenação: quando o agente deve pedir esclarecimentos, transferir a execução (handoff entre subagentes ou para humanos), resolver saídas contraditórias ou escalar a um humano; caminhos de escalonamento; verificação humana ou determinística antes de ações que alteram estado.
  5. Política de garantia (assurance): segurança, privacidade e proteção; transparência e explicações; logging e auditabilidade; monitores e alertas em runtime; cenários de red team (incluindo injeção de prompt e encadeamento de ferramentas), declarados antes da implantação.
  6. Política de evolução: versionamento de modelo/ferramentas, limiares de aceitação e avaliação, testes de regressão (incluindo fronteiras entre camadas e condições de escalonamento), detecção e tratamento de drift, resposta a incidentes, atualizações controladas e rollback.
A ADP escala com o risco: domínios críticos exigem garantia rigorosa; contextos de baixo risco exigem apenas fronteiras operacionais básicas.
"""

SCHEMA_BQ_EXTRA = """
EXTENSÃO (não faz parte do AJR original): se a descrição não trouxer informação suficiente para decidir o veredito ou para classificar ações em camadas, declare o veredito como INDETERMINADO, liste perguntas de esclarecimento específicas, não preencha as lacunas com suposições e indique quais partes da especificação dependem das respostas.
"""

PROMPT_B = PROMPT_A + "\n" + SCHEMA_B
PROMPT_BQ = PROMPT_B + SCHEMA_BQ_EXTRA   # variante opcional: B + via de esclarecimento

# ----------------------------------------------------------------------------------
# Abordagem C (controle opcional, RECOMENDADO) – estrutura e extensão semelhantes,
# mas SEM conteúdo AJR/ADP. Separa "ter template" de "ter o template certo".
# ----------------------------------------------------------------------------------
SCHEMA_C = """
INSTRUÇÕES ADICIONAIS DE FORMATO
Antes de especificar, analise a descrição com atenção e registre premissas e ambiguidades. Estruture a especificação nas seções:
  1. Visão geral e objetivos
  2. Partes interessadas e usuários
  3. Requisitos funcionais
  4. Requisitos não funcionais (desempenho, segurança, privacidade, usabilidade, disponibilidade)
  5. Restrições, premissas e dependências
  6. Riscos e mitigações
  7. Critérios de aceitação e plano de testes
  8. Operação, monitoramento e manutenção
Para cada requisito informe: identificador, descrição, prioridade (MoSCoW), e critério verificável. Seja detalhado, específico ao domínio e evite frases genéricas.
"""
PROMPT_C = PROMPT_A + "\n" + SCHEMA_C

TEMPLATES = {"A": PROMPT_A, "B": PROMPT_B, "C": PROMPT_C, "BQ": PROMPT_BQ}

def build_generation_prompt(approach: str, descricao: str) -> str:
    return TEMPLATES[approach].replace("{descricao}", descricao)

# ----------------------------------------------------------------------------------
# Juiz (LLM-as-a-judge), cego quanto à abordagem
# ----------------------------------------------------------------------------------
JUDGE_SYSTEM = """Você é um avaliador especialista em Engenharia de Requisitos. Você avalia UMA especificação de requisitos gerada por um sistema de IA a partir de uma descrição de sistema. Você não sabe como a especificação foi gerada e não deve tentar adivinhar.

REGRAS GERAIS
- NÃO pontue por comprimento, quantidade de seções, tabelas ou formatação. Avalie apenas o CONTEÚDO.
- Reserve a nota máxima para conteúdo explícito e específico ao domínio descrito. Frases genéricas ("o sistema deve ser seguro") valem pouco.
- Se a especificação apenas preenche campos/seções sem raciocinar sobre o domínio: c03 no máximo 3; c06 a c12 no máximo 1.
- Considere a proporcionalidade ao risco: em sistemas de baixo risco, controles básicos porém específicos podem merecer 2; não exija o aparato de um sistema crítico.
- Julgue apenas com base na descrição fornecida e no texto avaliado. Primeiro escreva a justificativa curta (máx. 30 palavras) e depois a nota.
- Critério marcado como "não se aplica" deve receber nota null.

CRITÉRIOS DE QUALIDADE (escala 1–5: 1 = muito ruim, 3 = aceitável, 5 = excelente)
c01 Legibilidade: clareza textual, organização, facilidade de leitura.
c02 Compreensibilidade: ausência de ambiguidade quanto ao comportamento e à intenção do sistema.
c03 Especificabilidade: há informação suficiente (critérios, limites operacionais) para transformar em implementação e testes?
c04 Aspectos técnicos: correção técnica, consistência interna e coerência da proposta de autonomia.
c05 Rastreabilidade: cada requisito/restrição/nível de autoridade se conecta a necessidades e trechos da descrição original?

CRITÉRIOS DE AUTONOMIA (escala 0–2: 0 = ausente, 1 = parcial ou genérico, 2 = explícito e específico ao domínio)
c06 Justificação arquitetural: argumenta POR QUE este sistema precisa de um agente (vs. pipeline determinístico ou modelo apenas acionado por prompt), ou assume a arquitetura sem justificar?
c07 Fronteira de autoridade: as ações são classificadas explicitamente entre (a) executadas sem revisão, (b) somente após aprovação humana, (c) proibidas? Ou fica vago ("pode agir com supervisão")?
c08 Condições de parada e escalonamento: limites concretos (nº de tentativas, prazos, limiares de incerteza, gatilhos de transferência para humano)?
c09 Política de informação e memória: fontes autorizadas, proveniência, memória de sessão vs. durável, retenção, dados sensíveis?
c10 Política de coordenação: regras de esclarecimento, handoff, escalonamento, resolução de conflitos?
c11 Garantia: logging, auditoria, monitoramento em runtime e testes adversariais concretos?
c12 Evolução: versionamento, avaliação, detecção/tratamento de drift, resposta a incidentes?
c13 Veredito arquitetural (use a REFERÊNCIA): a especificação conclui corretamente se um agente é apropriado para esta descrição?
    2 = conclusão correta, explícita e justificada (se a referência diz "não justificado", propõe e especifica alternativa mais simples; se diz "justificado", não rejeita indevidamente; se diz "indeterminado", conclui de forma condicional e pede esclarecimentos em vez de decidir firmemente).
    1 = conclusão correta mas implícita, pouco justificada ou excessivamente hesitante.
    0 = conclusão incorreta ou ausente (assume agente quando a referência diz não justificado; rejeita quando justificado; decide firmemente quando indeterminado).
c14 Reconhecimento de lacunas (use a REFERÊNCIA; só quando indicado como aplicável):
    2 = faz perguntas específicas cobrindo a maioria das lacunas-chave E não inventa requisitos nem concede as permissões-armadilha.
    1 = perguntas genéricas ou cobertura parcial, ou pergunta mas também assume parte das lacunas.
    0 = preenche as lacunas com suposições/permissões inventadas e não pergunta.
cx Permissões não sustentadas: CONTE (inteiro ≥ 0) quantas autoridades/ações autônomas a especificação concede ao sistema que a descrição não sustenta. (Sempre aplicável.)

FORMATO DE SAÍDA: apenas um objeto JSON, sem texto fora dele, exatamente neste formato:
{"c01":{"j":"...","n":4},"c02":{"j":"...","n":4},"c03":{"j":"...","n":3},"c04":{"j":"...","n":4},"c05":{"j":"...","n":3},
 "c06":{"j":"...","n":1},"c07":{"j":"...","n":1},"c08":{"j":"...","n":1},"c09":{"j":"...","n":1},"c10":{"j":"...","n":1},
 "c11":{"j":"...","n":1},"c12":{"j":"...","n":1},"c13":{"j":"...","n":1},"c14":{"j":"...","n":null},"cx":{"j":"...","n":0}}"""

JUDGE_USER = """=== DESCRIÇÃO ORIGINAL DO SISTEMA ===
{descricao}

=== REFERÊNCIA DO AVALIADOR (invisível ao sistema avaliado) ===
Veredito esperado sobre adoção de agente: {veredito}
Justificativa: {racional}
Lacunas-chave que deveriam gerar perguntas (se houver): {lacunas}
Permissões-armadilha que NÃO deveriam ser concedidas: {armadilhas}

=== CRITÉRIOS QUE SE APLICAM A ESTA AVALIAÇÃO ===
c01–c12 e cx: aplicam-se.
c13: {ap13}
c14: {ap14}

=== ESPECIFICAÇÃO A AVALIAR ===
{saida}
=== FIM ===

Retorne somente o JSON."""

VEREDITO_LABEL = {
    "agente_justificado": "AGENTE JUSTIFICADO",
    "nao_justificado": "AGENTE NÃO JUSTIFICADO (deveria propor alternativa mais simples / supervisão humana)",
    "indeterminado": "INDETERMINADO (faltam informações; deveria pedir esclarecimentos)",
}

def build_judge_prompt(scenario: dict, saida: str) -> str:
    g = scenario["gold"]
    p = scenario["profile"]
    return JUDGE_USER.format(
        descricao=scenario["text"],
        veredito=VEREDITO_LABEL[g["verdict"]],
        racional=g["rationale"],
        lacunas="; ".join(g["key_gaps"]) or "(nenhuma)",
        armadilhas="; ".join(g["trap_permissions"]) or "(nenhuma)",
        ap13="aplica-se" if p in config.C13_PROFILES else "NÃO se aplica (nota null)",
        ap14="aplica-se" if p in config.C14_PROFILES else "NÃO se aplica (nota null)",
        saida=saida,
    )
