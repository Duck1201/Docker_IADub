<img width="1536" height="1024" alt="Dublagem automática com IA e privacidade" src="https://github.com/user-attachments/assets/c1accb98-0dcb-4599-adbe-98f298841ba1" />
<br>
<h2>Dublador automático de vídeos (Local)</h2>

Este projeto é um sistema automatizado que realiza a dublagem completa de vídeos,
convertendo conteúdo originalmente em inglês para português de forma totalmente local, sem depender de serviços externos.

O sistema segue um pipeline sequencial de processamento:
vídeo → áudio → transcrição → tradução → síntese de voz → vídeo final

<h3>Estrutura:</h3>
/input   → vídeos originais<br>
/output  → vídeos dublados<br>
/temp    → arquivos intermediários<br>
/app     → código do pipeline<br>
