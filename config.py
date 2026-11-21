# Módulo de configurações globais do jogo Breakout Neon.
# Centraliza constantes de tela, presets de dificuldade, física, paleta de cores, pontuação e parâmetros de balanceamento das entidades.

# Dimensões lógicas da janela e taxa de quadros
LARGURA_TELA = 960
ALTURA_TELA = 700
FPS = 60
TITULO_JOGO = 'NEON BREAKOUT // ARCADE EDITION'
TELA_CHEIA_INICIAL = True

# Paleta de cores (estilo Synthwave / Arcade Retrô)
COR_FUNDO = (10, 12, 26)
COR_GRADE = (32, 24, 68)
COR_GRADE_BRILHO = (68, 42, 130)
COR_BORDA_NEON = (0, 240, 255)
COR_TEXTO_PRINCIPAL = (245, 248, 255)
COR_TEXTO_SECUNDARIO = (165, 180, 215)
COR_DESTAQUE_CIANO = (0, 245, 255)
COR_DESTAQUE_MAGENTA = (255, 45, 145)
COR_DESTAQUE_AMARELO = (255, 215, 0)
COR_DESTAQUE_VERDE = (50, 255, 130)
COR_DESTAQUE_LARANJA = (255, 130, 30)
COR_PERIGO_VERMELHO = (255, 45, 70)
COR_PERIGO_ROXO = (195, 55, 255)

# Presets de dificuldade selecionáveis no menu
ORDEM_DIFICULDADES = ['NORMAL', 'DIFICIL', 'INSANO']

DIFICULDADES = {
    'NORMAL': {
        'rotulo': 'NORMAL',
        'cor': (50, 255, 130),
        'vel_bola': 440.0,
        'largura_raquete': 128,
        'chance_drop': 0.26,
        'chance_armadilha': 0.18,
        'duracao_efeito': 7.0,
        'vel_inimigo': 90.0,
        'vida_chefao': 12,
    },
    'DIFICIL': {
        'rotulo': 'DIFICIL',
        'cor': (255, 215, 0),
        'vel_bola': 555.0,
        'largura_raquete': 98,
        'chance_drop': 0.26,
        'chance_armadilha': 0.52,
        'duracao_efeito': 6.0,
        'vel_inimigo': 160.0,
        'vida_chefao': 24,
    },
    'INSANO': {
        'rotulo': 'INSANO',
        'cor': (255, 45, 70),
        'vel_bola': 635.0,
        'largura_raquete': 84,
        'chance_drop': 0.30,
        'chance_armadilha': 0.68,
        'duracao_efeito': 5.0,
        'vel_inimigo': 210.0,
        'vida_chefao': 32,
    },
}

# Configurações da Raquete
RAQUETE_LARGURA_PADRAO = 128
RAQUETE_LARGURA_EXPANDIDA = 175
RAQUETE_LARGURA_ENCOLHIDA = 62
RAQUETE_ALTURA = 18
RAQUETE_VELOCIDADE = 660.0
RAQUETE_MARGEM_INFERIOR = 48

# Configurações da Bola
BOLA_RAIO = 9
BOLA_VELOCIDADE_INICIAL = 440.0
BOLA_VELOCIDADE_MAXIMA = 840.0
BOLA_TAMANHO_RASTRO = 12

# Configurações dos Tijolos
TIJOLO_COLUNAS = 11
TIJOLO_LARGURA = 74
TIJOLO_ALTURA = 26
TIJOLO_ESPACAMENTO = 6
TIJOLO_MARGEM_SUPERIOR = 88

# Tipos de Tijolos: (resistência, pontos, cor_principal, cor_borda)
# Resistência -1 indica bloco indestrutível
TIPOS_TIJOLO = {
    1: (1, 100, (0, 210, 245), (140, 250, 255)),  # Ciano -1 hit
    2: (1, 120, (50, 230, 130), (160, 255, 200)),  # Verde -1 hit
    3: (1, 150, (255, 200, 30), (255, 240, 150)),  # Amarelo - 1 hit
    4: (2, 250, (255, 65, 140), (255, 165, 205)),  # Magenta Reforçado - 2 hits
    5: (3, 400, (150, 165, 190), (235, 245, 255)),  # Aço Blindado - 3 hits
    6: (1, 300, (255, 105, 20), (255, 215, 100)),  # Explosivo - detona vizinhos
    7: (-1, 0, (68, 76, 115), (145, 160, 225)),  # Prisma Indestrutível
}

# Configurações de Cápsulas (Power-ups positivos e Armilhas negativas)
CAPSULA_VELOCIDADE_QUEDA = 215.0

TIPOS_POWERUP = {
    'EXPANDIR': ('EXP', (0, 245, 255)),
    'MULTIBOLA': ('3X', (255, 45, 145)),
    'LASER': ('LSR', (255, 130, 30)),
    'FOGO': ('FGO', (255, 215, 100)),
    'VIDA': ('+1', (50, 255, 130)),
}

TIPOS_ARMADILHA = {
    'ENCOLHER': ('-LARG', (255, 45, 70)),
    'TURBO': ('FAST', (255, 95, 40)),
    'INVERTER': ('INV', (195, 55, 255)),
}

# Regras gerais
VIDAS_INICIAIS = 3
VIDAS_MAXIMAS = 5
CADENCIA_LASER = 0.36