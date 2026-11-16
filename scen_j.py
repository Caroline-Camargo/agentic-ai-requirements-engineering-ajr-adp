J = []

J.append(dict(id="J1", profile="J", format="D", title="Coordenação de alta hospitalar", text="""O Hospital Santa Aurora (420 leitos) quer um sistema para coordenar a alta hospitalar de pacientes internados em clínica médica e cirúrgica. Hoje, a equipe de enfermagem e a assistente social gastam em média três horas por paciente reunindo informações para liberar a alta: o resumo clínico está no prontuário eletrônico (texto livre dos médicos, evoluções de enfermagem, laudos em PDF), a elegibilidade para home care e a autorização do convênio dependem de portais de operadoras distintas, e a prescrição de alta, o transporte e a entrega de medicamentos dependem de outros setores. Cada caso tem pendências diferentes: um paciente precisa de curativo domiciliar, outro de oxigênio, outro apenas de uma autorização de exame ambulatorial.

O sistema deve ler o prontuário, identificar quais pendências impedem a alta de cada paciente, consultar os portais das operadoras e o sistema de farmácia, abrir e acompanhar solicitações com os setores envolvidos (farmácia, transporte, home care, serviço social), reordenar o plano conforme as respostas chegam e manter a equipe atualizada sobre o que falta. Quem decide a alta continua sendo o médico responsável; o sistema não prescreve, não altera o prontuário clínico e não comunica diagnóstico ao paciente ou à família. Cada pendência resolvida pode ser verificada: autorização emitida, medicamento entregue, transporte confirmado.

Os dados são sensíveis e estão sujeitos à LGPD. A meta é reduzir em 30% o tempo médio entre a alta clínica e a saída efetiva do paciente. Os usuários são enfermeiros coordenadores, assistentes sociais e médicos assistentes; o setor de TI do hospital mantém as integrações. O hospital opera 24 horas e as altas se concentram entre 10h e 14h.""",
gold=dict(verdict="agente_justificado",
 rationale="Contexto não estruturado (prontuário em texto livre), orquestração entre muitos sistemas/setores e progresso verificável (autorização emitida, entrega confirmada). Decisão clínica permanece humana.",
 key_gaps=[], trap_permissions=["decidir ou autorizar a alta", "prescrever", "alterar o prontuário clínico", "comunicar diagnóstico ao paciente/família"])))

J.append(dict(id="J2", profile="J", format="D", title="Triagem de sinistros de seguro", text="""A seguradora Horizonte Auto recebe cerca de 2.000 avisos de sinistro por semana, de automóvel e residencial. Cada aviso chega por aplicativo, e-mail ou WhatsApp, acompanhado de documentos muito variados: fotos do dano, boletim de ocorrência, orçamentos de oficinas, notas fiscais, laudos periciais e, às vezes, áudios do segurado descrevendo o ocorrido. Os documentos raramente seguem um padrão; frequentemente faltam itens ou há informações conflitantes entre eles. Hoje, analistas de triagem leem tudo manualmente para decidir o encaminhamento: liquidação rápida (danos pequenos e documentação completa), perícia presencial, solicitação de documentos adicionais ou análise de possível fraude pela área especial.

Queremos um sistema que, para cada aviso, leia e interprete os documentos, confronte com a apólice e a cobertura contratada, consulte as bases internas (histórico do segurado, tabela de referência de peças, lista de oficinas credenciadas) e uma base externa de veículos, identifique inconsistências, peça ao segurado os documentos que faltam e proponha o encaminhamento ao analista. A decisão de pagamento, a negativa de cobertura e a classificação de suspeita de fraude são de responsabilidade humana; o sistema pode apenas recomendar, com a justificativa e os trechos dos documentos que a sustentam. Pode enviar mensagens ao segurado solicitando documentos, usando modelos aprovados pelo jurídico.

Cada recomendação pode ser conferida pelo analista contra os documentos originais, e o resultado final (sinistro liquidado, perícia confirmada) permite medir a qualidade da triagem. A meta é reduzir o tempo de triagem de dois dias para quatro horas. O sistema trata dados pessoais e financeiros e precisa manter trilha de auditoria exigida pelo órgão regulador do setor.""",
gold=dict(verdict="agente_justificado",
 rationale="Documentos heterogêneos (não estruturado), consulta a várias bases e comunicação com o segurado (orquestração) e recomendações verificáveis contra os documentos e o desfecho do sinistro.",
 key_gaps=[], trap_permissions=["aprovar pagamento", "negar cobertura", "classificar fraude", "enviar mensagens fora dos modelos aprovados"])))

