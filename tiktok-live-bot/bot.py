"""
Bot para live interativa no TikTok.

Escuta a sua live e agradece quem entra, manda presente, segue,
compartilha, curte ou comenta: fala em voz alta (TTS) e mostra na tela
(overlay para OBS / TikTok LIVE Studio).

Uso:
    python bot.py @seu_usuario            # conecta na sua live
    python bot.py @seu_usuario --sem-voz  # só overlay, sem voz
    python bot.py --simular               # testa sem estar ao vivo
"""

import argparse
import json
import queue
import random
import re
import shutil
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import mensagens

PASTA = Path(__file__).parent


# ---------------------------------------------------------------- Config ---
class Config:
    # Segundos para não agradecer a mesma pessoa de novo pelo mesmo motivo
    ESPERA_ENTRADA = 600
    ESPERA_CURTIDA = 120
    # No máximo quantas falas ficam na fila de voz (o resto só aparece na tela)
    FILA_VOZ_MAX = 5
    # Falar entradas? Em live cheia, entradas chegam aos montes.
    FALAR_ENTRADAS = True
    # Curtidas mínimas (acumuladas por pessoa) para agradecer
    CURTIDAS_MIN = 15
    PORTA_OVERLAY = 8765


# ----------------------------------------------------------------- Voz -----
class Voz:
    """Fala em uma thread separada para não travar a conexão com a live."""

    def __init__(self, ativa: bool):
        self.fila: "queue.Queue[str]" = queue.Queue()
        self.ativa = ativa
        if ativa:
            threading.Thread(target=self._loop, daemon=True).start()

    def falar(self, texto: str, prioridade: bool = False):
        if not self.ativa:
            return
        # Presentes sempre entram; o resto é descartado se a fila estiver cheia
        if prioridade or self.fila.qsize() < Config.FILA_VOZ_MAX:
            self.fila.put(texto)

    def _loop(self):
        # Celular Android (Termux): usa a voz do próprio Android
        if shutil.which("termux-tts-speak"):
            print("[voz] usando a voz do Android (Termux:API)")
            while True:
                texto = self.fila.get()
                subprocess.run(["termux-tts-speak", "-l", "pt", "-n", "BR", texto])
        try:
            import pyttsx3
        except ImportError:
            print("[voz] pyttsx3 não instalado: rodando sem voz.")
            return
        motor = pyttsx3.init()
        for v in motor.getProperty("voices"):
            if "pt" in (v.id + str(v.languages) + v.name).lower():
                motor.setProperty("voice", v.id)
                break
        motor.setProperty("rate", 185)
        while True:
            texto = self.fila.get()
            motor.say(texto)
            motor.runAndWait()


# -------------------------------------------------------------- Overlay ----
class Overlay:
    """Servidor local: abra http://localhost:8765 no OBS como 'Navegador'."""

    def __init__(self, porta: int):
        self.eventos = deque(maxlen=100)
        self.contador = 0
        self.trava = threading.Lock()
        overlay = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path.startswith("/eventos"):
                    desde = int(self.path.partition("desde=")[2] or 0)
                    with overlay.trava:
                        novos = [e for e in overlay.eventos if e["id"] > desde]
                    corpo = json.dumps(novos).encode()
                    tipo = "application/json"
                elif self.path.startswith("/personagem"):
                    corpo = (PASTA / "personagem.html").read_bytes()
                    tipo = "text/html; charset=utf-8"
                else:
                    corpo = (PASTA / "overlay.html").read_bytes()
                    tipo = "text/html; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", tipo)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(corpo)

        srv = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        print(f"[overlay]    http://localhost:{porta}  (cartões)")
        print(f"[personagem] http://localhost:{porta}/personagem  (boneco animado)")

    def mostrar(self, tipo: str, texto: str):
        with self.trava:
            self.contador += 1
            self.eventos.append({"id": self.contador, "tipo": tipo, "texto": texto})


# ---------------------------------------------------------------- Bot ------
class Anfitriao:
    """Decide o que responder para cada evento."""

    def __init__(self, voz: Voz, overlay: Overlay):
        self.voz = voz
        self.overlay = overlay
        self.ultimos: dict[tuple[str, str], float] = {}
        self.curtidas: dict[str, int] = {}

    def _pode(self, tipo: str, quem: str, espera: float) -> bool:
        agora = time.time()
        chave = (tipo, quem)
        if agora - self.ultimos.get(chave, 0) < espera:
            return False
        self.ultimos[chave] = agora
        return True

    def _responder(self, tipo, modelos, falar=True, prioridade=False, **dados):
        texto = random.choice(modelos).format(**dados)
        hora = time.strftime("%H:%M:%S")
        print(f"[{hora}] {tipo:<12} {texto}")
        self.overlay.mostrar(tipo, texto)
        if falar:
            self.voz.falar(texto, prioridade)

    def entrou(self, nome, uid):
        if self._pode("entrou", uid, Config.ESPERA_ENTRADA):
            self._responder("entrou", mensagens.ENTROU, falar=Config.FALAR_ENTRADAS, nome=nome)

    def presente(self, nome, presente, qtd):
        self._responder("presente", mensagens.PRESENTE, prioridade=True,
                        nome=nome, presente=presente, qtd=qtd)

    def seguiu(self, nome, uid):
        if self._pode("seguiu", uid, 10**9):
            self._responder("seguiu", mensagens.SEGUIU, prioridade=True, nome=nome)

    def compartilhou(self, nome, uid):
        if self._pode("compartilhou", uid, 300):
            self._responder("compartilhou", mensagens.COMPARTILHOU, nome=nome)

    def curtiu(self, nome, uid, qtd):
        self.curtidas[uid] = self.curtidas.get(uid, 0) + qtd
        if self.curtidas[uid] >= Config.CURTIDAS_MIN and self._pode("curtiu", uid, Config.ESPERA_CURTIDA):
            self.curtidas[uid] = 0
            self._responder("curtiu", mensagens.CURTIU, nome=nome)

    def comentou(self, nome, texto):
        print(f"[{time.strftime('%H:%M:%S')}] comentario   {nome}: {texto}")
        t = texto.lower()
        for chave, resposta in mensagens.RESPOSTAS_COMENTARIO.items():
            # palavra inteira: "oi" não casa com "depois"
            if re.search(r"\b" + re.escape(chave) + r"\b", t):
                self._responder("comentario", [resposta], nome=nome)
                return


