"""
Script de teste para demonstrar os dois analisadores atualizados
com imagens visuais e ordem de execução.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from gerenciador import MotorDeAnalise

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTE: Ordem de Execução e Analisadores com Imagens Visuais")
    print("=" * 70)
    
    motor = MotorDeAnalise()
    
    print(f"\n✓ Total de analisadores descobertos: {len(motor.analisadores)}\n")
    print("Ordem de execução:")
    print("-" * 70)
    
    for i, analisador in enumerate(motor.analisadores, 1):
        print(f"{i:2d}. [{analisador.ordem:3d}] {analisador.nome_modulo}")
    
    print("\n" + "=" * 70)
    print("Melhorias implementadas:")
    print("=" * 70)
    print("""
✅ Propriedade 'ordem' adicionada:
   - Cada analisador pode definir ordem (padrão: 999)
   - Executados em ordem crescente para melhor leitura do relatório

✅ Equalizador de Histograma (ordem: 20):
   - Retorna 3 imagens em base64 para comparação:
     • Original (escala de cinza)
     • Resultado com Equalização Padrão
     • Resultado com CLAHE (Contrast-Limited Adaptive Histogram)
   - Exibe métricas de contraste e melhoria (%)

✅ Detector de Formas (ordem: 30):
   - Retorna 4 imagens em base64 para visualização:
     • Original (imagem colorida)
     • Bordas detectadas (Canny)
     • Todos os contornos encontrados
     • Formas coloridas por tipo:
       - Azul: Triângulos
       - Verde: Quadrados/Retângulos
       - Vermelho: Círculos/Ovais
   - Marca centróide de cada forma detectada
   - Exibe métricas detalhadas de cada forma

✅ Interface de Relatório:
   - Imagens podem ser renderizadas no template HTML
   - Use: {{ resultado.extra.imagens_processadas.nome_imagem }}
   - Todas as imagens já vêm em formato data:image/png;base64
    """)
    
    print("\n" + "=" * 70 + "\n")