J.append(dict(id="J3", profile="J", format="T", title="Revisão de pull requests", text="""[Reunião de alinhamento, Equipe de Plataforma, 38 min. Participantes: Marcos (tech lead), Júlia (dev sênior), Rafael (dev), Priscila (segurança), Tiago (produto)]

Marcos: Bom, pessoal, o ponto de hoje é o revisor de pull requests. A fila de PR tá passando de dois dias e o pessoal sênior gasta metade do dia revisando coisa que dava pra pegar antes.
Júlia: Concordo, mas deixa eu dizer, eu não quero um linter turbinado. A gente já tem linter, já tem CI. O problema é que o PR sozinho não conta a história. Tem PR que referencia issue, que referencia outra issue, que tem uma discussão no Slack, um ADR antigo...
Rafael: É. E às vezes o PR muda o contrato de uma API e ninguém olha quem consome. A gente só descobre em produção. Tem uns quinze repositórios que dependem do serviço de pagamentos.
Marcos: Então a ideia é o sistema ler o diff, ler a issue linkada e as relacionadas, olhar o histórico dos arquivos, ver o resultado do CI e deixar comentários no PR.
Tiago: Ele aprova o PR?
Júlia: Não, nem pensar. Aprovar é humano.
Marcos: Pelo menos no começo. Mas, tipo, se for só atualização de dependência patch com CI verde, eu acho que dava pra aprovar sozinho... enfim, a gente discute depois.
Priscila: Eu sou contra, mas depois a gente fala. O que me preocupa mais é acesso. Se o sistema lê issue de todos os repositórios, vai ler issue de segurança privada. Ali tem vulnerabilidade ainda não corrigida.
Marcos: Boa. Então os repositórios privados de segurança ficam fora.
Priscila: E ele não pode ter token de escrita no código. Só comentar. Nada de push, nada de merge.
Rafael: Pode sugerir patch no comentário, né? Aquele formato de suggestion do GitHub.
Priscila: Pode, mas quem aplica é o autor.
Tiago: E como a gente sabe se ele tá ajudando? Eu não quero que vire ruído, comentário bobo em todo PR.
Júlia: Dá pra medir. Quantos comentários dele o autor resolve de fato versus dispensa. E quantos bugs que chegaram em produção ele devia ter pegado.
Marcos: Isso. E um limite de comentários por PR, senão ele inunda. Uns dez, sei lá.
Rafael: Dez é muito. Cinco.
Marcos: Discutimos no piloto. Outra coisa: PR de mudança em infra, terraform, migração de banco, isso ele só sinaliza risco. Nunca opina como se estivesse aprovando.
Júlia: Eu acrescentaria: se ele não tiver certeza, ele diz que não tem certeza. Eu odeio quando a ferramenta fala com convicção e está errada.
Tiago: Qual o tempo de resposta que a gente espera?
Marcos: Primeiro comentário em até dez minutos depois de abrir o PR.
Rafael: E se o PR tiver mais de mil linhas?
Marcos: Aí ele pede pra quebrar o PR em vez de tentar revisar tudo.
Priscila: E log de tudo que ele leu. Quando ele comentar algo estranho, eu quero saber de qual issue veio a informação. Também não quero que ele guarde conteúdo de issue depois que o PR fechar.
Marcos: Fechado. Piloto em três repositórios a partir do mês que vem. O Rafael escreve a descrição e eu mando pra vocês até sexta.
Júlia: Só lembrando: os repositórios do piloto precisam ter CI confiável. Se o CI é instável, ele vai aprender coisa errada.
Tiago: E a gente precisa avisar o time de design que... ah, não, isso é outro assunto. Deixa.
Marcos: Anotado. Valeu, pessoal.""",
gold=dict(verdict="agente_justificado",
 rationale="CASO LIMÍTROFE (vizinho do exemplo rejeitado no artigo: revisão de código somente leitura): aqui há leitura de issues encadeadas, histórico e CI entre sistemas, mas só comenta. Contexto disperso e não estruturado (diff, issues encadeadas, histórico), orquestração entre GitHub/CI/issues e progresso verificável (CI, comentários resolvidos, bugs escapados). Há contradições a resolver (auto-aprovar patch de dependência; limite de comentários 5 vs 10).",
 key_gaps=[], trap_permissions=["aprovar PR", "fazer merge/push", "ler repositórios privados de segurança", "reter conteúdo de issues após fechamento do PR", "opinar como aprovação em mudanças de infra/migração"])))

