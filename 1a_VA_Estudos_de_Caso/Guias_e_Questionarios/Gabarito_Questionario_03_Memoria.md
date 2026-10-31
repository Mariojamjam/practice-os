# Gabarito Comentado: Questionário 03 - Gerenciamento de Memória
**Disciplina:** Sistemas Operacionais (BCC - UFRPE)  
**Professor:** Dr. Douglas Véras  
**Discentes:** Luiz Maranhão & Mário Jorge  
**Pontuação:** 10% da 1ª VA  

---

## 📊 Tabela Rápida de Respostas (Gabarito)

| Questão | Enunciado Resumido | Resposta |
| :---: | :--- | :---: |
| **01** | Segmentação complementa a lógica do programa; paginação voltada ao hardware | **VERDADEIRO** |
| **02** | MMU mapeia endereços virtuais em endereços físicos na memória virtual | **VERDADEIRO** |
| **03** | Swapping consiste em transferir temporariamente parte de um processo | **FALSO** |
| **04** | Gerenciamento de memória geralmente é realizado por hardware e não por software | **FALSO** |
| **05** | First-fit é mais rápido quando comparado a best-fit e worst-fit | **VERDADEIRO** |
| **06** | Programa + dados + pilha não pode ser maior que a memória física disponível | **FALSO** |
| **07** | Maior sobra deixada pelo Worst-Fit pode ser mais útil que a do Best-Fit | **VERDADEIRO** |
| **08** | A MMU tem como função mapear endereços virtuais para endereços físicos | **VERDADEIRO** |
| **09** | Fragmentação externa ocorre quando somando todos os espaços não há memória suficiente | **FALSO** |
| **10** | Memória virtual consiste em trazer na totalidade cada processo, executá-lo e devolvê-lo ao disco | **FALSO** |
| **11** | Espaço de endereçamento estende-se de 0 a um valor máximo (32 ou 64 bits) | **VERDADEIRO** |
| **12** | Técnica de swapping realiza transferências entre memória cache e memória principal | **FALSO** |
| **13** | Os segmentos de páginas possuem tamanhos iguais e fixos até o término da execução | **FALSO** |
| **14** | Espaço de endereçamento é o conjunto de endereços utilizado para executar instruções e dados | **VERDADEIRO** |
| **15** | Na paginação o espaço virtual é dividido em blocos de tamanho e posição fixas numerados | **VERDADEIRO** |
| **16** | No algoritmo LFU o sistema seleciona a página menos referenciada/utilizada | **VERDADEIRO** |
| **17** | O maior problema na paginação não é decidir quais páginas carregar, mas quais liberar | **VERDADEIRO** |
| **18** | Memória atribuída dinamicamente pode ser gerenciada por mapas de bits ou listas encadeadas | **VERDADEIRO** |
| **19** | First-fit busca na lista de livres um segmento para compactar o máximo de processos | **FALSO** |
| **20** | Best-fit aloca o menor espaço livre suficiente e produz a menor sobra de espaço | **VERDADEIRO** |
| **21** | Worst-fit aloca o maior espaço livre e produz a maior sobra de espaço livre | **VERDADEIRO** |
| **22** | O SO deve manter o maior número de processos residentes para maximizar o compartilhamento | **VERDADEIRO** |
| **23** | Na técnica de segmentação não há necessidade de mapeamento para memória física | **FALSO** |
| **24** | Monoprogramação sem troca/paginação: SO na RAM inferior, em ROM superior ou misto com drivers | **VERDADEIRO** |
| **25** | Com memória virtual o SO pode executar um programa de 32 MB com 8 MB de RAM | **VERDADEIRO** |
| **26** | A compactação é usada para resolver fragmentação externa, mas tem alto custo computacional | **VERDADEIRO** |
| **27** | O LRU elimina páginas utilizadas por tempo mais longo porque consomem mais memória | **FALSO** |
| **28** | MMU é um módulo do sistema operacional responsável por mapear endereços | **FALSO** |
| **29** | Não existe possibilidade de fragmentação interna na alocação por paginação | **FALSO** |
| **30** | A segmentação divide o espaço virtual em blocos de tamanhos diferentes chamados segmentos | **VERDADEIRO** |

