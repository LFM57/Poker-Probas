from flask import Flask, render_template, request, jsonify
from card import Carte
from simulator import Simulateur
import traceback

app = Flask(__name__)

def string_to_cards(card_strings):
    cards = []
    vus = set()
    for s in card_strings:
        if not s: continue
        c = Carte.from_str(s)
        if c in vus:
            raise ValueError(f"Carte en double détectée : {s}")
        vus.add(c)
        cards.append(c)
    return cards

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json or {}
        
        ma_main = string_to_cards(data.get('ma_main', []))
        if len(ma_main) != 2:
            return jsonify({'success': False, 'error': "Votre main doit contenir exactement 2 cartes distinctes."})

        tableau = string_to_cards(data.get('tableau', []))
        if len(tableau) not in (0, 3, 4, 5):
            return jsonify({'success': False, 'error': "Le tableau doit comporter 0 (Pré-flop), 3 (Flop), 4 (Turn) ou 5 (River) cartes."})

        exclues = string_to_cards(data.get('exclues', []))

        # Vérification des doublons entre zones
        set_main = set(ma_main)
        set_tab = set(tableau)
        set_exc = set(exclues)
        if (set_main & set_tab) or (set_main & set_exc) or (set_tab & set_exc):
            return jsonify({'success': False, 'error': "Cartes en double détectées entre votre main, le tableau et les cartes brûlées."})

        raw_profiles = data.get('profiles', ['any'])
        nb_adv = max(1, min(9, len(raw_profiles)))
        profiles = ['any'] * nb_adv

        cartes_necessaires = len(ma_main) + 5 + (2 * nb_adv) + len(exclues)
        if cartes_necessaires > 52:
            return jsonify({'success': False, 'error': f"Trop de cartes utilisées ({cartes_necessaires} > 52 dans le paquet)."})
        
        # Calcul des outs
        outs_obj = Simulateur.calculer_outs(ma_main, tableau, exclues)
        outs = [repr(c) for c in outs_obj]
        
        # Analyse de Texture
        texture = Simulateur.analyser_texture(tableau)
        
        # Heatmap (uniquement si Turn ou Flop, trop long pour PreFlop)
        heatmap = {}
        if len(tableau) >= 3 and len(tableau) < 5:
            heatmap = Simulateur.calculer_heatmap(ma_main, tableau, exclues, profiles)
        
        # Simulation
        win, tie, mains_gagnantes, mains_absolues = Simulateur.simuler(ma_main, tableau, profiles, exclues, iterations=5000)
        
        # Analyse des Tirages (basée sur la heatmap)
        tirages = []
        proba_tirage = 0
        if heatmap:
            total_inconnues = 52 - len(ma_main) - len(tableau) - len(exclues)
            tirages, proba_tirage = Simulateur.analyser_tirages(heatmap, win, total_inconnues)

        return jsonify({
            'success': True,
            'win': round(win, 2),
            'tie': round(tie, 2),
            'loss': round(max(0, 100 - win - tie), 2),
            'outs': outs,
            'texture': texture,
            'heatmap': heatmap,
            'tirages': tirages,
            'proba_tirage': proba_tirage,
            'mains_gagnantes': mains_gagnantes,
            'mains_absolues': mains_absolues
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
