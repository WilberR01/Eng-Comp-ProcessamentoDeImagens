import cv2
import numpy as np
import base64
from gerenciador import AnalisadorBase
from models.analysis import AnalysisResult


def img_para_base64(imagem):
    """Converte imagem numpy para string base64."""
    _, buffer = cv2.imencode('.png', imagem)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


class AnalisadorEqualizacaoHistograma(AnalisadorBase):
    """
    Implementa técnicas de Equalização de Histograma para otimização de contraste.
    
    Realiza:
    1. Conversão para escala de cinza
    2. Equalização padrão com cv2.equalizeHist
    3. Equalização adaptativa limitada por contraste (CLAHE)
    
    Retorna métricas com detalhes da equalização e melhoria de contraste + imagens visuais.
    """

    @property
    def nome_modulo(self) -> str:
        return "Equalizador de Histograma"

    @property
    def ordem(self) -> int:
        return 20  # Executar após pré-processamento, antes de análises complexas

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        """
        Processa equalização de histograma na imagem.
        
        Args:
            caminho_imagem: Caminho para o arquivo de imagem
            conteudo: Bytes da imagem (quando disponível, ex: upload)
        
        Returns:
            AnalysisResult com métricas de contraste e detalhes da equalização
        """
        try:
            # Carregar imagem
            if conteudo is not None:
                # Carregar de bytes
                nparr = np.frombuffer(conteudo, np.uint8)
                imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                # Carregar do arquivo
                imagem = cv2.imread(caminho_imagem, cv2.IMREAD_COLOR)
            
            if imagem is None:
                return AnalysisResult(
                    detalhe="Erro: Não foi possível carregar a imagem.",
                    metrics={"status": "erro"}
                )
            
            # Converter para escala de cinza
            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            
            # Calcular contraste da imagem original (desvio padrão do histograma)
            contraste_original = float(np.std(cinza))
            
            # Equalização padrão
            equalizado = cv2.equalizeHist(cinza)
            contraste_equalizado = float(np.std(equalizado))
            
            # Equalização adaptativa (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equalizado_clahe = clahe.apply(cinza)
            contraste_clahe = float(np.std(equalizado_clahe))
            
            # Calcular melhoria percentual
            melhoria_padrao = ((contraste_equalizado - contraste_original) / (contraste_original + 1e-6)) * 100
            melhoria_clahe = ((contraste_clahe - contraste_original) / (contraste_original + 1e-6)) * 100
            
            # Gerar imagens em base64 para visualização
            imagens = {
                "original": img_para_base64(cinza),
                "equalizado_padrao": img_para_base64(equalizado),
                "equalizado_clahe": img_para_base64(equalizado_clahe)
            }
            
            detalhe = (
                f"Equalização concluída com sucesso. "
                f"Contraste original: {contraste_original:.2f}. "
                f"Contraste após equalização padrão: {contraste_equalizado:.2f} ({melhoria_padrao:+.1f}%). "
                f"Contraste após CLAHE: {contraste_clahe:.2f} ({melhoria_clahe:+.1f}%)."
            )
            
            metrics = {
                "contraste_original": float(contraste_original),
                "contraste_equalizado": float(contraste_equalizado),
                "contraste_clahe": float(contraste_clahe),
                "melhoria_padrao_pct": float(melhoria_padrao),
                "melhoria_clahe_pct": float(melhoria_clahe),
                "metodo": "Histogram Equalization (padrão + CLAHE)"
            }
            
            return AnalysisResult(detalhe=detalhe, metrics=metrics, extra={"imagens_processadas": imagens})
        
        except Exception as e:
            return AnalysisResult(
                detalhe=f"Erro ao processar equalização: {str(e)}",
                metrics={"status": "erro", "mensagem_erro": str(e)}
            )
