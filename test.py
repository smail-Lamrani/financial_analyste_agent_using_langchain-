import asyncio
from agents.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()

# --- LISTE DES TESTS ---
TESTS = [
    # Test 1 : Synthèse complète (Web + Finance)
    "Donne-moi une analyse complète de NVIDIA : prix actuel, fondamentaux, actualités récentes et contexte de marché.",

    # Test 2 : Vérification anti-hallucination
    "Quel est le prix exact actuel de l’action Tesla ? Et son chiffre d'affaires du trimestre en cours ?",

    # Test 3 : News uniquement
    "Quelles sont les dernières actualités concernant Apple ?",

    # Test 4 : Finance uniquement (sans web)
    "Analyse financière de l'action Microsoft (MSFT) avec les principaux ratios.",

    # Test 5 : Demande floue (doit être rejetée proprement)
    "Votre analyse précédente était correcte.",
]


async def run_tests():
    for i, query in enumerate(TESTS, 1):
        print("\n" + "-"*80)
        print(f"🚀 Test {i}: {query}")
        print("-"*80)

        try:
            response = await orchestrator.query(query)
            print("\n📌 RESPONSE:")
            print(response)
        except Exception as e:
            print(f"❌ ERROR during test {i}: {e}")


if __name__ == "__main__":
    asyncio.run(run_tests())
