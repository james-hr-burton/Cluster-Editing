#Importation des libraries
import sys
import time
import random
import signal
import fileinput

#Signalement SIGTERM
class Killer:
  exit_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit)
    signal.signal(signal.SIGTERM, self.exit)

  def exit(self,signum, frame):
    self.exit_now = True

#Algorithme de bron kerbosch pour trouver toutes les cliques maximales du graphe (pas utilisé ici)
"""
def bron_kerbosch(r, p, x, graph, cliques):
    if not p and not x:
        cliques.append(r)
    else:
        for v in p.copy():
            bron_kerbosch(r.union([v]), p.intersection(graph[v]), x.intersection(graph[v]), graph, cliques)
            p.remove(v)
            x.add(v)
    return cliques
"""

#Algorithme de bron kerbosch avec pivot pour trouver toutes les cliques maximales du graphe
def bron_kerbosch2(r, p, x, graph, cliques):
    if not p and not x:
        cliques.append(r)
    else:
        u = random.choice(tuple(p.union(x)))
        for v in p.copy().difference(graph[u]):
            bron_kerbosch2(r.union([v]), p.intersection(graph[v]), x.intersection(graph[v]), graph, cliques)
            p.remove(v)
            x.add(v)
    return cliques

#Vérifie si les éléments d'un clique sont uniques
def has_unique_(clique, graph):
    counter = 0
    for element in clique:
        for clq in graph:
            if clq != clique:
                if element in clq:
                    counter += 1
                    break
    if counter == len(clique):
        return False
    elif counter < len(clique):
        return True

#Créer des arêtes entre les sommets de cliques similaires
def check_has_elements(clq1, clq2):
    counter = 0
    for eg in clq1:
        if eg in clq2:
            counter += 1
            break
    if counter > 0:
        return True
    else:
        return False

#Fusionner deux cliques
def fusion(clq1, clq2):
    eg2 = clq2 - clq1
    eg3 = clq1 | eg2
    return eg3

#Créer la liste des arêtes du graphe sortant
def creer_aretes(grq):
    liste_edges = []
    for art in grq:
        for smt1 in art:
            for smt2 in art:
                if smt1 != smt2:
                    add = (smt1, smt2)
                    if ((smt1, smt2) not in liste_edges) and ((smt2, smt1) not in liste_edges):
                        st = (smt1, smt2)
                        liste_edges.append(st)
    return liste_edges

#Trouver les arêtes qui ont été modifiées
def get_arete_change(base, nvl):
    sendit = []
    for nxt in base:
        if ((nxt[0], nxt[1]) not in nvl) and ((nxt[1], nxt[0]) not in nvl):
            sendit.append((nxt[0], nxt[1]))
    for pre in nvl:
        if ((pre[0], pre[1]) not in base) and ((pre[1], pre[0]) not in base):
            sendit.append((pre[0], pre[1])) 
    return sendit

#Mettre en sortie les arêtes modifiées
def print_to_stdout(arete):
    ar = arete[0] + " " + arete[1]
    print(ar, file = sys.stdout)

if __name__ == '__main__':
    killer = Killer()

    #Importation du fichier et créer list des arêtes
    graphe = []
    for line in fileinput.input():
        ligne = line.rstrip()
        if not (ligne.startswith("c") or ligne.startswith("p")):
            graphe.append(tuple(ligne.split(" ")))

    #Tant que le SIGTERM n'est pas reçu, parcourir l'algorithme
    while not killer.exit_now:

        #Créer liste des voisins pour chaque sommet
        dico = {}
        for arete in graphe:
            for sommet in arete:
                if not sommet in dico:
                    dico[sommet] = []
                    for i in graphe:
                        if sommet in i:
                            if i[0] != sommet:
                                dico[sommet].append(i[0])
                            elif i[1] != sommet:
                                dico[sommet].append(i[1])

        #Création des cliques
        cl = bron_kerbosch2(set(), set(dico.keys()), set(), dico, [])

        #Sépare les cliques avec des éléments uniques
        unique = []
        not_unique = []
        for ele in cl:
            if has_unique_(ele, cl) == True:
                unique.append(ele)
            else:
                not_unique.append(ele)

        #Tant qu'il reste des cliques sans élément unique, il faut les enlever
        while not_unique:
            for el in not_unique:
                if has_unique_(el, unique + not_unique) == True:
                    not_unique.remove(el)
                    unique.append(el)
                else:
                    not_unique.remove(el)

        #Si deux cliques ont un ou des sommets en commun, alors les fusionner (pas du tout optimal, surtout si elles ont peu de sommets en commun)
        for e1 in unique:
            for e2 in unique:
                if e1 != e2:
                    if check_has_elements(e1, e2) == True:
                        fus = fusion(e1, e2)
                        if e1 in unique and e2 in unique:
                            unique.remove(e1)
                            unique.remove(e2)
                            unique.append(fus)
        
        #Créer la liste des arêtes de toutes les cliques trouvées
        lxx = creer_aretes(unique)

        #Trouver les arêtes qui ont été ajoutées / enlevées
        END = get_arete_change(graphe, lxx)

        #Envoyer les arêtes modifées au stdout
        for rmx in END:
            print_to_stdout(rmx)

        #Sortie de la boucle et fin du programmme
        break