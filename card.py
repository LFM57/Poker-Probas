import random

class Carte:
    """Représente une carte optimisée avec encodage binaire (Cactus Kev / Prime Product)."""
    
    VALEURS = "23456789TJQKA"
    COULEURS = "shdc"  # s=pique, h=coeur, d=carreau, c=trèfle
    
    # Nombres premiers associés à chaque rang
    # 2=2, 3=3, 5=5, 7=7, 11=11, 13=13, 17=17, 19=19, 23=23, 29=29, 31=31, 37=37, 41=41
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

    NOM_VALEURS = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        'T': '10', 'J': 'Valet', 'Q': 'Dame', 'K': 'Roi', 'A': 'As'
    }
    
    NOM_COULEURS = {
        's': 'Pique', 'h': 'Cœur', 'd': 'Carreau', 'c': 'Trèfle'
    }

    def __init__(self, valeur, couleur):
        if valeur not in self.VALEURS or couleur not in self.COULEURS:
            raise ValueError(f"Carte invalide : {valeur}{couleur}")
        self.valeur = valeur
        self.couleur = couleur
        self.rang = self.VALEURS.index(valeur)
        
        # Encodage binaire pour l'optimisation
        # Format (32 bits) : xxxxyyyy zzzzAAAA BBBBCCCC DDDDEEEE
        # EEEE (4 bits) : Nombre premier du rang (table PRIMES)
        # CCCC (4 bits) : Rang (0-12)
        # BBBB (4 bits) : Masque de couleur (1, 2, 4, 8)
        # AAAA (13 bits): Masque de rang (1 << rang)
        
        prime = self.PRIMES[self.rang]
        rank_shift = self.rang << 8
        suit_shift = (1 << self.COULEURS.index(couleur)) << 12
        rank_mask = (1 << self.rang) << 16
        
        self.bit_value = prime | rank_shift | suit_shift | rank_mask

    def __repr__(self):
        return f"{self.valeur}{self.couleur}"

    def __str__(self):
        return f"{self.NOM_VALEURS[self.valeur]} de {self.NOM_COULEURS[self.couleur]}"

class Paquet:
    """Représente un paquet de 52 cartes."""
    
    def __init__(self):
        self.cartes = [Carte(v, c) for v in Carte.VALEURS for c in Carte.COULEURS]
        self.melanger()

    def melanger(self):
        random.shuffle(self.cartes)

    def tirer(self):
        if not self.cartes:
            return None
        return self.cartes.pop()

    def retirer_cartes(self, cartes_a_retirer):
        """Retire des cartes spécifiques du paquet (pour les mains connues)."""
        str_cartes = [str(c) for c in cartes_a_retirer]
        self.cartes = [c for c in self.cartes if str(c) not in str_cartes]
