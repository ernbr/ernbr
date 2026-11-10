"""
Mensagens que o bot fala/mostra na live.
Edite à vontade! Use {nome} para o nome da pessoa, {presente} para o nome
do presente e {qtd} para a quantidade. Uma frase é sorteada de cada lista.
"""

ENTROU = [
    "Seja bem-vindo, {nome}! Obrigado por entrar na live!",
    "E aí, {nome}! Que bom te ver por aqui!",
    "Chegou {nome}! Fica à vontade, tá em casa!",
    "Chegou {nome}! Aqui no FatoClaro é informação sem enrolação.",
]

PRESENTE = [
    "Muito obrigado pelo {presente}, {nome}! Você é demais!",
    "Valeu demais, {nome}! {qtd} {presente}! Tamo junto!",
    "{nome} mandou {qtd} {presente}! Obrigadão!",
    "Fato claro: {nome} é demais! Valeu pelo {presente}!",
]

SEGUIU = [
    "Obrigado por seguir, {nome}! Bem-vindo à família!",
    "{nome} agora faz parte do time! Valeu por seguir!",
    "Valeu por seguir, {nome}! Agora nenhum golpe te pega desprevenido.",
]

COMPARTILHOU = [
    "Valeu por compartilhar a live, {nome}!",
    "{nome} compartilhou a live! Obrigado por espalhar!",
]

CURTIU = [
    "Obrigado pelas curtidas, {nome}!",
    "Chuva de coração do {nome}! Valeu!",
]

# Comentários: se o texto contiver a chave, o bot responde com o valor.
RESPOSTAS_COMENTARIO = {
    "oi": "Oi, {nome}! Tudo bem?",
    "salve": "Salve, {nome}!",
    "de onde": "{nome}, eu sou do Brasil! E você, de onde fala?",
    "golpe": "{nome}, na dúvida, não clica e não paga! Conta aqui o que aconteceu.",
    "pix": "{nome}, Pix enviado não volta fácil. Sempre confira o nome de quem recebe!",
}
