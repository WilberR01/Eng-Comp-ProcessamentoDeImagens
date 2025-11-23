import cv2
import numpy as np
from matplotlib import pyplot as plt

def plotar_histograma_grayscale(caminho_imagem):
    # Carrega a imagem em escala de cinza (0 indica grayscale)
    img = cv2.imread(caminho_imagem, 0)
    
    if img is None:
        print("Erro: Imagem não encontrada.")
        return

    # Calcula o histograma
    # calcHist(imagens, canais, máscara, bins, range)
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])

    # Plotagem
    plt.figure()
    plt.title("Histograma Grayscale")
    plt.xlabel("Intensidade do Pixel (0-255)")
    plt.ylabel("Quantidade de Pixels")
    plt.plot(hist, color='gray')
    plt.xlim([0, 256])
    plt.grid(True)
    plt.show()

def plotar_histograma_rgb(caminho_imagem):
    # Carrega a imagem colorida
    img = cv2.imread(caminho_imagem)
    
    if img is None:
        print("Erro: Imagem não encontrada.")
        return

    # Separa as cores para o loop (OpenCV usa BGR, não RGB)
    cores = ('b', 'g', 'r') 
    
    plt.figure()
    plt.title("Histograma RGB (Canais Separados)")
    plt.xlabel("Intensidade do Pixel")
    plt.ylabel("Quantidade de Pixels")

    # Loop para calcular e plotar cada canal separadamente
    for i, cor in enumerate(cores):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(hist, color=cor, label=f'Canal {cor.upper()}')

    plt.xlim([0, 256])
    plt.legend()
    plt.grid(True)
    plt.show()
if __name__ == "__main__":
    # Usando o 'r' para garantir que o Windows leia o caminho corretamente
    arquivo_teste = r'tests\image.png'

    print(f"Lendo imagem em: {arquivo_teste}")
    
    # Verifica se o arquivo existe antes de tentar plotar para evitar crash
    import os
    if os.path.exists(arquivo_teste):
        plotar_histograma_grayscale(arquivo_teste)
        plotar_histograma_rgb(arquivo_teste)
    else:
        print("ERRO CRÍTICO: O arquivo não foi encontrado nesse caminho.")
        print("Verifique se a pasta 'image' está dentro da pasta que você abriu no VS Code.")

arquivo_teste = r'tests\image.png'

# plotar_histograma_grayscale(arquivo_teste)
# plotar_histograma_rgb(arquivo_teste)