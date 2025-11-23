import time
from gerenciador import AnalisadorBase
from models.analysis import AnalysisResult


class AnalisadorExemplo(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Analisador de Exemplo"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:

        #No momento de processar vc pode escolher se usa o caminho da imagem para acessar ela ou se pega diretamente o conteudo em bytes

        time.sleep(1)

        """
        Você pode devolver métricas dentro do AnalysisResult para formar um gráfico de histograma. 
        Bins é a intensidade (eixo x) e counts é a quantidade de pixels com essa intensidade (eixo y).
        """
        
        return AnalysisResult(detalhe="Análise base concluída com sucesso.", metrics={"bins": [22, 45, 78], "counts": [100, 150, 200]})
    

class AnalisadorExemplo2(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Analisador de Exemplo 2"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:

        #No momento de processar vc pode escolher se usa o caminho da imagem para acessar ela ou se pega diretamente o conteudo em bytes

        time.sleep(1)

        """
        Você pode devolver métricas dentro do AnalysisResult para formar um gráfico de histograma. 
        Bins é a intensidade (eixo x) e counts é a quantidade de pixels com essa intensidade (eixo y).
        """
        
        return AnalysisResult(detalhe="Análise base 2 concluída com sucesso.", metrics={"bins": [2, 4, 7], "counts": [100, 150, 200]})