---

## 📝 Justificativas Teóricas Detalhadas

### 1. A segmentação complementa a lógica real de um programa, enquanto a paginação é voltada para o hardware do sistema.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** A segmentação reflete a visão lógica do programador (segmentos de código, dados, pilha, sub-rotinas), com tamanhos variáveis associados à semântica do programa. A paginação, por sua vez, é orientada ao hardware e à MMU, dividindo o espaço em blocos de tamanho fixo (frames) para eliminar a fragmentação externa sem conhecimento da lógica interna do código. *(Referência: Silberschatz, Cap. 9; Tanenbaum, Cap. 3)*.

### 2. Nos sistemas de memória virtual, cabe à unidade de gerenciamento de memória (memory management unit) mapear endereços virtuais em endereços físicos.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** É a função primordial do hardware da MMU realizar a tradução/mapeamento dos endereços virtuais gerados pela CPU para os respectivos endereços físicos na memória principal (RAM) em tempo de execução.

### 3. A técnica de swapping consiste em transferir temporariamente parte de um processo da memória para o disco do computador e depois carregá-lo novamente em memória.
- **Resposta:** **FALSO**
- **Justificativa:** No *swapping* clássico/tradicional, o processo é transferido **em sua totalidade** (inteiro) entre a memória principal e a área de swap em disco. A transferência de "partes" (páginas individuais ou segmentos sob demanda) é a característica definidora da **paginação / memória virtual**, e não do swapping puro.

### 4. O gerenciamento de memória de um computador geralmente é realizado por hardware específico, e não por software.
- **Resposta:** **FALSO**
- **Justificativa:** O gerenciamento de memória é uma atribuição fundamental do **software do Sistema Operacional** (o subsistema de gerência de memória do kernel). O hardware (MMU, registradores de base/limite, tabelas de páginas) fornece apenas os mecanismos de suporte físico para que o software do SO implemente suas políticas.

### 5. A estratégia de alocação de partição first-fit quando comparada com as estratégias best-fit e worst-fit é mais rápida.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** O algoritmo *First-Fit* percorre a lista de blocos livres e aloca a memória imediatamente no primeiro espaço em que o processo caiba, encerrando a busca. O *Best-Fit* e o *Worst-Fit* precisam percorrer a lista inteira (a menos que esteja ordenada) para localizar, respectivamente, o menor e o maior bloco.

### 6. Para que um programa possa ser executado, o seu tamanho, incluindo os dados e a pilha, não pode ser maior que a quantidade de memória física disponível no computador para a sua execução.
- **Resposta:** **FALSO**
- **Justificativa:** A principal vantagem da **memória virtual** é desvincular o tamanho lógico do programa da quantidade física de memória RAM. Um programa pode ser muito maior do que a RAM instalada, pois apenas suas páginas ativas precisam residir na memória física no momento da execução.

### 7. A maior sobra de espaço livre produzido pelo algoritmo Worst-Fit poderá ser mais útil do que o pequeno espaço livre deixado pelo Best-Fit.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Esse é o fundamento conceitual da existência do *Worst-Fit*. O *Best-Fit* gera pequenas "sobras" (fragmentos minúsculos) espalhados pela memória que raramente podem ser aproveitados por outros processos. O *Worst-Fit*, ao alocar no maior bloco, deixa uma sobra grande com alta probabilidade de acomodar uma requisição futura.

### 8. A Memory Management Unit (MMU) tem como função mapear os endereços virtuais para endereços físicos de memória.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Definição canônica do dispositivo de hardware MMU.

### 9. O problema da fragmentação externa ocorre quando, por exemplo, na alocação Encadeada, não existem espaços contíguos (somando todos) de forma suficiente a alocar um processo.
- **Resposta:** **FALSO**
- **Justificativa:** A fragmentação externa ocorre justamente quando a soma de todos os espaços livres **É SUFICIENTE** para alocar o processo, mas eles estão fragmentados em blocos não contíguos. Dizer que "não existem espaços (somando todos) de forma suficiente" descreve simplesmente falta total de memória física, e não fragmentação.

