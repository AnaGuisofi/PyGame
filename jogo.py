"""
Módulo controlador principal do jogo Breakout.

Gerencia o modo tela cheia, seletor de dificuldade, entrada do nome do jogador,
exibição das pontuações da sessão, máquina de estados das telas, física de
colisões, inimigos e chefão final.
"""

import math
import random
import pygame
from audio import GerenciadorAudio
from config import (
    ALTURA_TELA,
    BOLA_VELOCIDADE_MAXIMA,
    CADENCIA_LASER,
    COR_DESTAQUE_AMARELO,
    COR_DESTAQUE_CIANO,
    COR_DESTAQUE_LARANJA,
    COR_DESTAQUE_MAGENTA,
    COR_DESTAQUE_VERDE,
    COR_FUNDO,
    COR_PERIGO_ROXO,
    COR_PERIGO_VERMELHO,
    COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO,
    DIFICULDADES,
    FPS,
    LARGURA_TELA,
    ORDEM_DIFICULDADES,
    TELA_CHEIA_INICIAL,
    TIPOS_ARMADILHA,
    TIPOS_POWERUP,
    TITULO_JOGO,
    VIDAS_INICIAIS,
    VIDAS_MAXIMAS,
)
from entidades import (
    Bola,
    Capsula,
    FundoAnimado,
    OndaChoque,
    Particula,
    ProjetilLaser,
    Raquete,
    TextoFlutuante,
)
from fases import GerenciadorFases


