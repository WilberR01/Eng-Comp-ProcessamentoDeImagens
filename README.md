# Eng-Comp - Processamento de Imagens (interface + motor)

Este repositório contém um scaffold mínimo para executar módulos de análise de imagens:
- `gerenciador.py` — motor que descobre analisadores (subclasses de `AnalisadorBase`) e executa um pipeline;
- `models/` — classes modelo (`AnalysisResult`, `ResultItem`, `ConsolidatedReport`) para resultados tipados e serializáveis;
- `services/runner.py` — runner que integra o motor com a UI;
- `ui/` — aplicação web Flask para envio de imagens e visualização de relatórios (upload + gráficos);
- `analyzers/` — (pasta) local para adicionar analisadores (cada um deve herdar `AnalisadorBase`).

Este README explica como executar o projeto em outra máquina (Windows, PowerShell).

---

## Requisitos
- Python 3.8+ instalado (recomenda-se 3.10/3.11+).
- Windows PowerShell (instruções abaixo usam PowerShell).

## Passos rápidos (Windows PowerShell)

1) Clone o repositório e entre na pasta do projeto:

```powershell
git clone <repo_url>
cd Eng-Comp-ProcessamentoDeImagens
```

2) Crie e ative um ambiente virtual (recomendo `venv`):

```powershell
python -m venv .venv
# Ativar (PowerShell)
.\.venv\Scripts\Activate.ps1
```

Se a ativação falhar por política de execução, permita scripts para o seu usuário, se não der certo tem um monte de lugar na internet que explica melhor sobre isso:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1
```

3) Instale dependências:

```powershell
pip install -r requirements.txt
# (opcional) instalar pytest para rodar testes
pip install pytest
```

4) Rodar a aplicação web (Flask):

```powershell
python .\main.py
# ou definir outra porta
# $env:PORT = 8000; python .\main.py
```

Abra http://127.0.0.1:5000 no navegador. Use o formulário para enviar uma imagem; a interface exibirá o relatório consolidado dos módulos descobertos automaticamente.

## Testes

Rodar a suíte de testes (pytest):

```powershell
pytest -q
```

## Arquitetura e contrato dos analisadores
- Para criar um novo analisador, adicione um módulo em `analyzers/` e defina uma classe que herde `AnalisadorBase` e implemente `processar`.
- Assinatura recomendada do método `processar`:

```py
from gerenciador import AnalisadorBase
from models.analysis import AnalysisResult

class MeuAnalisador(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Meu Analisador"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        # conteudo: bytes do arquivo (quando disponível, p.ex. upload)
        # Retorne um AnalysisResult com detalhe, metrics e extra (serializáveis)
        return AnalysisResult(detalhe="OK", metrics={"foo": 1})
```

- O motor detecta automaticamente subclasses carregadas. Para garantir que seus analisadores sejam carregados, importe o módulo em `analyzers/__init__.py` ou use um pacote instalável.
- O motor aceita que `processar` devolva um `dict` por compatibilidade legacy — ele converte `dict` em `AnalysisResult` internamente. Mas o ideal é retornar `AnalysisResult`.

## Formato dos resultados
- `AnalysisResult` contém campos: `detalhe` (string), `metrics` (dict) e `extra` (dict). Todos são serializados para JSON pela UI.
- A UI procura por `metrics.bins` e `metrics.counts` para desenhar automaticamente um histograma (Chart.js). Mas você pode devolver qualquer métrica que precisar.

## Notas operacionais
- Uploads: os arquivos enviados pela UI são salvos temporariamente em `ui/uploads/` e removidos após processamento.
- Logs: por agora as exceções são formatadas e mostradas no relatório; adicionar logging em arquivo é uma melhoria recomendada.
- Segurança: limite o tamanho máximo do upload e valide tipos de arquivo antes de processar em produção.

## Ajuda / Troubleshooting
- Se `python` não for reconhecido: instale Python e marque a opção "Add Python to PATH" no instalador do Windows.
- Se `py` não existir, não é um problema — usamos `python` nos comandos acima.
- Erro ao importar módulos nos testes: certifique-se de ativar o venv e que o diretório do projeto está sendo usado (o `tests/conftest.py` já coloca o root no sys.path).

## Próximos passos sugeridos (opcionais)
- Adicionar logging (arquivo) e um endpoint para baixar relatórios completos.
- Implementar upload persistente e histórico de execuções.
- Criar CI (GitHub Actions) que roda pytest em cada PR.

Se quiser, eu gero um `requirements-dev.txt` com pytest e ferramentas de lint, ou crio o fluxo de CI agora.

---

Se houver algo específico que você queira documentado no README (ex.: exemplos de analisadores, contrato JSON preciso, comandos para Windows CMD em vez de PowerShell), eu adapto o arquivo.
