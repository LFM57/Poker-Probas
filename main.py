import sys
from card import Carte
from simulator import Simulateur

def parser_cartes(entree):
    mots = entree.replace(',', ' ').split()
    cartes = []
    for mot in mots:
        if len(mot) < 2: continue
        valeur = mot[0].upper()
        couleur = mot[1].lower()
        try:
            cartes.append(Carte(valeur, couleur))
        except ValueError:
            print(f"Erreur : Carte invalide '{mot}'")
            return None
    return cartes

def main():
    print("\n" + "="*50)
    print("   CALCULATEUR POKER PRO - ANALYSE AVANCÉE")
    print("="*50)
    
    while True:
        entree_ma_main = input("\nVotre main (ex: Ah Ad) : ")
        ma_main = parser_cartes(entree_ma_main)
        if ma_main and len(ma_main) == 2: break
        print("Veuillez entrer exactement 2 cartes.")

    entree_tableau = input("Le tableau (ex: 7h 8h 9h, ou vide) : ")
    tableau = parser_cartes(entree_tableau) or []

    entree_exclues = input("Cartes sorties/brûlées (ex: 2c 3d, ou vide) : ")
    exclues = parser_cartes(entree_exclues) or []

    try:
        nb_adv = int(input("Nombre d'adversaires : ") or "1")
    except ValueError:
        nb_adv = 1

    print("\n" + "-"*30)
    print("ANALYSE DES OUTS (Cartes à venir)")
    outs = Simulateur.calculer_outs(ma_main, tableau, exclues)
    if not outs:
        if len(tableau) >= 5:
            print("Tableau complet. Plus d'outs possibles.")
        else:
            print("Aucune carte simple n'améliore votre main immédiatement.")
    else:
        print(f"Outs détectés ({len(outs)}) : " + ", ".join([str(c) for c in outs]))
        prob_out = (len(outs) / (52 - 2 - len(tableau) - len(exclues))) * 100
        print(f"Probabilité de toucher un out au prochain tour : {prob_out:.2f}%")

    print("\nSIMULATION MONTE CARLO (10 000 itérations)...")
    win, tie, mains_stats = Simulateur.simuler(ma_main, tableau, nb_adv, exclues)

    print("\n--- PROBABILITÉS DE VICTOIRE ---")
    print(f"VICTOIRE : {win:.2f}%")
    print(f"ÉGALITÉ  : {tie:.2f}%")
    print(f"DÉFAITE  : {(100 - win - tie):.2f}%")

    if mains_stats:
        print("\n--- VOS MAINS GAGNANTES (Répartition) ---")
        for nom, proc in sorted(mains_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nom}: {proc:.1f}% des victoires")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
        sys.exit(0)
