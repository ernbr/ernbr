# 🎥 Bot de Live Interativa no TikTok

Durante a sua live, o bot **agradece automaticamente** quem:

| Evento | O que acontece |
|---|---|
| 👋 Entrou na live | "Seja bem-vindo, Fulano! Obrigado por entrar na live!" |
| 🎁 Mandou presente | "Muito obrigado pela Rosa, Fulano! Você é demais!" |
| ⭐ Seguiu | "Obrigado por seguir, Fulano! Bem-vindo à família!" |
| 🔁 Compartilhou | "Valeu por compartilhar a live, Fulano!" |
| ❤️ Curtiu bastante | "Obrigado pelas curtidas, Fulano!" |
| 💬 Comentou "oi", "salve"... | Responde na hora |

Ele **fala em voz alta** (o microfone da live capta) e **mostra na tela** com
um overlay animado.

## Como usar

1. Instale o Python 3.10+ e, nesta pasta, rode:
   ```bash
   pip install -r requirements.txt
   ```
2. Teste sem estar ao vivo:
   ```bash
   python bot.py --simular
   ```
3. Abra a live no TikTok (celular ou **TikTok LIVE Studio** no PC).
4. Com a live **já no ar**, rode:
   ```bash
   python bot.py @seu_usuario
   ```

## 📱 Rodar no celular (Android)

Dá para fazer a live pelo app do TikTok e deixar o bot rodando no mesmo
celular, falando os agradecimentos pelo alto-falante.

1. Instale pela **F-Droid** (não pela Play Store, que tem versão velha):
   **Termux** e **Termux:API**.
2. Abra o Termux e rode (demora uns minutos na primeira vez):
   ```bash
   pkg update -y
   pkg install -y python git rust termux-api
   pip install "setuptools<70" wheel
   pip install --no-build-isolation protobuf3-to-dict
   pip install TikTokLive
   git clone -b claude/tiktok-live-interativa-5m8vbk https://github.com/ernbr/ernbr
   cd ernbr/tiktok-live-bot
   ```
3. Teste a voz: `python bot.py --simular` (Ctrl+C para parar).
4. Para o Android não matar o bot em segundo plano: puxe a notificação do
   Termux e toque em **Acquire wakelock**. Nas configurações do Android,
   tire o Termux da **otimização de bateria**.
5. Abra a live no app do TikTok. Com ela já no ar, volte ao Termux e rode
   `python bot.py @seu_usuario`, depois volte para o TikTok.

Dicas para o celular:
- Deixe o volume de mídia alto: o microfone da live capta a voz do bot.
  Fone de ouvido **não** serve, porque aí só você escuta.
- O overlay na tela não funciona na live pelo app do celular. Só a voz.
- Em live cheia, desligue `FALAR_ENTRADAS` em `bot.py` para o bot não falar sem parar.
- **iPhone não funciona**: o iOS não deixa rodar esse tipo de programa em
  segundo plano. Nesse caso, rode no PC.

### Mostrar os agradecimentos na tela da live
No **TikTok LIVE Studio** ou **OBS**: adicione uma fonte **Navegador / Link**
com o endereço `http://localhost:8765`, tamanho 1080x1920. O fundo é
transparente; os cartões aparecem no canto inferior esquerdo.

### 🤖 Personagem animado (mascote do FatoClaro)
Adicione outra fonte **Navegador** com `http://localhost:8765/personagem`.
O mascote é um herói de moletom com lupa e um ✓ no peito, desenhado no estilo
de rabisco (doodle) dos vídeos do canal. Ele fica no canto inferior direito e
reage a cada evento com um balão de fala:
acena para quem entra, pula e solta confete com presente, gira com novo seguidor,
dança com curtidas e mexe a boca enquanto "fala".
- `?fundo=verde` → fundo verde para chroma key (se o programa não aceitar transparência).
- `?entradas=nao` → não reage a quem entra (live cheia).
- Cores: mude as variáveis no topo de `personagem.html` (`--moletom`, `--alerta`, `--certo`, `--pele`...).

### 🎙️ Voz do bot direto na live (sem passar pelo microfone)
No **TikTok LIVE Studio** ou **OBS**, adicione uma fonte de **áudio do sistema /
captura de áudio do desktop**. A voz do bot entra limpa na transmissão, mesmo com
fone de ouvido. No celular isso não é possível: lá a voz precisa sair pelo
alto-falante para o microfone captar.

### Opções
- `--sem-voz` → só overlay, sem falar.
- `--porta 9000` → muda a porta do overlay.

## Personalizar
- **Frases:** edite `mensagens.py` (use `{nome}`, `{presente}`, `{qtd}`).
- **Comportamento:** a classe `Config` em `bot.py` controla tempo de espera
  antes de agradecer a mesma pessoa de novo, se fala as entradas (em live
  cheia vale desligar `FALAR_ENTRADAS`), curtidas mínimas etc.

## Observações
- O bot **não escreve no chat** do TikTok; ele responde por voz e na tela.
  Escrever no chat exigiria usar sua sessão logada, o que é arriscado para a conta.
- Usa a biblioteca não oficial [TikTokLive](https://github.com/isaackogan/TikTokLive).
  Se o TikTok mudar algo e parar de conectar, atualize: `pip install -U TikTokLive`.
- Presentes em combo são agradecidos uma vez só, quando o combo termina.
- Se a voz sair em inglês, instale uma voz em português no sistema
  (Windows: Configurações → Hora e idioma → Fala).