### 10. O método para lidar com a sobrecarga de memória denominado de memória virtual consiste em trazer, em sua totalidade, cada processo para a memória, executá-lo durante um certo tempo e, então, devolvê-lo ao disco.
- **Resposta:** **FALSO**
- **Justificativa:** Essa é a definição textual exata do **Swapping** dada por Andrew Tanenbaum (*Sistemas Operacionais Modernos*). A memória virtual opera exatamente de forma oposta: não traz o processo em sua totalidade, mas apenas as páginas necessárias sob demanda.

### 11. No gerenciamento de memória por um sistema operacional, cada processo possui um conjunto de endereços que pode ser utilizado e cujos valores podem se estender de 0 a um valor máximo. Nos computadores, os endereços são normalmente de 32 bits ou de 64 bits.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Citação clássica do conceito de espaço de endereçamento linear privado de um processo (Tanenbaum, Cap. 3).

### 12. A técnica de swapping realiza transferências entre as memórias cache e memória principal.
- **Resposta:** **FALSO**
- **Justificativa:** O *swapping* realiza a transferência de processos entre a **memória principal (RAM)** e o **disco secundário (área de swap/SSD)**. A gerência entre cache e memória principal é realizada puramente por hardware (controlador de cache do processador).

### 13. Os segmentos de páginas de um programa em execução possuem tamanhos iguais e fixos até o término da execução.
- **Resposta:** **FALSO**
- **Justificativa:** Segmentos possuem tamanhos **variáveis** definidos pela lógica do programador (código, matriz, pilha). Apenas as páginas possuem tamanho fixo e igual, tornando a afirmativa falsa (Questão Q114682).

### 14. Espaço de endereçamento de um processo é um conjunto de endereços que um processo utiliza para acessar a memória do sistema, para executar instruções e armazenar dados.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Definição correta do espaço de endereçamento lógico privativo de um processo.

### 15. Na paginação, o espaço de endereçamento virtual é dividido em blocos, denominados unidades de alocação, de tamanho e posição fixas, geralmente de pequeno tamanho, aos quais se associa um número.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** O espaço de endereçamento virtual é particionado em unidades de tamanho fixo denominadas páginas virtuais (*Virtual Pages*), cada uma identificada por um índice ou número sequencial (VPN).

### 16. No algoritmo LFU (least-frequently-used), o sistema seleciona a página menos referenciada, ou seja, menos utilizada.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** O algoritmo LFU mantém um contador de frequência de uso para cada página residente e, na ocorrência de uma falta de página sem quadros livres, escolhe como vítima a página com a menor contagem de referências.

### 17. O maior problema na gerência de memória virtual por paginação não é decidir quais páginas carregar para a memória principal, mas quais liberar.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Proposição histórica consagrada por Peter Denning em 1968. Carregar uma página em paginação por demanda é uma resposta direta à falta de página (*page fault*); o desafio computacional crítico reside no algoritmo de substituição de páginas (quais páginas descartar/liberar para manter baixa taxa de falhas).

### 18. Quando a memória é atribuída dinamicamente, o sistema operacional pode gerenciá-la por meio de mapas de bits ou de listas encadeadas.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Conforme Tanenbaum (Cap. 3), as duas estruturas de dados primárias para rastrear a alocação dinâmica de memória no kernel são mapas de bits (*bitmaps*) e listas duplamente encadeadas de nós livres e ocupados.

### 19. No algoritmo first fit(o primeiro que couber), o gerenciador de memória procura ao longo da lista encadeada de segmentos de memória livres um segmento suficientemente grande para compactar o máximo de processos.
- **Resposta:** **FALSO**
- **Justificativa:** O *First-Fit* localiza o primeiro segmento livre suficiente para **alocar o processo solicitante**, particionando o bloco. Não tem nenhuma relação com "compactar o máximo de processos" (compactação é um procedimento distinto de desfragmentação física da RAM).

