import cv2
import numpy as np
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

# ==========================================
# 1. ANALISADOR DE INTENSIDADE (CINZA)
# ==========================================
class AnalisadorHistogramaGray(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Histograma 1: Intensidade (Cinza/Luma)"

    @property
    def ordem(self) -> int:
        return 60

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: return AnalysisResult(detalhe="Erro imagem", metrics={})
        
        # Converte BGR para Cinza (Fórmula correta de luminosidade: 0.299R + 0.587G + 0.114B)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        counts = [int(x) for x in hist.flatten()] # Converte para Inteiros

        return AnalysisResult(
            detalhe="Intensidade (Claridade) calculada.",
            metrics={"bins": list(range(256)), "counts": counts}
        )

# ==========================================
# 2. ANALISADOR CANAL VERMELHO (R)
# ==========================================
class AnalisadorHistogramaRed(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Histograma 2: Canal Vermelho (R)"

    @property
    def ordem(self) -> int:
        return 61

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: return AnalysisResult(detalhe="Erro imagem", metrics={})

        # Separa os canais explicitamente para não haver erro de índice
        # OpenCV carrega como BGR (Blue, Green, Red)
        b, g, r = cv2.split(img)
        
        # DEBUG: Calcula média para conferência no terminal
        media_r = np.mean(r)
        print(f"[DEBUG VERMELHO] Média de cor R: {media_r:.2f} (0=Sem vermelho, 255=Muito vermelho)")

        # Calcula histograma SOMENTE do canal R
        hist = cv2.calcHist([r], [0], None, [256], [0, 256])
        counts = [int(x) for x in hist.flatten()]

        return AnalysisResult(
            detalhe=f"Nível médio de Vermelho: {int(media_r)}/255",
            metrics={"bins": list(range(256)), "counts": counts}
        )

# ==========================================
# 3. ANALISADOR CANAL VERDE (G)
# ==========================================
class AnalisadorHistogramaGreen(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Histograma 3: Canal Verde (G)"

    @property
    def ordem(self) -> int:
        return 62

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: return AnalysisResult(detalhe="Erro imagem", metrics={})

        b, g, r = cv2.split(img)
        
        media_g = np.mean(g)
        print(f"[DEBUG VERDE] Média de cor G: {media_g:.2f}")

        hist = cv2.calcHist([g], [0], None, [256], [0, 256])
        counts = [int(x) for x in hist.flatten()]

        return AnalysisResult(
            detalhe=f"Nível médio de Verde: {int(media_g)}/255",
            metrics={"bins": list(range(256)), "counts": counts}
        )

# ==========================================
# 4. ANALISADOR CANAL AZUL (B)
# ==========================================
class AnalisadorHistogramaBlue(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "Histograma 4: Canal Azul (B)"

    @property
    def ordem(self) -> int:
        return 63

    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        img = carregar_imagem_segura(caminho_imagem, conteudo)
        if img is None: return AnalysisResult(detalhe="Erro imagem", metrics={})

        b, g, r = cv2.split(img)
        
        media_b = np.mean(b)
        print(f"[DEBUG AZUL] Média de cor B: {media_b:.2f}")

        hist = cv2.calcHist([b], [0], None, [256], [0, 256])
        counts = [int(x) for x in hist.flatten()]

        return AnalysisResult(
            detalhe=f"Nível médio de Azul: {int(media_b)}/255",
            metrics={"bins": list(range(256)), "counts": counts}
        )