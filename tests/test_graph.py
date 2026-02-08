# ==================     TEST THE GRAPH     =======================

# tests/test_graph.py

from src.graph.workflow import graph

def test_graph():
    """Teste completo do workflow"""
    
    input_state = {
        'type_post': 'description',
        'topic': 'Carros',
        'idea': 'dilema dos carros eletricos',
        'tone': 'professional',
        'slides': 0,
        'messages': []
    }
    
    print("🚀 Iniciando workflow...\n")
    
    result = graph.invoke(input_state)
    
    print("=" * 50)
    print("📊 RESULTADO FINAL")
    print("=" * 50)
    print(f"\n✅ Research: {result.get('result_research')}")
    print(f"\n✅ Final Report: {result.get('final_report')}")
    print("=" * 50)
    
    return result


if __name__ == "__main__":
    test_graph()
   