### 20. O algoritmo de alocação Best-fit aloca o menor espaço livre que seja suficientemente grande para carregar o programa. Produz a menor sobra de espaço livre.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Definição precisa do *Best-Fit*. Ele minimiza o tamanho da sobra resultante da alocação.

### 21. O algoritmo de alocação worst-fit aloca o maior espaço livre. Produz a maior sobra de espaço livre.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Definição precisa do *Worst-Fit*. Ele escolhe o maior buraco disponível, gerando a maior sobra possível.

### 22. O sistema operacional, através do gerenciador de memória, deve tentar manter na memória principal o maior número de processos residentes, permitindo maximizar o compartilhamento do processador e demais recursos computacionais.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Princípio de maximização do grau de multiprogramação para garantir que a CPU permaneça produtiva enquanto processos aguardam operações de E/S.

### 23. Na técnica de segmentação não há necessidade de mapeamento para memória física.
- **Resposta:** **FALSO**
- **Justificativa:** Em qualquer esquema de memória estruturada ou virtual (inclusive na segmentação), o par lógico `<segmento, deslocamento>` deve obrigatoriamente ser mapeado para endereços físicos na memória RAM utilizando a Tabela de Segmentos (contendo endereço base e limite).

### 24. No contexto da organização hierárquica de memórias e da monoprogramação sem troca ou paginação, o sistema operacional pode estar na parte inferior da memória RAM ou parte em ROM, ou ainda, os drivers de dispositivos podem estar na parte superior da memória ROM e o restante do sistema em RAM, na parte inferior.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Descrição literal dos três modelos clássicos de monoprogramação apresentados na Seção 3.1 e Figura 3-1 do livro *Sistemas Operacionais Modernos* de Andrew Tanenbaum.

### 25. Caso utilize a técnica de memória virtual, um sistema operacional pode carregar e executar um programa de 32 Mb em um computador com 8 Mb de memória principal.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** A memória virtual viabiliza a execução de processos cujo espaço de endereçamento excede a memória RAM física, utilizando paginação por demanda e swap em disco.

### 26. A técnica de compactação de memória é usada para resolver o problema da fragmentação externa, porém tem um custo computacional elevado.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** A compactação desloca fisicamente blocos de processos em execução para reunir áreas livres dispersas em um único bloco contíguo, o que gera alto consumo de ciclos de CPU e saturação do barramento de memória.

### 27. Quando ocorre uma falta de página, a estratégia de paginação LRU (least recently used) permite a eliminação de páginas utilizadas por um período de tempo mais longo, uma vez que elas consomem maior memória do sistema.
- **Resposta:** **FALSO**
- **Justificativa:** Duplamente errada: o LRU substitui a página **menos recentemente utilizada** (aquela cujo último acesso ocorreu há mais tempo no passado), e todas as páginas têm **exatamente o mesmo tamanho** na memória (não havendo páginas que "consomem maior memória").

### 28. MMU (Memory Managment Unity) é um módulo do sistema operacional responsável por mapear o espaçamento de endereçamento virtual no espaço de endereçamento físico.
- **Resposta:** **FALSO**
- **Justificativa:** Pegadinha clássica! A MMU é um componente de **HARDWARE** (integrado ao chip do processador) e **NÃO um módulo de software do sistema operacional**.

### 29. Não existe possibilidade de fragmentação interna na alocação por paginação.
- **Resposta:** **FALSO**
- **Justificativa:** A paginação elimina a fragmentação externa, mas gera **fragmentação interna** na última página alocada para o processo, caso o tamanho da solicitação não seja múltiplo exato do tamanho do frame.

### 30. A segmentação divide o espaço do endereçamento virtual em blocos de tamanhos diferentes chamados segmentos.
- **Resposta:** **VERDADEIRO**
- **Justificativa:** Definição fundamental da técnica de segmentação, na qual cada segmento possui tamanho variável compatível com os blocos lógicos do programa (funções, pilhas, vetores).
