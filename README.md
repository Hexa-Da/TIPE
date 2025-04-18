# Simulation de Trafic Routier 

## À propos
Ce projet est une simulation de trafic routier développée en Python dans le cadre d'un TIPE (Travail d'Initiative Personnelle Encadré). Il permet de simuler et d'analyser le comportement du trafic routier aux intersections avec différentes configurations de feux de circulation.

## Fonctionnalités 

- Simulation de 1, 2 ou 4 carrefours interconnectés
- Gestion de différents types de véhicules (voitures, bus, camions, motos)
- Deux modes de fonctionnement des feux de circulation
- Interface graphique interactive avec Pygame
- Analyse en temps réel des temps d'attente et du flux de véhicules

## Prérequis 

- Python 3.x
- Pygame 2.x
- Autres dépendances standard Python (random, time, sys, statistics)

## Installation 

1. Clonez le repository
2. Installez les dépendances :
```bash
pip install pygame
```

## Utilisation 

1. Naviguez vers le dossier du projet :
```bash
cd chemin/vers/TIPE
```

2. Lancez la simulation :
```bash
python3 Code.py
```

## Configuration 

Vous pouvez modifier les paramètres suivants dans le fichier `Code.py` :

```python
nbrCarrefour = 4                # 1, 2 ou 4 carrefours
FonctionnementFeux = 2          # 1: feux 2 à 2, 2: feux 1 par 1
ChanceVehicule = [25,50,75,100] # Probabilités d'apparition des véhicules
Vert = 10                       # Durée du feu vert
Orange = 3                      # Durée du feu orange
```

## Métriques et Analyses 

La simulation fournit en temps réel :
- Temps d'attente maximum (Tmax)
- Temps d'attente moyen (Tmoy)
- Temps d'attente médian (Tmed)
- Nombre de véhicules par direction

## Structure du Projet 

- `Code.py` : Programme principal
- `images/` : Assets graphiques pour 1 et 2 carrefours
- `images4C/` : Assets graphiques pour 4 carrefours

## Contrôles 

- Fermer la fenêtre pour arrêter la simulation
- La simulation s'arrête automatiquement après le temps limite défini (Texplim)

## Caractéristiques Techniques 🔧

- Gestion des collisions
- Changement de voies intelligent
- Distances de sécurité adaptatives
- Synchronisation des feux paramétrable
- Logging des événements

## Contribution 

Ce projet a été développé dans le cadre d'un TIPE. N'hésitez pas à l'utiliser comme base pour vos propres expérimentations ou améliorations.

## Licence 

Ce projet est disponible sous licence libre pour usage éducatif et personnel.

---
*Développé avec ❤️ pour le TIPE grâce à M.Viard* 
