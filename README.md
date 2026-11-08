# GuihGuih Cyber

Aplicativo desktop local para Windows, Linux e macOS. Inclui scanner em Python com SHA-256 e regras explicáveis, histórico SQLite, monitoramento de pastas adicionado pelo usuário, cópia de quarentena reversível e interface PySide6. Tkinter permanece como alternativa mínima.

## Executar no Windows

Requer Python 3.12+. No PowerShell:

```powershell
cd 'D:\#codex\Aplicativos\GuihGuih Cyber'
python -m venv .venv
python -m pip install -e ".[dev]"
python -m guihguih_cyber.desktop
```

Se a instalação do PySide6 falhar ou quiser abrir a interface mínima sem Qt:

```powershell
cd 'D:\#codex\Aplicativos\GuihGuih Cyber'
.\.venv\Scripts\python.exe -m guihguih_cyber.app
```

A interface principal oferece verificação rápida (pasta escolhida), completa (pasta pessoal) e personalizada (arquivo). O scanner lê arquivos em blocos, calcula SHA-256, aplica regras locais explicáveis e grava sessões em SQLite no diretório de dados do usuário.

## Testes

```powershell
python -m pytest
```

Os testes usam fixtures sintéticas. O marcador EICAR utilizado é texto inofensivo, não malware executável.

## Recursos e limites

- Funcionais: scanner manual, hash SHA-256, regras heurísticas explicáveis, cancelamento, histórico SQLite, monitoramento por polling em pastas escolhidas pelo usuário e quarentena por cópia com hash e restauração confirmada sem sobrescrita.
- Consultas e uploads para serviços externos de reputação não fazem parte do aplicativo.
- GuihGuih AI: extração estática experimental, sem modelo treinado ou classificação.
- YARA/ClamAV, eventos de rede, defesa ransomware, backups versionados e proteção pré-execução ainda não implementados.
- Quarentena cria uma cópia e mantém o original; criptografia em repouso não está implementada.
- Microsoft Defender e demais proteções nativas não são alterados.
- O workflow `.github/workflows/build.yml` executa testes e gera artefatos PyInstaller em runners de Windows, Linux e macOS. Esses builds ainda não foram executados nesta máquina.
- Instaladores `.msi`/Setup, `.AppImage`, `.deb`, `.rpm`, `.dmg` e `.pkg` não foram produzidos. Assinatura/notarização exigem credenciais específicas.
- Testado localmente apenas no Windows. Linux e macOS aguardam execução nos runners.

## Builds instaláveis e releases

Após mesclar as mudanças em `main`, crie uma tag de versão para iniciar a matriz de testes e builds nativos. A release só é publicada se os testes e os três jobs de empacotamento terminarem com sucesso:

```bash
git checkout main
git pull
git tag v0.1.0
git push origin v0.1.0
```

O workflow `.github/workflows/release.yml` publica `GuihGuihCyber.exe` e `GuihGuihCyber-Setup.exe` no Windows; `.AppImage`, `.deb` e `.rpm` no Linux; e `.dmg`, `.pkg` e `.app.zip` no macOS. Cada plataforma inclui arquivo SHA-256. São builds x64 no Windows/Linux e da arquitetura do runner `macos-latest` no macOS. Os jobs precisam passar; falhas não publicam uma release parcial.

Os artefatos atuais são **não assinados**. Windows SmartScreen pode alertar; macOS pode bloquear a primeira abertura. A distribuição assinada exige certificado de assinatura Authenticode no Windows e Developer ID, perfil/certificado de instalador, credenciais App Store Connect e notarização para macOS. Esses segredos ainda não estão configurados no repositório, então assinatura e notarização não são realizadas pelo workflow. O pacote `.pkg` e o `.dmg` ainda precisam ser validados em máquinas limpas de cada SO antes de uso amplo.