class JogoBreakout:
    """Orquestra o loop principal, eventos, regras e renderização do jogo."""

    def __init__(self):
        """Inicializa PyGame em tela cheia, fontes, áudio e estado inicial."""
        pygame.init()
        self.tela_cheia = TELA_CHEIA_INICIAL
        self.tela = self._configurar_janela(self.tela_cheia)
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("consolas", 50, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_hud = pygame.font.SysFont("consolas", 19, bold=True)
        self.fonte_texto = pygame.font.SysFont("consolas", 17)
        self.fonte_pequena = pygame.font.SysFont("consolas", 14, bold=True)

        self.audio = GerenciadorAudio()
        self.gerenciador_fases = GerenciadorFases()
        self.fundo = FundoAnimado()

        self.indice_dificuldade = 0
        self.estado = "MENU"
        self.nome_jogador = ""
        self.pontuacao = 0
        self.historico_partidas = []
        self.vidas = VIDAS_INICIAIS
        self.fase_atual = 0
        self.combo = 0
        self.vitoria_final = False
        self.tremor_tela = 0.0
        self.tempo_global = 0.0

        self.raquete = Raquete()
        self.bolas = []
        self.tijolos = []
        self.drones = []
        self.chefao = None
        self.capsulas = []
        self.lasers = []
        self.tiros_inimigos = []
        self.particulas = []
        self.ondas_choque = []
        self.textos_flutuantes = []

        self.audio.iniciar_musica()

    def _configurar_janela(self, ativar_tela_cheia):
        """Cria ou alterna a janela entre tela cheia escalonada e modo janela."""
        flags = (pygame.FULLSCREEN | pygame.SCALED) if ativar_tela_cheia else pygame.SCALED
        return pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), flags)

    def alternar_tela_cheia(self):
        """Alterna dinamicamente entre tela cheia e modo janela."""
        self.tela_cheia = not self.tela_cheia
        self.tela = self._configurar_janela(self.tela_cheia)

    @property
    def cfg_dificuldade(self):
        """Retorna o dicionário de parâmetros da dificuldade selecionada."""
        chave = ORDEM_DIFICULDADES[self.indice_dificuldade]
        return DIFICULDADES[chave]

    def _mudar_dificuldade(self, delta):
        """Altera o nível de dificuldade selecionado no menu."""
        self.indice_dificuldade = (self.indice_dificuldade + delta) % len(ORDEM_DIFICULDADES)
        self.audio.tocar("menu_select")

    def iniciar_novo_jogo(self):
        """Reseta placar, vidas e carrega a primeira fase na dificuldade escolhida."""
        if not self.nome_jogador.strip():
            self.nome_jogador = "JOGADOR"
        self.pontuacao = 0
        self.vidas = VIDAS_INICIAIS
        self.fase_atual = 0
        self.combo = 0
        self.vitoria_final = False
        self._carregar_fase(0)
        self.estado = "JOGANDO"

    def _finalizar_partida(self, venceu):
        """Registra a pontuação do jogador no histórico da sessão e encerra."""
        self.vitoria_final = venceu
        self.historico_partidas.insert(
            0,
            {
                "nome": self.nome_jogador,
                "pontos": self.pontuacao,
                "dificuldade": self.cfg_dificuldade["rotulo"],
            },
        )
        self.historico_partidas = self.historico_partidas[:4]
        self.estado = "FIM_DE_JOGO"

    def _carregar_fase(self, indice):
        """Prepara blocos, inimigos, chefão e reposiciona raquete e bola."""
        cfg = self.cfg_dificuldade
        self.fase_atual = indice
        self.tijolos, self.drones, self.chefao = self.gerenciador_fases.construir_fase(
            indice, cfg["vel_inimigo"], cfg["vida_chefao"]
        )
        self.capsulas.clear()
        self.lasers.clear()
        self.tiros_inimigos.clear()
        self.particulas.clear()
        self.ondas_choque.clear()
        self.textos_flutuantes.clear()
        self.raquete.resetar(largura_base=cfg["largura_raquete"])
        self._criar_bola_presa()

    def _criar_bola_presa(self):
        """Cria uma bola inicial posicionada sobre a raquete."""
        vel_base = self.cfg_dificuldade["vel_bola"] + self.fase_atual * 24.0
        bola = Bola(
            self.raquete.rect.centerx,
            self.raquete.rect.top - 12,
            presa=True,
            velocidade=vel_base,
        )
        self.bolas = [bola]

    def _disparar_acao_principal(self):
        """Lança bolas presas ou dispara lasers quando o power-up está ativo."""
        lancou = False
        for bola in self.bolas:
            if bola.presa:
                bola.lancar()
                lancou = True

        if lancou:
            self.audio.tocar("raquete")
            return

        if (
            self.raquete.tempo_laser > 0
            and self.raquete.recarga_laser <= 0
            and self.raquete.tempo_choque <= 0
        ):
            self.lasers.append(ProjetilLaser(self.raquete.rect.left + 7, self.raquete.rect.top))
            self.lasers.append(ProjetilLaser(self.raquete.rect.right - 7, self.raquete.rect.top))
            self.raquete.recarga_laser = CADENCIA_LASER
            self.audio.tocar("laser")

    def _processar_digitacao_nome(self, evento):
        """Trata a digitação do nome do jogador antes de iniciar a partida."""
        if evento.key == pygame.K_ESCAPE:
            self.audio.tocar("menu_select")
            self.estado = "MENU"
        elif evento.key == pygame.K_RETURN:
            self.audio.tocar("menu_select")
            self.iniciar_novo_jogo()
        elif evento.key == pygame.K_BACKSPACE:
            self.nome_jogador = self.nome_jogador[:-1]
        elif evento.unicode and evento.unicode.isprintable():
            if len(self.nome_jogador) < 16:
                self.nome_jogador += evento.unicode.upper()

    def _processar_eventos(self):
        """Trata entradas de teclado, mouse e fechamento da janela."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEMOTION and self.estado == "JOGANDO":
                self.raquete.mover_mouse(evento.pos[0])

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.estado == "JOGANDO":
                    self._disparar_acao_principal()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    self.alternar_tela_cheia()
                    continue

                if self.estado == "NOME_JOGADOR":
                    self._processar_digitacao_nome(evento)
                    continue

                if evento.key == pygame.K_m:
                    self.audio.alternar_mudo()

                if self.estado == "MENU":
                    if evento.key in (pygame.K_LEFT, pygame.K_a):
                        self._mudar_dificuldade(-1)
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        self._mudar_dificuldade(1)
                    elif evento.key == pygame.K_1:
                        self.indice_dificuldade = 0
                        self.audio.tocar("menu_select")
                    elif evento.key == pygame.K_2:
                        self.indice_dificuldade = 1
                        self.audio.tocar("menu_select")
                    elif evento.key == pygame.K_3:
                        self.indice_dificuldade = 2
                        self.audio.tocar("menu_select")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self.estado = "NOME_JOGADOR"
                    elif evento.key == pygame.K_i:
                        self.audio.tocar("menu_select")
                        self.estado = "INSTRUCOES"
                    elif evento.key == pygame.K_ESCAPE:
                        return False

                elif self.estado == "INSTRUCOES":
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_i):
                        self.audio.tocar("menu_select")
                        self.estado = "MENU"

                elif self.estado == "JOGANDO":
                    if evento.key == pygame.K_SPACE:
                        self._disparar_acao_principal()
                    elif evento.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.estado = "PAUSADO"

                elif self.estado == "PAUSADO":
                    if evento.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN):
                        self.estado = "JOGANDO"
                    elif evento.key == pygame.K_q:
                        self.estado = "MENU"

                elif self.estado == "TRANSICAO_FASE":
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self._carregar_fase(self.fase_atual + 1)
                        self.estado = "JOGANDO"

                elif self.estado == "FIM_DE_JOGO":
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.tocar("menu_select")
                        self.iniciar_novo_jogo()
                    elif evento.key == pygame.K_n:
                        self.audio.tocar("menu_select")
                        self.nome_jogador = ""
                        self.estado = "NOME_JOGADOR"
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU"

        return True

    def _atualizar_tijolos_moveis(self, dt):
        """Atualiza tijolos e inverte a direção sincronizada das fileiras móveis."""
        for tijolo in self.tijolos:
            tijolo.atualizar(dt)

        linhas_reverter = set()
        for tijolo in self.tijolos:
            if tijolo.vx < 0 and tijolo.rect.left <= 18:
                linhas_reverter.add(tijolo.linha_id)
            elif tijolo.vx > 0 and tijolo.rect.right >= LARGURA_TELA - 18:
                linhas_reverter.add(tijolo.linha_id)

        if linhas_reverter:
            for tijolo in self.tijolos:
                if tijolo.linha_id in linhas_reverter:
                    tijolo.vx = -tijolo.vx