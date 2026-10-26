import random
from itertools import combinations
from card import Carte, Paquet
from evaluator_fast import EvaluateurFast

class Simulateur:
    """Moteur de simulation complet avec Analyse et Heatmap."""

    @staticmethod
    def analyser_texture(tableau):
        """Analyse le danger du tableau (Flush draw, Straight draw, Paires)."""
        if len(tableau) < 3: return []
        
        alerts = []
        couleurs = [c.couleur for c in tableau]
        counts_c = {k: couleurs.count(k) for k in set(couleurs)}
        max_c = max(counts_c.values()) if counts_c else 0
        
        if max_c >= 3: alerts.append("Danger Couleur (3+ cartes)")
        elif max_c == 2: alerts.append("Tirage Couleur possible")
            
        rangs = sorted([c.rang for c in tableau])
        counts_r = {k: rangs.count(k) for k in set(rangs)}
        max_r = max(counts_r.values())
        if max_r >= 2: alerts.append("Paire sur le tableau")
        if max_r >= 3: alerts.append("Brelan sur le tableau")
        
        rangs_unique = sorted(list(set(rangs)))
        connected_count = 0
        for i in range(len(rangs_unique) - 2):
            if rangs_unique[i+2] - rangs_unique[i] <= 4:
                connected_count = 3
                break
        if connected_count >= 3: alerts.append("Tirage Quinte possible")
        
        return alerts

    @staticmethod
    def analyser_tirages(heatmap, win_actuel, total_inconnues):
        """Regroupe les cartes bénéfiques de manière intelligente et fiable."""
        tirages = []
        bonnes_cartes = [c for c, eq in heatmap.items() if eq > (win_actuel + 5)]
        
        if not bonnes_cartes: return [], 0

        # Récupérer toutes les cartes testées dans la heatmap pour comparer
        toutes_testees = list(heatmap.keys())
        cartes_retenues_global = set()
        
        # 1. Analyse par Rang (ex: Les 5)
        rangs_presents = set(c[0] for c in toutes_testees)
        for r in rangs_presents:
            dans_ce_rang = [c for c in toutes_testees if c[0] == r]
            bons_dans_ce_rang = [c for c in dans_ce_rang if c in bonnes_cartes]
            
            # Condition : Au moins 75% du rang doit être bon ET au moins 2 cartes
            if len(bons_dans_ce_rang) >= 2 and (len(bons_dans_ce_rang) / len(dans_ce_rang)) >= 0.75:
                nom = f"Un {Carte.NOM_VALEURS.get(r, r)}"
                prob = (len(bons_dans_ce_rang) / total_inconnues) * 100
                tirages.append({'nom': nom, 'prob': round(prob, 1), 'type': 'rank'})
                for c in bons_dans_ce_rang: cartes_retenues_global.add(c)

        # 2. Analyse par Couleur (ex: Les Cœurs)
        couleurs_presentes = set(c[-1] for c in toutes_testees)
        for coul in couleurs_presentes:
            dans_cette_coul = [c for c in toutes_testees if c[-1] == coul]
            bons_dans_cette_coul = [c for c in dans_cette_coul if c in bonnes_cartes]
            
            # Condition : Au moins 75% de la couleur doit être bonne ET au moins 4 cartes
            if len(bons_dans_cette_coul) >= 4 and (len(bons_dans_cette_coul) / len(dans_cette_coul)) >= 0.75:
                nom = f"Un {Carte.NOM_COULEURS.get(coul, coul)}"
                prob = (len(bons_dans_cette_coul) / total_inconnues) * 100
                tirages.append({'nom': nom, 'prob': round(prob, 1), 'type': 'suit'})
                for c in bons_dans_cette_coul: cartes_retenues_global.add(c)
        
        # Probabilité cumulée réelle (Union de toutes les cartes bénéfiques identifiées)
        proba_cumulee = (len(cartes_retenues_global) / total_inconnues) * 100
        
        return sorted(tirages, key=lambda x: x['prob'], reverse=True), round(proba_cumulee, 1)

    @staticmethod
    def calculer_heatmap(ma_main, tableau, cartes_exclues, profils):
        """Estime l'impact de chaque carte future sur l'équité (Multi-joueurs)."""
        if len(tableau) >= 5 or len(tableau) < 3:
            return {}
        
        nb_adv = len(profils)
        if nb_adv < 1:
            return {}
            
        cartes_connues = set(ma_main) | set(tableau) | set(cartes_exclues)
        paquet = Paquet()
        cartes_testables = [c for c in paquet.cartes if c not in cartes_connues]
        
        impacts = {}
        is_flop = (len(tableau) == 3)
        base_iterations = 80 if is_flop else (120 if nb_adv <= 3 else 80)
        needed_sample = (2 * nb_adv + 1) if is_flop else (2 * nb_adv)
        
        for carte_future in cartes_testables:
            tableau_futur = tableau + [carte_future]
            pool = [c for c in cartes_testables if c != carte_future]
            if len(pool) < needed_sample:
                break
                
            victoires = 0
            mon_score_turn = None
            if not is_flop:
                mon_score_turn = EvaluateurFast.evaluer_7_cartes(ma_main + tableau_futur)[1]

            for _ in range(base_iterations):
                sampled = random.sample(pool, needed_sample)
                if is_flop:
                    river_card = sampled[-1]
                    full_board = tableau_futur + [river_card]
                    hero_score = EvaluateurFast.evaluer_7_cartes(ma_main + full_board)[1]
                else:
                    full_board = tableau_futur
                    hero_score = mon_score_turn
                
                gagne = True
                partage = False
                for i in range(nb_adv):
                    m_adv = [sampled[2 * i], sampled[2 * i + 1]]
                    adv_score = EvaluateurFast.evaluer_7_cartes(m_adv + full_board)[1]
                    if adv_score > hero_score:
                        gagne = False
                        break
                    elif adv_score == hero_score:
                        partage = True
                
                if gagne:
                    victoires += 1 if not partage else 0.5
            
            equite = (victoires / base_iterations) * 100
            impacts[repr(carte_future)] = equite
            
        return impacts

    @staticmethod
    def _est_feature_tableau(tableau, carte_test, best_type):
        """Vérifie si la combinaison atteinte existe déjà sur le tableau seul avec la carte test."""
        board_cards = tableau + [carte_test]
        ranks = [c.rang for c in board_cards]
        counts = {}
        for r in ranks: counts[r] = counts.get(r, 0) + 1
        max_c = max(counts.values()) if counts else 0
        pairs = [r for r, c in counts.items() if c >= 2]
        
        if max_c >= 4 and best_type <= 7: return True
        if max_c >= 3 and best_type <= 3: return True
        if len(pairs) >= 2 and best_type <= 2: return True
        if len(pairs) >= 1 and best_type <= 1: return True
        
        suits = [c.couleur for c in board_cards]
        suit_counts = {s: suits.count(s) for s in set(suits)}
        if max(suit_counts.values()) >= 5 and best_type <= 5: return True
        
        if len(board_cards) >= 5:
            b_ranks = sorted(list(set(ranks)), reverse=True)
            if 12 in b_ranks: b_ranks.append(-1)
            for i in range(len(b_ranks) - 4):
                if b_ranks[i] - b_ranks[i+4] == 4 and best_type <= 4:
                    return True
        return False

    @staticmethod
    def calculer_outs(ma_main, tableau, cartes_exclues=None):
        """Calcule les outs réels améliorant la catégorie de main avec les cartes du joueur."""
        if len(tableau) >= 5 or len(tableau) < 3: return []
        if cartes_exclues is None: cartes_exclues = []
        
        cartes_connues = set(ma_main) | set(tableau) | set(cartes_exclues)
        paquet = [c for c in Paquet().cartes if c not in cartes_connues]
        
        current_type, current_score = EvaluateurFast.evaluer_7_cartes(ma_main + tableau)
        outs = []
        
        for carte_test in paquet:
            new_cards = ma_main + tableau + [carte_test]
            best_score = -1
            best_type = -1
            best_combo = None
            for combo in combinations(new_cards, 5):
                s, t = EvaluateurFast.evaluer_5_ints([c.bit_value for c in combo])
                tot = (t << 24) | s
                if tot > best_score:
                    best_score = tot
                    best_type = t
                    best_combo = combo
                    
            # Amélioration stricte de la catégorie de main requise
            if best_type <= current_type:
                continue
            if carte_test not in best_combo:
                continue
            if not any(h in best_combo for h in ma_main):
                continue
            if Simulateur._est_feature_tableau(tableau, carte_test, best_type):
                continue
                
            outs.append(carte_test)
        return outs

    @staticmethod
    def simuler(ma_main, tableau, profils, cartes_exclues=None, iterations=10000):
        victoires = 0
        egalites = 0
        stats_mains = [0] * 9
        total_mains = [0] * 9
        if cartes_exclues is None: cartes_exclues = []
        
        cartes_connues = set(ma_main) | set(tableau) | set(cartes_exclues)
        paquet_base = Paquet()
        cartes_restantes = [c for c in paquet_base.cartes if c not in cartes_connues]
        
        nb_adv = len(profils)
        cartes_a_venir = 5 - len(tableau)
        cartes_necessaires = 2 * nb_adv + cartes_a_venir
        if len(cartes_restantes) < cartes_necessaires or nb_adv < 1:
            return 0.0, 0.0, {}, {}
        
        for _ in range(iterations):
            sampled = random.sample(cartes_restantes, cartes_necessaires)
            tableau_simu = list(tableau) + sampled[:cartes_a_venir]
            
            mon_res = EvaluateurFast.evaluer_7_cartes(ma_main + tableau_simu)
            mon_score_total = mon_res[1]
            mon_type = mon_res[0]
            
            gagne = True
            partage = False
            offset = cartes_a_venir
            for _ in range(nb_adv):
                adv_res = EvaluateurFast.evaluer_7_cartes([sampled[offset], sampled[offset + 1]] + tableau_simu)
                offset += 2
                if adv_res[1] > mon_score_total:
                    gagne = False
                    break
                elif adv_res[1] == mon_score_total:
                    partage = True
            
            total_mains[mon_type] += 1
            if gagne:
                if partage: egalites += 1
                else:
                    victoires += 1
                    stats_mains[mon_type] += 1
                
        total_played = sum(total_mains)
        prob_victoire = (victoires / total_played * 100) if total_played > 0 else 0
        prob_egalite = (egalites / total_played * 100) if total_played > 0 else 0
        
        repartition_gagnante = {}
        if victoires > 0:
            for i, count in enumerate(stats_mains):
                if count > 0:
                    repartition_gagnante[EvaluateurFast.RANGS_MAINS[i]] = (count / victoires) * 100
        
        repartition_absolue = {}
        if total_played > 0:
            for i, count in enumerate(total_mains):
                if count > 0:
                    repartition_absolue[EvaluateurFast.RANGS_MAINS[i]] = (count / total_played) * 100
        
        return prob_victoire, prob_egalite, repartition_gagnante, repartition_absolue