def nome_de(user) -> tuple[str, str]:
    if user is None:
        return "amigo", "?"
    nome = getattr(user, "nickname", "") or getattr(user, "unique_id", "") or "amigo"
    uid = str(getattr(user, "unique_id", None) or getattr(user, "id", nome))
    return nome, uid


# ------------------------------------------------------- Conexão TikTok ----
def conectar(usuario: str, bot: Anfitriao):
    from TikTokLive import TikTokLiveClient
    from TikTokLive.events import (CommentEvent, ConnectEvent, DisconnectEvent,
                                   FollowEvent, GiftEvent, JoinEvent, LikeEvent,
                                   LiveEndEvent, ShareEvent)

    cliente = TikTokLiveClient(unique_id=usuario)

    @cliente.on(ConnectEvent)
    async def _(ev: ConnectEvent):
        print(f"Conectado na live de @{ev.unique_id}! (sala {ev.room_id})")
        bot.overlay.mostrar("sistema", "Bot conectado! Bora!")

    @cliente.on(JoinEvent)
    async def _(ev: JoinEvent):
        bot.entrou(*nome_de(ev.user))

    @cliente.on(GiftEvent)
    async def _(ev: GiftEvent):
        # Presentes em sequência (combo) só são agradecidos quando o combo termina
        if ev.streaking:
            return
        nome, _uid = nome_de(ev.user)
        presente = getattr(ev.gift, "name", None) or "presente"
        bot.presente(nome, presente, ev.repeat_count or 1)

    @cliente.on(FollowEvent)
    async def _(ev: FollowEvent):
        bot.seguiu(*nome_de(ev.user))

    @cliente.on(ShareEvent)
    async def _(ev: ShareEvent):
        bot.compartilhou(*nome_de(ev.user))

    @cliente.on(LikeEvent)
    async def _(ev: LikeEvent):
        bot.curtiu(*nome_de(ev.user), ev.count or 1)

    @cliente.on(CommentEvent)
    async def _(ev: CommentEvent):
        bot.comentou(nome_de(ev.user)[0], ev.content or "")

    @cliente.on(DisconnectEvent)
    async def _(ev):
        print("Desconectado da live.")

    @cliente.on(LiveEndEvent)
    async def _(ev):
        print("A live terminou. Até a próxima!")

    print(f"Conectando na live de {usuario}... (a live precisa já estar no ar)")
    cliente.run()


def simular(bot: Anfitriao):
    print("Modo simulação: gerando eventos falsos. Ctrl+C para sair.")
    nomes = ["Ana", "Joao", "Maria", "Pedro", "Carla", "Lucas"]
    presentes = ["Rosa", "TikTok", "Coração", "Leão", "Galáxia"]
    while True:
        n = random.choice(nomes)
        acao = random.choice(["entrou", "entrou", "presente", "seguiu", "compartilhou", "curtiu", "comentou"])
        if acao == "entrou":
            bot.entrou(n, n)
        elif acao == "presente":
            bot.presente(n, random.choice(presentes), random.randint(1, 10))
        elif acao == "seguiu":
            bot.seguiu(n, n)
        elif acao == "compartilhou":
            bot.compartilhou(n, n)
        elif acao == "curtiu":
            bot.curtiu(n, n, 20)
        else:
            bot.comentou(n, random.choice(["oi!", "salve salve", "de onde vc é?", "kkkk"]))
        time.sleep(2)


def main():
    p = argparse.ArgumentParser(description="Bot de agradecimento para live no TikTok")
    p.add_argument("usuario", nargs="?", help="seu @ do TikTok, ex: @ernbr")
    p.add_argument("--simular", action="store_true", help="testa com eventos falsos")
    p.add_argument("--sem-voz", action="store_true", help="não fala, só mostra na tela")
    p.add_argument("--porta", type=int, default=Config.PORTA_OVERLAY)
    a = p.parse_args()

    bot = Anfitriao(Voz(not a.sem_voz), Overlay(a.porta))
    try:
        if a.simular:
            simular(bot)
        elif a.usuario:
            conectar(a.usuario if a.usuario.startswith("@") else "@" + a.usuario, bot)
        else:
            p.error("informe seu @ do TikTok ou use --simular")
    except KeyboardInterrupt:
        print("\nTchau!")


if __name__ == "__main__":
    main()
