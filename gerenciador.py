import os
import time
import inspect
from abc import ABC, abstractmethod
from typing import Any

from models.report import ResultItem, ConsolidatedReport
from models.analysis import AnalysisResult


class AnalisadorBase(ABC):
    @property
    @abstractmethod
    def nome_modulo(self) -> str:
        pass

    @property
    def ordem(self) -> int:
        """Ordem de execução dos analisadores (menor = executado primeiro). Padrão: 999."""
        return 999

    @abstractmethod
    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        pass


class MotorDeAnalise:
    def __init__(self):
        self.analisadores = []
        self._descobrir_analisadores()

    def _descobrir_analisadores(self):
        # Tentativa robusta: importe dinamicamente todos os módulos em 'analisadores'
        # para garantir que as subclasses de AnalisadorBase sejam registradas.
        try:
            import importlib
            import sys
            from pathlib import Path

            project_root = Path(__file__).resolve().parent
            analisadores_dir = project_root / "analisadores"
            if analisadores_dir.exists() and analisadores_dir.is_dir():
                for p in analisadores_dir.iterdir():
                    if p.suffix == ".py" and not p.name.startswith("_"):
                        mod_name = p.stem
                        full_mod = f"analisadores.{mod_name}"
                        try:
                            if full_mod in sys.modules:
                                importlib.reload(sys.modules[full_mod])
                            else:
                                importlib.import_module(full_mod)
                            print(f"    [import] {full_mod}")
                        except Exception as ie:
                            print(f"    [!] Falha ao importar {full_mod}: {ie}")
        except Exception:
            # Não crítico: prosseguimos mesmo se a importação falhar
            pass

        subclasses = AnalisadorBase.__subclasses__()
        print(f"[*] Sistema inicializado. {len(subclasses)} módulos de análise encontrados.")

        for cls in subclasses:
            try:
                instancia = cls()
                self.analisadores.append(instancia)
                print(f"    -> Módulo carregado: {instancia.nome_modulo} (ordem: {instancia.ordem})")
            except Exception as e:
                print(f"    [!] Erro ao instanciar o módulo {cls.__name__}: {e}")

        # Ordenar analisadores pela propriedade 'ordem'
        self.analisadores.sort(key=lambda a: a.ordem)

    def executar_pipeline(self, caminho_imagem: str) -> dict:
        print(f"\n{'='*60}")
        print(f"INICIANDO ANÁLISE DO ARQUIVO: {caminho_imagem}")
        print(f"{'='*60}")

        if not caminho_imagem or not isinstance(caminho_imagem, str):
            print("[ERRO FATAL] Caminho de arquivo inválido.")
            return {}

        if not os.path.exists(caminho_imagem):
            print(f"[AVISO] O arquivo '{caminho_imagem}' não foi encontrado no disco.")
            print("        (Prosseguindo com simulação para fins de teste...)")

        relatorio_final = ConsolidatedReport()

        for analisador in self.analisadores:
            print(f"\n>>> Executando: {analisador.nome_modulo}...")
            start_time = time.time()

            conteudo = None
            try:
                if os.path.exists(caminho_imagem):
                    with open(caminho_imagem, 'rb') as f:
                        conteudo = f.read()
            except Exception:
                conteudo = None

            try:
                sig = inspect.signature(analisador.processar)
                params = [p for p in sig.parameters.values() if p.name != 'self']
                if len(params) >= 2:
                    resultado = analisador.processar(caminho_imagem, conteudo)
                else:
                    resultado = analisador.processar(caminho_imagem)

                tempo = time.time() - start_time
                print(f"    [SUCESSO] Concluído em {tempo:.2f}s")
                if isinstance(resultado, dict):
                    ar = AnalysisResult(detalhe=resultado.get("detalhe"), extra={k: v for k, v in resultado.items() if k != "detalhe"})
                elif isinstance(resultado, AnalysisResult):
                    ar = resultado
                else:
                    ar = AnalysisResult(extra={"value": resultado})

                item = ResultItem(module=analisador.nome_modulo, status="OK", dados=ar, time_taken=tempo)
                relatorio_final.add(item)

            except Exception as e:
                tempo = time.time() - start_time
                print(f"    [FALHA] Ocorreu um erro: {str(e)}")
                item = ResultItem(module=analisador.nome_modulo, status="ERRO", msg=str(e), time_taken=tempo)
                relatorio_final.add(item)

        self._gerar_relatorio_consolidado(relatorio_final)

        return relatorio_final.to_dict() # Precisa fazer assim pra UI entender

    def _gerar_relatorio_consolidado(self, dados: ConsolidatedReport):
        print(f"\n{'-'*60}")
        print("RESUMO DA EXECUÇÃO")
        print(f"{'-'*60}")
        for modulo, info in dados:
                status = info.status
                if status == 'OK':
                    detalhe = None
                    if isinstance(info.dados, AnalysisResult):
                        detalhe = info.dados.detalhe
                    print(f"[{status}] {modulo} -> Tempo: {info.time_taken:.2f}s" + (f" | Detalhe: {detalhe}" if detalhe else ""))
                else:
                    print(f"[{status}] {modulo} -> Erro: {info.msg} (tempo: {info.time_taken:.2f}s)")

