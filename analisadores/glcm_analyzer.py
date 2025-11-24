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
        nparr = np.frombuffer(conteudo, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(caminho, cv2.IMREAD_COLOR)
    return img

def calcular_glcm(imagem_cinza, distancia=1, angulo=0, niveis=64):
    """
    Calcula a matriz de co-ocorrência de níveis de cinza (GLCM)
    Versão corrigida com tratamento seguro de índices.
    """
    # Faz uma cópia para não modificar a original
    img_quantized = imagem_cinza.copy().astype(np.float32)
    
    # Quantiza a imagem para reduzir o número de níveis de cinza
    if niveis < 256:
        fator = 256 / niveis
        img_quantized = (img_quantized / fator).astype(np.uint8)
    else:
        img_quantized = imagem_cinza.astype(np.uint8)
    
    # Inicializa a matriz GLCM
    glcm = np.zeros((niveis, niveis), dtype=np.float64)
    
    # Calcula offsets baseados na distância e ângulo
    offset_x = int(round(distancia * np.cos(angulo)))
    offset_y = int(round(distancia * np.sin(angulo)))
    
    altura, largura = img_quantized.shape
    
    # Define limites seguros para evitar índices fora dos bounds
    start_i = max(0, -offset_y)
    end_i = min(altura, altura - offset_y)
    start_j = max(0, -offset_x)
    end_j = min(largura, largura - offset_x)
    
    # Preenche a matriz GLCM com verificação de limites
    for i in range(start_i, end_i):
        for j in range(start_j, end_j):
            pixel_atual = img_quantized[i, j]
            pixel_vizinho = img_quantized[i + offset_y, j + offset_x]
            
            # Garante que os pixels estão dentro dos níveis
            if 0 <= pixel_atual < niveis and 0 <= pixel_vizinho < niveis:
                glcm[pixel_atual, pixel_vizinho] += 1
    
    # Normaliza a matriz
    if glcm.sum() > 0:
        glcm = glcm / glcm.sum()
    
    return glcm

def extrair_caracteristicas_glcm(glcm):
    """
    Extrai características texturais da matriz GLCM
    """
    if glcm.sum() == 0:
        return {}
    
    glcm = glcm.astype(np.float64)
    metrics = {}
    
    # Cria matrizes de índices
    i, j = np.indices(glcm.shape)
    
    # 1. Contraste (Contrast)
    contrast = np.sum(glcm * ((i - j) ** 2))
    metrics['contraste'] = float(contrast)
    
    # 2. Dissimilaridade (Dissimilarity)
    dissimilarity = np.sum(glcm * np.abs(i - j))
    metrics['dissimilaridade'] = float(dissimilarity)
    
    # 3. Homogeneidade (Homogeneity)
    with np.errstate(divide='ignore', invalid='ignore'):
        homogeneity = np.sum(glcm / (1 + (i - j) ** 2))
    metrics['homogeneidade'] = float(homogeneity)
    
    # 4. Energia (Energy)
    energy = np.sum(glcm ** 2)
    metrics['energia'] = float(energy)
    
    # 5. Correlação (Correlation)
    mu_i = np.sum(i * glcm)
    mu_j = np.sum(j * glcm)
    sigma_i = np.sqrt(np.sum(glcm * (i - mu_i) ** 2))
    sigma_j = np.sqrt(np.sum(glcm * (j - mu_j) ** 2))
    
    if sigma_i > 1e-10 and sigma_j > 1e-10:
        correlation = np.sum(glcm * (i - mu_i) * (j - mu_j)) / (sigma_i * sigma_j)
        metrics['correlacao'] = float(correlation)
    else:
        metrics['correlacao'] = 0.0
    
    # 6. Entropia (Entropy)
    glcm_nonzero = glcm[glcm > 0]
    if len(glcm_nonzero) > 0:
        entropy = -np.sum(glcm_nonzero * np.log2(glcm_nonzero))
        metrics['entropia'] = float(entropy)
    else:
        metrics['entropia'] = 0.0
    
    return metrics

class AnalisadorGLCM(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "GLCM: Análise de Textura"

    @property
    def ordem(self) -> int:
        return 70
    
    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        try:
            img = carregar_imagem_segura(caminho_imagem, conteudo)
            if img is None:
                return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
            
            # Converte para tons de cinza
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Parâmetros para GLCM
            distancia = 1
            angulos = [0, np.pi/4, np.pi/2, 3*np.pi/4]  # 0°, 45°, 90°, 135°
            niveis = 64  # Reduz níveis para melhor performance
            
            # Calcula GLCM para diferentes ângulos
            caracteristicas_por_angulo = []
            glcm_info = {}
            
            for idx, angulo in enumerate(angulos):
                try:
                    glcm = calcular_glcm(img_gray, distancia, angulo, niveis)
                    caracteristicas = extrair_caracteristicas_glcm(glcm)
                    
                    if caracteristicas:
                        caracteristicas_por_angulo.append(caracteristicas)
                        
                        # Armazena informações do GLCM
                        angulo_graus = int(np.degrees(angulo))
                        glcm_info[f'angulo_{angulo_graus}'] = {
                            'glcm_nao_zero': int(np.count_nonzero(glcm)),
                            'soma_glcm': float(glcm.sum())
                        }
                        
                except Exception as e:
                    print(f"[DEBUG] Erro no ângulo {np.degrees(angulo):.0f}°: {e}")
                    continue
            
            if not caracteristicas_por_angulo:
                return AnalysisResult(
                    detalhe="Não foi possível calcular características GLCM", 
                    metrics={}
                )
            
            # Combina características (média entre ângulos)
            metrics = {}
            todas_chaves = set()
            for carac in caracteristicas_por_angulo:
                todas_chaves.update(carac.keys())
            
            for key in todas_chaves:
                valores = [carac.get(key, 0) for carac in caracteristicas_por_angulo]
                metrics[key] = float(np.mean(valores))
                metrics[f'{key}_std'] = float(np.std(valores))
            
            # Adiciona informações gerais
            metrics.update({
                'niveis_cinza': niveis,
                'distancia': distancia,
                'num_angulos_validos': len(caracteristicas_por_angulo),
                'altura_imagem': img_gray.shape[0],
                'largura_imagem': img_gray.shape[1]
            })
            
            # Debug no terminal
            print(f"[DEBUG GLCM] Imagem: {img_gray.shape}, Ângulos processados: {len(caracteristicas_por_angulo)}")
            for key, value in metrics.items():
                if not key.endswith('_std') and key in ['contraste', 'homogeneidade', 'energia', 'entropia']:
                    print(f"  {key}: {value:.4f}")
            
            detalhe = (f"GLCM com {niveis} níveis. "
                      f"Contraste: {metrics.get('contraste', 0):.2f}, "
                      f"Homogeneidade: {metrics.get('homogeneidade', 0):.3f}, "
                      f"Entropia: {metrics.get('entropia', 0):.3f}")
            
            return AnalysisResult(
                detalhe=detalhe,
                metrics=metrics,
                extra={
                    'angulos_analisados': [int(np.degrees(a)) for a in angulos],
                    'glcm_info': glcm_info
                }
            )
            
        except Exception as e:
            print(f"[ERRO GLCM] {e}")
            return AnalysisResult(
                detalhe=f"Erro na análise GLCM: {str(e)}",
                metrics={}
            )

class AnalisadorGLCMContraste(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "GLCM: Contraste e Homogeneidade"

    @property
    def ordem(self) -> int:
        return 71
    
    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        try:
            img = carregar_imagem_segura(caminho_imagem, conteudo)
            if img is None:
                return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
            
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Usa apenas ângulo 0° para simplificar
            glcm = calcular_glcm(img_gray, distancia=1, angulo=0, niveis=64)
            caracteristicas = extrair_caracteristicas_glcm(glcm)
            
            metrics = {
                'contraste': caracteristicas.get('contraste', 0),
                'homogeneidade': caracteristicas.get('homogeneidade', 0),
                'dissimilaridade': caracteristicas.get('dissimilaridade', 0)
            }
            
            detalhe = (f"Contraste: {metrics['contraste']:.2f} | "
                      f"Homogeneidade: {metrics['homogeneidade']:.3f} | "
                      f"Dissimilaridade: {metrics['dissimilaridade']:.3f}")
            
            print(f"[DEBUG CONTRASTE] Contraste: {metrics['contraste']:.2f}")
            print(f"[DEBUG HOMOGENEIDADE] Homogeneidade: {metrics['homogeneidade']:.3f}")
            
            return AnalysisResult(
                detalhe=detalhe,
                metrics=metrics
            )
            
        except Exception as e:
            print(f"[ERRO GLCM Contraste] {e}")
            return AnalysisResult(
                detalhe=f"Erro no GLCM Contraste: {str(e)}",
                metrics={}
            )

class AnalisadorGLCMEnergiaEntropia(AnalisadorBase):
    @property
    def nome_modulo(self) -> str:
        return "GLCM: Energia e Entropia"

    @property
    def ordem(self) -> int:
        return 72
    
    def processar(self, caminho_imagem: str, conteudo: bytes = None) -> AnalysisResult:
        try:
            img = carregar_imagem_segura(caminho_imagem, conteudo)
            if img is None:
                return AnalysisResult(detalhe="Erro ao carregar imagem", metrics={})
            
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            glcm = calcular_glcm(img_gray, distancia=1, angulo=0, niveis=64)
            caracteristicas = extrair_caracteristicas_glcm(glcm)
            
            metrics = {
                'energia': caracteristicas.get('energia', 0),
                'entropia': caracteristicas.get('entropia', 0),
                'correlacao': caracteristicas.get('correlacao', 0)
            }
            
            detalhe = (f"Energia: {metrics['energia']:.4f} | "
                      f"Entropia: {metrics['entropia']:.3f} | "
                      f"Correlação: {metrics['correlacao']:.3f}")
            
            print(f"[DEBUG ENERGIA] Energia: {metrics['energia']:.4f}")
            print(f"[DEBUG ENTROPIA] Entropia: {metrics['entropia']:.3f}")
            
            return AnalysisResult(
                detalhe=detalhe,
                metrics=metrics
            )
            
        except Exception as e:
            print(f"[ERRO GLCM Energia] {e}")
            return AnalysisResult(
                detalhe=f"Erro no GLCM Energia: {str(e)}",
                metrics={}
            )