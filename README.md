# Docker_IADub
Dublador automático de vídeos (Local)

Este projeto é um sistema automatizado que realiza a dublagem completa de vídeos,
convertendo conteúdo originalmente em inglês para português de forma totalmente local, sem depender de serviços externos.

O sistema segue um pipeline sequencial de processamento:
vídeo → áudio → transcrição → tradução → síntese de voz → vídeo final

Estrutura:
/input   → vídeos originais<br>
/output  → vídeos dublados<br>
/temp    → arquivos intermediários<br>
/app     → código do pipeline<br>
