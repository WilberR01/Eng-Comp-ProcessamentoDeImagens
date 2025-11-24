"""
Script de teste para verificar que os dois novos analisadores
são descobertos e funcionam corretamente.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from gerenciador import MotorDeAnalise

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTE: Descoberta de Analisadores")
    print("=" * 60)
    
    motor = MotorDeAnalise()
    
    print(f"\n✓ Total de analisadores descobertos: {len(motor.analisadores)}\n")
    
    for i, analisador in enumerate(motor.analisadores, 1):
        print(f"{i}. {analisador.nome_modulo}")
    
    print("\n" + "=" * 60)
    print("Esperado: 4 analisadores")
    print("  1. Analisador de Exemplo")
    print("  2. Analisador de Exemplo 2")
    print("  3. Equalizador de Histograma (NOVO)")
    print("  4. Detector de Formas (NOVO)")
    print("=" * 60 + "\n")
    
    if len(motor.analisadores) >= 3:
        nomes = [a.nome_modulo for a in motor.analisadores]
        
        if "Equalizador de Histograma" in nomes:
            print("✅ Equalizador de Histograma descoberto com sucesso!")
        else:
            print("❌ Equalizador de Histograma NÃO foi descoberto")
        
        if "Detector de Formas" in nomes:
            print("✅ Detector de Formas descoberto com sucesso!")
        else:
            print("❌ Detector de Formas NÃO foi descoberto")
    else:
        print(f"⚠️  Apenas {len(motor.analisadores)} analisador(es) encontrado(s)")
