# GuihGuih Cyber

<img src="guihguih_cyber/assets/logo.png" alt="Logo oficial do GuihGuih Cyber" width="144">

Aplicativo desktop local para Windows, Linux e macOS. Inclui scanner em Python com SHA-256 e regras explicáveis, histórico SQLite, monitoramento de pastas adicionado pelo usuário, cópia de quarentena reversível e interface PySide6. Tkinter permanece como alternativa mínima.

## Executar no Windows

Requer Python 3.12+. No PowerShell:

```powershell
cd 'D:\#codex\Aplicativos\GuihGuih Cyber'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m guihguih_cyber.desktop
```

Se a instalação do PySide6 falhar ou quiser abrir a interface mínima sem Qt:

```powershell
cd 'D:\#codex\Aplicativos\GuihGuih Cyber'
.\.venv\Scripts\python.exe -m guihguih_cyber.app
```

A interface oferece análise de uma pasta escolhida, da pasta pessoal ou de um arquivo. O scanner lê arquivos em blocos, calcula SHA-256, aplica regras locais explicáveis e grava sessões em SQLite no diretório de dados do usuário.

## Testes

```powershell
python -m pytest
```

Os testes usam fixtures sintéticas. O marcador EICAR utilizado é texto inofensivo, não malware executável.

## Recursos e limites

- Funcionais: scanner manual, hash SHA-256, regras heurísticas explicáveis, cancelamento, histórico SQLite, monitoramento por polling em pastas escolhidas pelo usuário e quarentena por cópia com hash e restauração confirmada sem sobrescrita.
- Configurações: intervalo do polling (1, 2 ou 5 s) e sensibilidade do alerta de mudanças rápidas, persistidos localmente.
- Monitor experimental contra rajadas: alerta quando vários arquivos distintos em pastas monitoradas mudam em 10 s. É heurístico, depende do polling, pode gerar falsos positivos e não bloqueia nem restaura arquivos; não equivale a proteção anti-ransomware.
- Consultas e uploads para serviços externos de reputação não fazem parte do aplicativo.
- GuihGuih AI: tela funcional de triagem local da última verificação, com explicações de regras acionadas, indicação de erros e sugestões cautelosas de revisão. Essa triagem é determinística, não é IA generativa nem modelo de aprendizado de máquina; não produz pontuação ou veredito de segurança e não envia dados.
- Modelo de classificação local: ainda indisponível. Nenhum modelo foi treinado/validado e nenhuma classificação por IA é feita; a página informa esse estado explicitamente.
- YARA/ClamAV, eventos de rede, detecção abrangente de ransomware, backups versionados e proteção pré-execução ainda não implementados.
- Quarentena cria uma cópia e mantém o original; criptografia em repouso não está implementada.
- Microsoft Defender e demais proteções nativas não são alterados.
- A CI executa os testes automatizados em Windows, Linux e macOS. Consulte a página da versão para os pacotes disponíveis.

## Builds instaláveis e releases

Baixe o pacote para seu sistema em [Releases](https://github.com/GuihInc/GuihGuih-Cyber/releases). Os arquivos `SHA256SUMS-*.txt` permitem conferir a integridade dos downloads.

O workflow `Build installers` gera prévias de instalação no pull request. Após mesclar as mudanças em `main`, crie uma tag que corresponda à versão em `pyproject.toml`. A publicação depende dos testes e da geração dos pacotes de todas as plataformas.

Atualize a versão em `pyproject.toml` e crie uma tag Git com o mesmo número (por exemplo, `v0.2.0`). Ao receber a tag, o GitHub Actions testa e compila os pacotes para as plataformas suportadas; a release é publicada apenas se os builds concluírem.

| Plataforma | Arquivos | Como instalar |
|---|---|---|
| Windows x64 | `GuihGuihCyber-Setup.exe` e `GuihGuihCyber.exe` | Abra o instalador ou execute a versão portátil. |
| Linux x86-64 | `.deb`, `.rpm` e `.AppImage` | Instale com `sudo apt install ./arquivo.deb` ou `sudo dnf install ./arquivo.rpm`. Para AppImage, torne o arquivo executável com `chmod +x arquivo.AppImage` e abra-o. Os builds usam Ubuntu 24.04. |
| macOS 14 ou mais recente | `.dmg`, `.pkg` e `.app.zip` para Apple Silicon (`arm64`) e Intel (`x86_64`) | Abra o DMG e arraste o app para Aplicativos ou abra o PKG. |

Os pacotes são distribuídos sem assinatura de editor. O SmartScreen pode alertar no Windows e o Gatekeeper pode bloquear a abertura no macOS. A assinatura Authenticode e a assinatura com Developer ID seguida de notarização dependem de credenciais do mantenedor.
