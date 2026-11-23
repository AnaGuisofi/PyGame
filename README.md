# NEON BREAKOUT // Arcade Edition

## Autores
* **Ana Guisofi**
* **Bernardo Abner**
* **Enzo Giorgetti**

## Vídeo de Demonstração
* **Link do vídeo:** **(https://youtu.be/To-jp1EhXdc?si=VJ1Hj7HzbPsmEhBM)**

---

## Sobre o Projeto

Releitura moderna do clássico **Breakout (Atari)** desenvolvida em Python com a biblioteca **PyGame**, trazendo estética *Synthwave/Neon*, trilha e efeitos sonoros sintetizados proceduralmente, sistema de dificuldades, armadilhas, inimigos móveis e batalha contra chefão.

### Funcionalidades Principais

* **Identificação e Histórico de Sessão:** Tela para inserção do nome do jogador antes da partida, com exibição em tempo real no HUD e painel com o histórico das últimas pontuações na tela inicial.
* **Três Níveis de Dificuldade:** Modos **Normal**, **Difícil** e **Insano**, que ajustam a velocidade da bola, o tamanho inicial da raquete, a frequência de armadilhas, a velocidade dos drones e os pontos de vida do chefão.
* **4 Fases Progressivas:**
  * **Fase 1:** Formação clássica para aquecimento e combos.
  * **Fase 2:** Introdução de blocos explosivos, prismas indestrutíveis e fileiras móveis.
  * **Fase 3:** Fortaleza blindada protegida por drones de patrulha.
  * **Fase 4 (Chefão):** Confronto contra o **Core**, que patrulha a arena e dispara rajadas de plasma capazes de encolher e paralisar temporariamente a raquete.
* **Power-ups e Armadilhas:** Cápsulas arredondadas concedem melhorias (expansão da raquete, multibola, canhões laser, bola de fogo e vida extra), enquanto cápsulas quadradas aplicam penalidades temporárias (encolhimento, aceleração brusca da bola e inversão de controles).
* **Áudio Procedural:** Efeitos sonoros e música de fundo gerados dinamicamente via código, sem necessidade de arquivos externos de áudio.
* **Feedback Visual:** Sistema de partículas, ondas de choque expansivas, rastro luminoso na bola, textos flutuantes de pontuação/combo e tremor de tela (*screen shake*) em impactos críticos.

---

## Estrutura do Projeto

O código foi estruturado seguindo o paradigma de **Programação Orientada a Objetos (POO)** e dividido em módulos com responsabilidades bem definidas:

```text
PyGame/
├── main.py         # Ponto de entrada da aplicação
├── config.py       # Constantes globais, paleta de cores, regras e presets de dificuldade
├── jogo.py         # Controlador principal, máquina de estados, colisões e renderização
├── entidades.py    # Classes das entidades (Raquete, Bola, Tijolo, Cápsula, Drone, Chefão, etc.)
├── fases.py        # Construção e gerenciamento dos layouts das 4 fases
├── audio.py        # Sintetizador procedural de efeitos sonoros e música de fundo
└── README.md       # Documentação do projeto
```

---

## Pré-requisitos e Como Executar

1. Certifique-se de ter o **Python 3.10+** instalado.
2. Instale a biblioteca **PyGame**:
   ```bash
   pip install pygame
   ```
3. Acesse a pasta do projeto pelo terminal e execute o arquivo principal:
   ```bash
   python main.py
   ```
   *(No Windows, caso utilize o launcher padrão, execute `py main.py`)*

---

## Controles

| Tecla / Ação | Função |
| :--- | :--- |
| **Setas (`←` / `→`)**, **`A` / `D`** ou **Mouse** | Move a raquete horizontalmente |
| **`Espaço`** ou **Clique Esquerdo** | Lança a bola inicial / Dispara lasers (quando ativo) |
| **`1`**, **`2`**, **`3`** ou **Setas (`<` `>`)** | Seleciona a dificuldade no Menu Inicial |
| **`Enter`** | Confirma opções e inicia a partida |
| **`I`** | Abre a tela de instruções e guia de itens no Menu |
| **`P`** ou **`ESC`** | Pausa ou retoma a partida |
| **`F11`** | Alterna entre Modo Tela Cheia e Modo Janela |
| **`M`** | Ativa ou silencia o áudio do jogo |

---

## Elementos da Arena

* **Blocos:** Comuns (1 acerto), Reforçados Magenta (2 acertos), Aço Blindado (3 acertos), Explosivos Laranja (detonam blocos vizinhos) e Prismas Cinza (indestrutíveis).
* **Cápsulas Positivas (Arredondadas):** `EXP` (Aumenta raquete), `3X` (Triplica bolas), `LSR` (Canhões laser), `FGO` (Bola de fogo perfurante) e `+1V` (Vida extra, até o máximo de 5).
* **Armadilhas (Quadradas):** `-LARG` (Encolhe raquete), `FAST` (Aumenta velocidade da bola) e `INV` (Inverte os controles horizontais).

---

## Declaração de Uso de Inteligência Artificial Generativa (IAg)

* **Projeto:** Neon Breakout // Arcade Edition
* **Autores:** Ana Guisofi, Bernardo Abner, Enzo Giorgetti
* **Disciplina:** Design de Software
* **Ferramenta Utilizada:** Google Gemini

Declaramos que ferramentas de Inteligência Artificial Generativa (**Google Gemini**) foram utilizadas como recurso de apoio técnico durante o desenvolvimento deste projeto (aproximadamente 70% da estrutura base de código gerada com apoio da IA e 30% de adaptação, ajustes de regras, design de fases e validação pelos autores), especificamente nas seguintes etapas:

* **Arquitetura e Estruturação de Código:** Auxílio na organização modular do projeto em Python utilizando Programação Orientada a Objetos (`main.py`, `config.py`, `entidades.py`, `fases.py`, `audio.py` e `jogo.py`).
* **Implementação de Mecânicas e Áudio:** Apoio na escrita da lógica de física de colisões (reflexão por eixo de penetração), máquina de estados das telas, efeitos visuais (partículas, ondas de choque e *screen shake*) e síntese procedural de efeitos sonoros com PyGame (`audio.py`).
* **Depuração e Refinamento Iterativo:** Suporte na correção de bugs e na adaptação de funcionalidades conforme os testes e decisões de design dos autores, incluindo o balanceamento das dificuldades, a criação da tela de identificação do jogador e o painel de histórico de pontuações da sessão.

Todo o código gerado foi revisado, testado, ajustado e validado integralmente pelos autores do trabalho, que assumem total responsabilidade pelo funcionamento e entrega final do software.

* **Histórico/Anexo da interação com a IAg:** **(https://share.gemini.google/1P2f1mMRoodL)**
