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


class AnalisadorDeteccaoFormas(AnalisadorBase):
    """
    Implementa detecção de formas utilizando busca de contornos (findContours)
    e classificação baseada em contagem de vértices.
    
    Classifica formas como:
    - Triângulos: 3 vértices
    - Quadrados/Retângulos: 4 vértices
    - Círculos: > 4 vértices (aproximação circular)
    
    Retorna métricas com lista de formas detectadas e imagens com contornos desenhados.
    """

    @property
    def nome_modulo(self) -> str:
        return "Detector de Formas"

    @property
    def ordem(self) -> int:
        return 30  # Executar após equalização, como parte da análise

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        """
        Processa detecção de formas na imagem.
        
        Args:
            caminho_imagem: Caminho para o arquivo de imagem
            conteudo: Bytes da imagem (quando disponível, ex: upload)
        
        Returns:
            AnalysisResult com métricas de formas detectadas
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
            
            # Aplicar limiarização (thresholding)
            _, binaria = cv2.threshold(cinza, 127, 255, cv2.THRESH_BINARY)
            
            # Detecção de bordas (Canny)
            bordas = cv2.Canny(binaria, 50, 150)
            
            # Busca de contornos
            contornos, _ = cv2.findContours(bordas, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Classificar formas
            formas_detectadas = []
            triangulos = 0
            quadrados = 0
            circulos = 0
            
            for contorno in contornos:
                # Aproximar o contorno a um polígono
                perimetro = cv2.arcLength(contorno, True)
                aproximacao = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
                vertices = len(aproximacao)
                
                # Ignorar contornos muito pequenos
                area = cv2.contourArea(contorno)
                if area < 100:
                    continue
                
                # Classificar pela contagem de vértices
                if vertices == 3:
                    tipo = "Triângulo"
                    triangulos += 1
                elif vertices == 4:
                    tipo = "Quadrado/Retângulo"
                    quadrados += 1
                elif vertices > 4:
                    tipo = "Círculo/Oval"
                    circulos += 1
                else:
                    tipo = "Outra forma"
                
                # Calcular centro e perímetro
                M = cv2.moments(contorno)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    cx, cy = 0, 0
                
                formas_detectadas.append({
                    "tipo": tipo,
                    "vertices": int(vertices),
                    "area": float(area),
                    "perimetro": float(perimetro),
                    "centro": {"x": int(cx), "y": int(cy)}
                })
            
            # Ordenar por área (maior primeiro)
            formas_detectadas.sort(key=lambda x: x["area"], reverse=True)
            
            total_formas = len(formas_detectadas)
            detalhe = (
                f"Detecção concluída. {total_formas} forma(s) detectada(s): "
                f"{triangulos} triângulo(s), {quadrados} quadrado(s)/retângulo(s), "
                f"{circulos} círculo(s)/oval(is)."
            )
            
            # Criar imagens para visualização
            # 1. Imagem com todos os contornos
            img_contornos = imagem.copy()
            cv2.drawContours(img_contornos, contornos, -1, (0, 255, 0), 2)
            
            # 2. Imagem com formas classificadas (desenhadas com cores diferentes)
            img_formas_coloridas = imagem.copy()
            cores = {
                "Triângulo": (255, 0, 0),           # Azul
                "Quadrado/Retângulo": (0, 255, 0), # Verde
                "Círculo/Oval": (0, 0, 255),       # Vermelho
                "Outra forma": (255, 255, 0)       # Ciano
            }
            
            for contorno in contornos:
                perimetro = cv2.arcLength(contorno, True)
                aproximacao = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
                vertices = len(aproximacao)
                area = cv2.contourArea(contorno)
                
                if area < 100:
                    continue
                
                # Determinar tipo e cor
                if vertices == 3:
                    tipo = "Triângulo"
                elif vertices == 4:
                    tipo = "Quadrado/Retângulo"
                elif vertices > 4:
                    tipo = "Círculo/Oval"
                else:
                    tipo = "Outra forma"
                
                cor = cores.get(tipo, (255, 255, 0))
                cv2.drawContours(img_formas_coloridas, [contorno], 0, cor, 2)
                
                # Desenhar centróide
                M = cv2.moments(contorno)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(img_formas_coloridas, (cx, cy), 5, cor, -1)
            
            # Gerar imagens em base64
            imagens = {
                "original": img_para_base64(imagem),
                "bordas": img_para_base64(bordas),
                "contornos": img_para_base64(img_contornos),
                "formas_coloridas": img_para_base64(img_formas_coloridas)
            }
            
            metrics = {
                "total_formas": int(total_formas),
                "triangulos": int(triangulos),
                "quadrados": int(quadrados),
                "circulos": int(circulos),
                "formas": formas_detectadas,
                "metodo": "Contour Detection (findContours + Canny + Thresholding)"
            }
            
            return AnalysisResult(detalhe=detalhe, metrics=metrics, extra={"imagens_processadas": imagens})
        
        except Exception as e:
            return AnalysisResult(
                detalhe=f"Erro ao processar detecção de formas: {str(e)}",
                metrics={"status": "erro", "mensagem_erro": str(e)}
            )