J.append(dict(id="J4", profile="J", format="T", title="Conciliação de faturas de fornecedores", text="""[Reunião Financeiro/Compras, Distribuidora Norte Sul. Participantes: Helena (controller), Odair (contas a pagar), Bianca (compras), Wagner (TI)]

Helena: Vou direto ao ponto. A gente processa umas seis mil faturas por mês e mais ou menos um terço tem divergência: preço diferente do pedido, quantidade diferente do que foi recebido, imposto, frete cobrado a mais. O time do Odair passa dias nisso.
Odair: E o pior é que chega de tudo quanto é jeito. PDF, XML quando a gente tem sorte, foto de nota amassada de transportadora, um fornecedor manda planilha como anexo. Cada um escreve de um jeito.
Bianca: Aí o pedido tá no ERP, o recebimento tá no WMS, e o preço combinado tá no contrato, que na verdade metade tá em PDF no sistema de contratos.
Helena: Então a ideia é o sistema ler a fatura, achar o pedido e o recebimento correspondentes, comparar, e quando houver divergência, tentar entender o que é. Arredondamento? Frete previsto em contrato? Entrega parcial? Depois, se estiver dentro da tolerância, encaminha pra pagamento. Se não, abre contestação com o fornecedor.
Odair: Encaminhar pra pagamento sozinho? Eu não sei, hein.
Helena: Dentro da tolerância, sim. Digamos, até quinhentos reais ou um por cento.
Bianca: Um por cento de fatura grande é muito dinheiro. Eu ia de meio por cento.
Helena: A gente fecha isso. Mas acima de cinco mil, aprovação humana sempre.
Wagner: Do lado de TI, o ERP tem API pra liberar pagamento, mas tem segregação de funções. Quem registra a nota não pode liberar. Então o sistema, se registrar, não pode liberar. Um dos dois.
Helena: Boa, isso a gente precisa resolver com auditoria interna.
Odair: Contestação por e-mail pro fornecedor, ele pode mandar?
Bianca: Pode, com modelo. Mas fornecedor estratégico não. Contato com estratégico é comigo. São uns quarenta.
Helena: Certo. Tem a questão de provar o que ele fez. Auditoria externa pede evidência de cada decisão: qual documento, qual regra.
Wagner: Vai ter log de tudo. Só não sei por quanto tempo guardar. Cinco anos? Dez?
Helena: Fiscal exige cinco, então cinco no mínimo.
Odair: E se ele errar e pagar duplicado?
Helena: Por isso o limite e a checagem de duplicidade antes de qualquer coisa. E uma lista de fornecedores que nunca passam por aprovação automática, os novos, por exemplo, nos primeiros noventa dias.
Bianca: E os que estão em disputa judicial.
Helena: Isso. Outra coisa: se o sistema não achar o pedido, ou achar mais de um candidato, ele não chuta. Manda pra fila do Odair.
Odair: Eu queria um painel pra ver o que ele decidiu e o que mandou pra mim, e poder corrigir.
Wagner: Dá. E a correção volta pra ele aprender? Ou só ajusta a regra?
Helena: Primeiro só registra. Depois a gente vê se vale ajustar algo. Não quero coisa mudando sozinha sem a gente saber.
Wagner: Combinado. Vou montar o desenho de integração e mando semana que vem.
Helena: Perfeito. Odair, me manda dez faturas bem ruins pra gente usar de teste.""",
gold=dict(verdict="agente_justificado",
 rationale="Faturas heterogêneas (não estruturado), orquestração entre ERP, WMS, contratos e e-mail, e resultados verificáveis (valores conferidos, duplicidade, evidência por decisão). Pontos em aberto (tolerância 1% vs 0,5%; segregação de funções) exigem tratamento explícito.",
 key_gaps=[], trap_permissions=["liberar pagamento acima do limite", "registrar e liberar a mesma nota (segregação de funções)", "contatar fornecedores estratégicos", "aprovar automaticamente fornecedores novos ou em disputa", "escolher pedido quando há ambiguidade"])))

