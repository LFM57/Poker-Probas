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
        if len(tableau) >= 5: return {}
        
        nb_adv = len(profils)
        cartes_connues = list(ma_main) + list(tableau) + list(cartes_exclues)
        paquet = Paquet()
        cartes_testables = [c for c in paquet.cartes if not any(c.valeur == ck.valeur and c.couleur == ck.couleur for ck in cartes_connues)]
        
        impacts = {}
        # On réduit les itérations pour garder une interface fluide
        base_iterations = 150 if nb_adv <= 3 else 80 
        
        for carte_future in cartes_testables:
            tableau_futur = tableau + [carte_future]
            victoires = 0
            pool = [c for c in cartes_testables if c != carte_future]
            
            # Calcul du score héro une seule fois pour ce tableau futur
            mon_score = EvaluateurFast.evaluer_7_cartes(ma_main + tableau_futur)[1]

            for _ in range(base_iterations):
                random.shuffle(pool)
                idx = 0
                mains_actives = []
                for _ in range(nb_adv):
                    if idx + 2 > len(pool): break
                    mains_actives.append([pool[idx], pool[idx+1]])
                    idx += 2
                
                gagne = True
                partage = False
                for m_adv in mains_actives:
                    adv_score = EvaluateurFast.evaluer_7_cartes(m_adv + tableau_futur)[1]
                    if adv_score > mon_score:
                        gagne = False
                        break
                    elif adv_score == mon_score:
                        partage = True
                
                if gagne:
                    victoires += 1 if not partage else 0.5
            
            equite = (victoires / base_iterations) * 100
            impacts[repr(carte_future)] = equite
            
        return impacts

    @staticmethod
    def calculer_outs(ma_main, tableau, cartes_exclues):
        if len(tableau) >= 5: return []
        cartes_connues = list(ma_main) + list(tableau) + list(cartes_exclues)
        paquet = Paquet()
        paquet.cartes = [c for c in paquet.cartes if not any(c.valeur == ck.valeur and c.couleur == ck.couleur for ck in cartes_connues)]
        
        score_actuel = EvaluateurFast.evaluer_7_cartes(ma_main + tableau)
        outs = []
        for carte_test in paquet.cartes:
            nouveau_score = EvaluateurFast.evaluer_7_cartes(ma_main + tableau + [carte_test])
            if nouveau_score[1] > score_actuel[1]:
                outs.append(carte_test)
        return outs

    @staticmethod
    def simuler(ma_main, tableau, profils, cartes_exclues=None, iterations=10000):
        victoires = 0
        egalites = 0
        stats_mains = [0] * 9
        total_mains = [0] * 9
        if cartes_exclues is None: cartes_exclues = []
        
        cartes_connues = list(ma_main) + list(tableau) + list(cartes_exclues)
        paquet_base = Paquet()
        cartes_restantes = [c for c in paquet_base.cartes if not any(c.valeur == ck.valeur and c.couleur == ck.couleur for ck in cartes_connues)]
        
        nb_adv = len(profils)
        cartes_a_venir = 5 - len(tableau)
        iterations_reelles = 20000 if iterations == 5000 else iterations 
        
        for _ in range(iterations_reelles):
            random.shuffle(cartes_restantes)
            idx = 0
            mains_actives = []
            
            for _ in profils:
                if idx + 2 > len(cartes_restantes): break
                mains_actives.append([cartes_restantes[idx], cartes_restantes[idx+1]])
                idx += 2

            tableau_simu = list(tableau)
            for _ in range(cartes_a_venir):
                tableau_simu.append(cartes_restantes[idx])
                idx += 1
            
            mon_res = EvaluateurFast.evaluer_7_cartes(ma_main + tableau_simu)
            mon_score_total = mon_res[1]
            mon_type = mon_res[0]
            
            gagne = True
            partage = False
            for m_adv in mains_actives:
                adv_res = EvaluateurFast.evaluer_7_cartes(m_adv + tableau_simu)
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
        
        repartition_absolue = {}
        if total_played > 0:
            for i, count in enumerate(total_mains):
                if count > 0:
                    repartition_absolue[EvaluateurFast.RANGS_MAINS[i]] = (count / total_played) * 100
        
        return prob_victoire, prob_egalite, {}, repartition_absolue
