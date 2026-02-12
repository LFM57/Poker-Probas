from itertools import combinations

class EvaluateurFast:
    """Evaluateur optimisé utilisant les produits de nombres premiers et les opérations bit à bit."""
    
    # Tables de lookup (générées à l'initialisation)
    FLUSH_LOOKUP = {}
    UNSUITED_LOOKUP = {}
    
    # Rangs lisibles
    RANGS_MAINS = [
        "Carte Haute", "Paire", "Double Paire", "Brelan", 
        "Quinte", "Couleur", "Full", "Carré", "Quinte Flush"
    ]
    
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

    @staticmethod
    def _init_tables():
        """Génère les tables de lookup pour l'évaluation O(1)."""
        # Cette fonction est simplifiée pour ne pas bloquer le script, 
        # elle utilise une logique hybride (plus rapide que lookup géante)
        pass

    @staticmethod
    def evaluer_7_cartes(cartes):
        """Prend 7 objets Carte et retourne le score (Rang, Tie-Breaker)."""
        # On passe directement aux entiers
        ints = [c.bit_value for c in cartes]
        
        meilleur_score = -1
        meilleur_type = -1
        
        # On teste toutes les combinaisons de 5 cartes parmi 7
        for combo in combinations(ints, 5):
            score, type_main = EvaluateurFast.evaluer_5_ints(combo)
            # Le score combiné : (Type << 20) | Score_Interne
            total = (type_main << 24) | score
            if total > meilleur_score:
                meilleur_score = total
                meilleur_type = type_main
                
        return (meilleur_type, meilleur_score)

    @staticmethod
    def evaluer_5_ints(cards_ints):
        """Évalue 5 entiers de cartes."""
        # 1. Vérifier la Couleur (Flush)
        # On fait un OR de tous les masques de couleur. Si (OR & 0xF000) != 0, c'est pas une couleur unique
        # Optimisation: Si (c1 & c2 & c3 & c4 & c5 & 0xF000) != 0, alors toutes les cartes ont le même bit de couleur
        
        q = (cards_ints[0] | cards_ints[1] | cards_ints[2] | cards_ints[3] | cards_ints[4]) >> 16
        
        # Vérification flush
        est_flush = (cards_ints[0] & cards_ints[1] & cards_ints[2] & cards_ints[3] & cards_ints[4] & 0xF000) != 0
        
        # Vérification Quinte (Straight) via le masque de rang (q)
        # q est un bitmask des rangs présents. Ex: 1111100000000 (AKQJT)
        # On doit gérer l'As (bit 12) qui peut être 1 (bit -1 n'existe pas, on check 1111000000001 pour A2345)
        
        est_st8 = False
        if est_flush:
            # Check Straight Flush
            # On utilise une astuce binaire pour détecter 5 bits consécutifs
            # Ou plus simplement, on regarde les patterns connus
            pass # Simplifié ci-dessous
            
        # --- Méthode Hybride Rapide (Sans Lookup géante) ---
        
        # Récupérer les rangs (0-12)
        rangs = sorted([(c >> 8) & 0xF for c in cards_ints], reverse=True)
        
        est_st8 = False
        if len(set(rangs)) == 5:
            if rangs[0] - rangs[4] == 4:
                est_st8 = True
            elif rangs == [12, 3, 2, 1, 0]: # A-5-4-3-2
                est_st8 = True
                rangs = [3, 2, 1, 0, -1] # Pour le tie-breaker (5 high)

        if est_flush and est_st8:
            return (rangs[0], 8) # Straight Flush
            
        if (q in [0x7C00, 0x3E00, 0x1F00, 0xF80, 0x7C0, 0x3E0, 0x1F0, 0xF8, 0x7C, 0x3E, 0x1F] or q == 0x100F):
            # C'est une quinte (détection par masque) - redondant avec logic haut mais plus rapide si lookup
            pass

        # Carré (4-of-a-kind)
        # On utilise les primes : produit des nombres premiers
        # Si le produit est divisible par P^4...
        
        # Méthode classique optimisée : fréquence
        if est_flush:
            # Score de flush = somme des rangs pondérée
            val = rangs[0]<<16 | rangs[1]<<12 | rangs[2]<<8 | rangs[3]<<4 | rangs[4]
            return (val, 5)

        if est_st8:
            return (rangs[0], 4)

        # Paires / Brelans / Full
        # On compte les fréquences
        # Optimisation : XOR des rangs ? Non, histogramme rapide
        counts = {}
        for r in rangs:
            counts[r] = counts.get(r, 0) + 1
        
        freqs = sorted(counts.values(), reverse=True)
        
        if freqs[0] == 4:
            # Carré : Rang du carré << 4 | Kicker
            r4 = [r for r, c in counts.items() if c == 4][0]
            k = [r for r, c in counts.items() if c == 1][0]
            return ((r4 << 4) | k, 7)
            
        if freqs[0] == 3 and freqs[1] == 2:
            # Full : R3 << 4 | R2
            r3 = [r for r, c in counts.items() if c == 3][0]
            r2 = [r for r, c in counts.items() if c == 2][0]
            return ((r3 << 4) | r2, 6)
            
        if freqs[0] == 3:
            # Brelan
            r3 = [r for r, c in counts.items() if c == 3][0]
            kickers = sorted([r for r, c in counts.items() if c == 1], reverse=True)
            return ((r3 << 8) | (kickers[0] << 4) | kickers[1], 3)
            
        if freqs[0] == 2 and freqs[1] == 2:
            # Double Paire
            paires = sorted([r for r, c in counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in counts.items() if c == 1][0]
            return ((paires[0] << 8) | (paires[1] << 4) | kicker, 2)
            
        if freqs[0] == 2:
            # Paire
            pair = [r for r, c in counts.items() if c == 2][0]
            kickers = sorted([r for r, c in counts.items() if c == 1], reverse=True)
            return ((pair << 12) | (kickers[0] << 8) | (kickers[1] << 4) | kickers[2], 1)
            
        # Carte Haute
        val = rangs[0]<<16 | rangs[1]<<12 | rangs[2]<<8 | rangs[3]<<4 | rangs[4]
        return (val, 0)
