"""
Módulo de síntese e gerenciamento de áudio procedural.

Gera efeitos sonoros estilo arcade 16-bit e trilha ambiente diretamente em
memória via pygame.mixer, dispensando arquivos externos de áudio.
"""

import array
import math
import pygame


class GerenciadorAudio:
    """Sintetiza e controla todos os efeitos sonoros e a música de fundo."""

    def __init__(self):
        """Inicializa o mixer e gera os buffers sonoros do jogo."""
        self.ativo = True
        self.disponivel = False
        self.sons = {}
        self.canal_musica = None
        self.musica_ambiente = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.disponivel = True
            self._criar_efeitos()
            self._criar_musica_ambiente()
        except pygame.error:
            self.disponivel = False

    def _sintetizar_onda(self, notas, tipo="square", volume=0.25):
        """
        Gera um objeto pygame.mixer.Sound a partir de uma sequência de notas.

        Args:
            notas (list[tuple[float, float]]): Lista de pares (frequencia_hz, duracao_s).
            tipo (str): Formato da onda ('sine', 'square' ou 'triangle').
            volume (float): Amplitude relativa entre 0.0 e 1.0.

        Returns:
            pygame.mixer.Sound: Objeto de som pronto para reprodução.
        """
        taxa = 44100
        amostras = array.array("h")

        for freq, duracao in notas:
            total_amostras = int(taxa * duracao)
            for i in range(total_amostras):
                t = i / taxa
                envelope = 1.0
                if i < 150:
                    envelope = i / 150.0
                elif i > total_amostras - 300:
                    envelope = max(0.0, (total_amostras - i) / 300.0)

                if freq <= 0:
                    onda = 0.0
                else:
                    fase = 2.0 * math.pi * freq * t
                    if tipo == "sine":
                        onda = math.sin(fase)
                    elif tipo == "triangle":
                        onda = 2.0 * abs(2.0 * ((freq * t) % 1.0) - 1.0) - 1.0
                    else:
                        onda = 1.0 if math.sin(fase) >= 0 else -1.0

                valor = int(max(-32767, min(32767, onda * envelope * volume * 32767)))
                amostras.append(valor)

        return pygame.mixer.Sound(buffer=amostras)

    def _criar_efeitos(self):
        """Prepara todos os efeitos sonoros utilizados nas interações do jogo."""
        self.sons["raquete"] = self._sintetizar_onda(
            [(440, 0.045), (587.33, 0.055)], tipo="triangle", volume=0.28
        )
        self.sons["parede"] = self._sintetizar_onda(
            [(310, 0.04)], tipo="sine", volume=0.20
        )
        self.sons["tijolo"] = self._sintetizar_onda(
            [(523.25, 0.04), (659.25, 0.06)], tipo="square", volume=0.22
        )
        self.sons["metal"] = self._sintetizar_onda(
            [(980, 0.03), (740, 0.05)], tipo="triangle", volume=0.25
        )
        self.sons["explosao"] = self._sintetizar_onda(
            [(180, 0.06), (130, 0.08), (85, 0.12)], tipo="square", volume=0.30
        )
        self.sons["powerup"] = self._sintetizar_onda(
            [(523.25, 0.05), (659.25, 0.05), (783.99, 0.05), (1046.50, 0.10)],
            tipo="triangle",
            volume=0.28,
        )
        self.sons["armadilha"] = self._sintetizar_onda(
            [(320, 0.06), (240, 0.07), (155, 0.12)],
            tipo="square",
            volume=0.28,
        )
        self.sons["laser"] = self._sintetizar_onda(
            [(1200, 0.025), (750, 0.035), (420, 0.04)], tipo="square", volume=0.18
        )
        self.sons["drone"] = self._sintetizar_onda(
            [(720, 0.03), (960, 0.04)], tipo="sine", volume=0.24
        )
        self.sons["chefao_hit"] = self._sintetizar_onda(
            [(220, 0.05), (165, 0.06), (290, 0.06)], tipo="square", volume=0.30
        )
        self.sons["chefao_tiro"] = self._sintetizar_onda(
            [(880, 0.03), (520, 0.04), (260, 0.05)], tipo="triangle", volume=0.22
        )
        self.sons["choque"] = self._sintetizar_onda(
            [(190, 0.04), (420, 0.04), (140, 0.08)], tipo="square", volume=0.30
        )
        self.sons["perder_vida"] = self._sintetizar_onda(
            [(392.0, 0.10), (349.23, 0.10), (293.66, 0.12), (220.0, 0.22)],
            tipo="square",
            volume=0.26,
        )
        self.sons["vitoria_fase"] = self._sintetizar_onda(
            [
                (523.25, 0.08),
                (659.25, 0.08),
                (783.99, 0.08),
                (1046.50, 0.18),
                (783.99, 0.08),
                (1046.50, 0.25),
            ],
            tipo="triangle",
            volume=0.30,
        )
        self.sons["menu_select"] = self._sintetizar_onda(
            [(660, 0.05), (880, 0.07)], tipo="sine", volume=0.22
        )

    def _criar_musica_ambiente(self):
        """Cria um loop melódico synthwave suave para tocar durante o jogo."""
        arpejo = [
            (110.00, 0.18),
            (164.81, 0.18),
            (220.00, 0.18),
            (261.63, 0.18),
            (220.00, 0.18),
            (164.81, 0.18),
            (130.81, 0.18),
            (196.00, 0.18),
            (98.00, 0.18),
            (146.83, 0.18),
            (196.00, 0.18),
            (246.94, 0.18),
            (196.00, 0.18),
            (146.83, 0.18),
            (110.00, 0.18),
            (164.81, 0.18),
        ]
        self.musica_ambiente = self._sintetizar_onda(
            arpejo, tipo="triangle", volume=0.08
        )

    def tocar(self, nome):
        """
        Reproduz um efeito sonoro pelo nome cadastrado.

        Args:
            nome (str): Identificador do som (ex: 'raquete', 'tijolo', 'armadilha').
        """
        if self.disponivel and self.ativo and nome in self.sons:
            self.sons[nome].play()

    def iniciar_musica(self):
        """Inicia o loop da trilha ambiente caso o áudio esteja ativo."""
        if not self.disponivel or not self.ativo or not self.musica_ambiente:
            return
        if self.canal_musica is None or not self.canal_musica.get_busy():
            self.canal_musica = self.musica_ambiente.play(loops=-1)

    def parar_musica(self):
        """Interrompe a reprodução da trilha ambiente."""
        if self.canal_musica is not None:
            self.canal_musica.stop()

    def alternar_mudo(self):
        """Liga ou desliga todos os sons do jogo."""
        self.ativo = not self.ativo
        if not self.ativo:
            self.parar_musica()
        else:
            self.iniciar_musica()