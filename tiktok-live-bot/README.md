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

### Mostrar os agradecimentos na tela da live
No **TikTok LIVE Studio** ou **OBS**: adicione uma fonte **Navegador / Link**
com o endereço `http://localhost:8765`, tamanho 1080x1920. O fundo é
transparente; os cartões aparecem no canto inferior esquerdo.

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
