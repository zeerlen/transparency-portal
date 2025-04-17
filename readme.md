# RPA do Portal da Transparência

Esse projeto é uma ferramenta que automatiza a busca de informações no Portal da Transparência do Brasil. Ele entra no site, pega dados de pessoas (como nome e CPF) e organiza tudo em arquivos fáceis de usar. É ideal pra quem quer acessar essas informações de forma rápida e sem complicação.

## Este projeto ainda está em desenvolvimento...

## O que já tá pronto

- **Busca fácil**: Você dá um nome e CPF, e o sistema vai no Portal da Transparência buscar os dados certinho. Pode usar NIS também, se quiser.
- **Dados organizados**: Tudo que ele encontra vira um arquivo JSON com nome bem claro, tipo `456789_25-12-2023_14-30-00.json`, com o CPF e a data direitinho.
- **Checagem esperta**: O sistema valida o CPF (tem que ter 6 dígitos) e não deixa passar nada errado.
- **Segunda chance**: Se o site der problema, ele tenta de novo sozinho. Se ainda assim não rolar, tira uma foto da tela pra te ajudar a entender.
- **Estrutura redonda**: Já tá tudo organizado em pastas pra guardar resultados, logs e as ferramentas que fazem o sistema rodar.


## O que ainda falta

- **API**