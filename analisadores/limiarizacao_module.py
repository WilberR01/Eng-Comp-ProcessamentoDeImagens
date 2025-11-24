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
# 1. LIMIARIZAÇÃO GLOBAL SIMPLES
# ==========================================
class AnalisadorLimiarizacaoSimples(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Limiarização 1: Global Simples (T=127)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        # Converte para escala de cinza
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplica limiarização simples com threshold 127
        _, img_binaria = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
        
        # Calcula métricas
        pixels_brancos = np.sum(img_binaria == 255)
        pixels_pretos = np.sum(img_binaria == 0)
        percentual_brancos = (pixels_brancos / img_binaria.size) * 100
        
        print(f"[Limiarização Simples] {percentual_brancos:.1f}% pixels brancos")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "limiarizada": img_para_base64(img_binaria)
        }
        
        return AnalysisResult(
            detalhe=f"Limiar fixo em 127. Pixels brancos: {percentual_brancos:.1f}%",
            metrics={"limiar": 127, "pixels_brancos": int(pixels_brancos), "percentual": round(percentual_brancos, 2)},
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 2. MÉTODO DE OTSU (AUTOMÁTICO)
# ==========================================
class AnalisadorLimiarizacaoOtsu(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Limiarização 2: Método de Otsu (Automático)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Otsu calcula o melhor limiar automaticamente
        limiar_otsu, img_binaria = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        pixels_brancos = np.sum(img_binaria == 255)
        percentual_brancos = (pixels_brancos / img_binaria.size) * 100
        
        print(f"[Otsu] Limiar calculado: {limiar_otsu:.0f}, {percentual_brancos:.1f}% pixels brancos")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "otsu": img_para_base64(img_binaria)
        }
        
        return AnalysisResult(
            detalhe=f"Limiar calculado automaticamente: {int(limiar_otsu)}. Pixels brancos: {percentual_brancos:.1f}%",
            metrics={"limiar": int(limiar_otsu), "pixels_brancos": int(pixels_brancos), "percentual": round(percentual_brancos, 2)},
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 3. LIMIARIZAÇÃO ADAPTATIVA - MÉDIA
# ==========================================
class AnalisadorLimiarizacaoAdaptativaMedia(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Limiarização 3: Adaptativa (Média Local)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Limiarização adaptativa usa média local de cada região
        img_binaria = cv2.adaptiveThreshold(
            img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        pixels_brancos = np.sum(img_binaria == 255)
        percentual_brancos = (pixels_brancos / img_binaria.size) * 100
        
        print(f"[Adaptativa Média] {percentual_brancos:.1f}% pixels brancos")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "adaptativa_media": img_para_base64(img_binaria)
        }
        
        return AnalysisResult(
            detalhe=f"Limiar adaptativo por média local. Pixels brancos: {percentual_brancos:.1f}%",
            metrics={"tamanho_bloco": 11, "pixels_brancos": int(pixels_brancos), "percentual": round(percentual_brancos, 2)},
            extra={"imagens_processadas": imagens}
        )

# ==========================================
# 4. LIMIARIZAÇÃO ADAPTATIVA - GAUSSIANA
# ==========================================
class AnalisadorLimiarizacaoAdaptativaGaussiana(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Limiarização 4: Adaptativa (Gaussiana)"

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: 
            return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Limiarização adaptativa usa média gaussiana ponderada
        img_binaria = cv2.adaptiveThreshold(
            img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        pixels_brancos = np.sum(img_binaria == 255)
        percentual_brancos = (pixels_brancos / img_binaria.size) * 100
        
        print(f"[Adaptativa Gaussiana] {percentual_brancos:.1f}% pixels brancos")
        
        # Gera imagens em base64
        imagens = {
            "original": img_para_base64(img_gray),
            "adaptativa_gaussiana": img_para_base64(img_binaria)
        }
        
        return AnalysisResult(
            detalhe=f"Limiar adaptativo gaussiano. Pixels brancos: {percentual_brancos:.1f}%",
            metrics={"tamanho_bloco": 11, "pixels_brancos": int(pixels_brancos), "percentual": round(percentual_brancos, 2)},
            extra={"imagens_processadas": imagens}
        )