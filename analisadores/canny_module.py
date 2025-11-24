import cv2
import numpy as np
import base64
from gerenciador import AnalisadorBase
from models.analysis import AnalysisResult

def carregar_imagem_segura(caminho, conteudo):
    """
    Carrega a imagem garantindo formato BGR (Padrão OpenCV).
    """
    img = None
    if conteudo:
        # Lê direto da memória (mais rápido para uploads)
        nparr = np.frombuffer(conteudo, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        # Lê do disco
        img = cv2.imread(caminho, cv2.IMREAD_COLOR)
    return img

def img_para_base64(imagem):
    """Converte imagem numpy para string base64."""
    _, buffer = cv2.imencode('.png', imagem)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# ==========================================
# 1. DETECÇÃO DE BORDAS CANNY PADRÃO
# ==========================================
class AnalisadorCannyPadrao(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Canny 1: Detecção Padrão (50-150)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        # Converte para escala de cinza
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplica detector de bordas Canny com thresholds padrão
        bordas = cv2.Canny(img_gray, 50, 150)
        
        # Calcula métricas
        pixels_borda = np.sum(bordas == 255)
        percentual_bordas = (pixels_borda / bordas.size) * 100
        total_pixels = bordas.size
        
        print(f"[Canny Padrão] {percentual_bordas:.2f}% pixels detectados como borda")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "bordas_canny": img_para_base64(bordas)
        }
        
        return AnalysisResult(
            detalhe=f"Bordas detectadas: {percentual_bordas:.2f}% da imagem",
            metrics={
                "threshold_min": 50, 
                "threshold_max": 150, 
                "pixels_borda": int(pixels_borda),
                "percentual": round(percentual_bordas, 2),
                "total_pixels": int(total_pixels)
            },
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 2. DETECÇÃO DE BORDAS CANNY SENSÍVEL
# ==========================================
class AnalisadorCannySensivel(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Canny 2: Alta Sensibilidade (30-100)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholds mais baixos = detecta mais bordas (mais sensível)
        bordas = cv2.Canny(img_gray, 30, 100)
        
        pixels_borda = np.sum(bordas == 255)
        percentual_bordas = (pixels_borda / bordas.size) * 100
        
        print(f"[Canny Sensível] {percentual_bordas:.2f}% pixels detectados como borda")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "bordas_sensiveis": img_para_base64(bordas)
        }
        
        return AnalysisResult(
            detalhe=f"Detecção sensível. Bordas: {percentual_bordas:.2f}%",
            metrics={
                "threshold_min": 30, 
                "threshold_max": 100, 
                "pixels_borda": int(pixels_borda),
                "percentual": round(percentual_bordas, 2)
            },
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 3. DETECÇÃO DE BORDAS CANNY RIGOROSO
# ==========================================
class AnalisadorCannyRigoroso(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Canny 3: Baixa Sensibilidade (100-200)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholds mais altos = detecta menos bordas (mais rigoroso)
        bordas = cv2.Canny(img_gray, 100, 200)
        
        pixels_borda = np.sum(bordas == 255)
        percentual_bordas = (pixels_borda / bordas.size) * 100
        
        print(f"[Canny Rigoroso] {percentual_bordas:.2f}% pixels detectados como borda")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "bordas_rigorosas": img_para_base64(bordas)
        }
        
        return AnalysisResult(
            detalhe=f"Detecção rigorosa. Bordas: {percentual_bordas:.2f}%",
            metrics={
                "threshold_min": 100, 
                "threshold_max": 200, 
                "pixels_borda": int(pixels_borda),
                "percentual": round(percentual_bordas, 2)
            },
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 4. DETECÇÃO DE BORDAS COM PRÉ-PROCESSAMENTO
# ==========================================
class AnalisadorCannyComBlur(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Canny 4: Com Blur Gaussiano (Reduz Ruído)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplica Gaussian Blur para reduzir ruído antes do Canny
        img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1.4)
        
        # Aplica Canny na imagem suavizada
        bordas = cv2.Canny(img_blur, 50, 150)
        
        pixels_borda = np.sum(bordas == 255)
        percentual_bordas = (pixels_borda / bordas.size) * 100
        
        print(f"[Canny + Blur] {percentual_bordas:.2f}% pixels detectados como borda")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "com_blur": img_para_base64(img_blur),
            "bordas_suavizadas": img_para_base64(bordas)
        }
        
        return AnalysisResult(
            detalhe=f"Blur aplicado para reduzir ruído. Bordas: {percentual_bordas:.2f}%",
            metrics={
                "threshold_min": 50, 
                "threshold_max": 150,
                "blur_kernel": 5,
                "pixels_borda": int(pixels_borda),
                "percentual": round(percentual_bordas, 2)
            },
            extra={"imagens_processadas": imagens}
        )