from flask import Flask, render_template, request, jsonify
from card import Carte
from simulator import Simulateur
import traceback

app = Flask(__name__)

def string_to_cards(card_strings):
    cards = []
    for s in card_strings:
        if not s: continue
        valeur = s[0].upper()
        couleur = s[1].lower()
        cards.append(Carte(valeur, couleur))
    return cards

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        print(f"DEBUG: Data received = {data}") # Log pour voir les données
        
        ma_main = string_to_cards(data.get('ma_main', []))
        tableau = string_to_cards(data.get('tableau', []))
        exclues = string_to_cards(data.get('exclues', []))
        profiles = data.get('profiles', ['any'])
        
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
    except Exception as e:
        print("!!! ERREUR DURANT LA SIMULATION !!!")
        traceback.print_exc() # Affiche l'erreur complète dans le terminal
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