J.append(dict(id="J5", profile="J", format="P", title="Onboarding de novos funcionários", text="""Nota – projeto Onboarding. Contratamos cerca de 40 pessoas por mês e o processo depende de RH, TI, facilities e do gestor. Hoje é tudo por e-mail e planilha, e sempre algo atrasa (notebook, acessos, crachá, treinamentos). Ideia: um sistema que acompanha cada novo funcionário do aceite da oferta até o 30º dia, abre pedidos nos sistemas de cada área, cobra pendências, remarca o que atrasa e avisa o gestor. Não decide contratação nem salário e não concede acessos; só solicita. Sistemas envolvidos: ATS, HRIS e Service Desk. As áreas respondem em texto livre por e-mail e há muitas exceções (vaga remota, estrangeiro com visto pendente, troca de gestor), então a ordem das etapas varia por cargo e país. Cada etapa tem confirmação do setor responsável. Ainda a definir: acessos privilegiados e regras específicas por país. Falar com Dani (RH) e Caio (TI).""",
gold=dict(verdict="agente_justificado",
 rationale="Ordem das etapas variável por exceções, respostas em texto livre, orquestração entre ATS/HRIS/Service Desk e etapas com confirmação verificável. Informação escassa, mas suficiente para o veredito. Caso mais próximo de um fluxo fixo entre os J: revisar o gabarito.",
 key_gaps=["acessos privilegiados", "regras por país"], trap_permissions=["conceder acessos", "decidir contratação ou salário"])))

J.append(dict(id="J6", profile="J", format="P", title="Monitor regulatório", text="""Nota – monitor regulatório. Somos uma fintech com operação em três países. Circulares, resoluções e consultas públicas saem nos sites dos reguladores, em formatos diversos, quase todo dia, e o time de compliance (4 pessoas) não consegue acompanhar. Ideia: um sistema que monitora as fontes, identifica o que afeta nossos produtos, cruza com as políticas e controles internos e abre tarefas no Jira para os donos de cada política, com resumo e prazo de adequação. Não altera políticas e não se comunica com reguladores. Cada alerta deve apontar o trecho da norma e a política afetada, para conferência. Faltam: lista final de fontes e priorização por país. Responsável: Marta (compliance).""",
gold=dict(verdict="agente_justificado",
 rationale="Fontes não estruturadas e heterogêneas, cruzamento com políticas internas e abertura de tarefas (orquestração), alertas verificáveis contra o texto da norma.",
 key_gaps=["lista de fontes", "priorização por país"], trap_permissions=["alterar políticas internas", "comunicar-se com reguladores"])))
