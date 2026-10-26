import sys
from card import Carte
from simulator import Simulateur

def parser_cartes(entree):
    mots = entree.replace(',', ' ').split()
    cartes = []
    vus = set()
    for mot in mots:
        if not mot: continue
        try:
            c = Carte.from_str(mot)
        except ValueError:
            print(f"Erreur : Carte invalide '{mot}'")
            return None
        if c in vus:
            print(f"Erreur : Carte en double détectée '{mot}'")
            return None
        vus.add(c)
        cartes.append(c)
    return cartes

def main():
    print("\n" + "="*50)
    print("   CALCULATEUR POKER PRO - ANALYSE AVANCÉE")
    print("="*50)
    
    while True:
        entree_ma_main = input("\nVotre main (ex: Ah Ad) : ")
        ma_main = parser_cartes(entree_ma_main)
        if ma_main and len(ma_main) == 2: break
        if ma_main is not None:
            print("Veuillez entrer exactement 2 cartes distinctes.")

    while True:
        entree_tableau = input("Le tableau (ex: 7h 8h 9h, ou vide) : ")
        tableau = parser_cartes(entree_tableau)
        if tableau is None:
            continue
        if len(tableau) not in (0, 3, 4, 5):
            print("Le tableau doit contenir 0 (Pré-flop), 3 (Flop), 4 (Turn) ou 5 (River) cartes.")
            continue
        conflits = set(tableau) & set(ma_main)
        if conflits:
            print(f"Erreur : Cartes déjà dans votre main : {', '.join(str(c) for c in conflits)}")
            continue
        break

    while True:
        entree_exclues = input("Cartes sorties/brûlées (ex: 2c 3d, ou vide) : ")
        exclues = parser_cartes(entree_exclues)
        if exclues is None:
            continue
        conflits = (set(exclues) & set(ma_main)) | (set(exclues) & set(tableau))
        if conflits:
            print(f"Erreur : Cartes déjà utilisées : {', '.join(str(c) for c in conflits)}")
            continue
        break

    while True:
        entree_adv = input("Nombre d'adversaires (1-9) : ").strip() or "1"
        try:
            nb_adv = int(entree_adv)
            if 1 <= nb_adv <= 9:
                break
            print("Le nombre d'adversaires doit être compris entre 1 et 9.")
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")

    cartes_necessaires = len(ma_main) + 5 + (2 * nb_adv) + len(exclues)
    if cartes_necessaires > 52:
        print(f"Erreur : Trop de cartes demandées ({cartes_necessaires} > 52 dans le paquet).")
        return

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
    profils = ['random'] * nb_adv
    win, tie, mains_gagnantes, mains_absolues = Simulateur.simuler(ma_main, tableau, profils, exclues)

    print("\n--- PROBABILITÉS DE VICTOIRE ---")
    print(f"VICTOIRE : {win:.2f}%")
    print(f"ÉGALITÉ  : {tie:.2f}%")
    print(f"DÉFAITE  : {(100 - win - tie):.2f}%")

    if mains_gagnantes:
        print("\n--- VOS MAINS GAGNANTES (Répartition) ---")
        for nom, proc in sorted(mains_gagnantes.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nom}: {proc:.1f}% de vos victoires")

    if mains_absolues:
        print("\n--- PROBABILITÉ DES MAINS OBTENUES (Toutes issues) ---")
        for nom, proc in sorted(mains_absolues.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nom}: {proc:.1f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
        sys.exit(0)
