import random
import time 
import pygame
import sys
import statistics



#################### Tableau de commande ######################

nbrCarrefour = 1                #1,2 ou 4 pour l'instant
FonctionnementFeux = 2          #1: 2 à 2 ou 2: 1 par 1

ChanceVehicule = [25,50,75,100]     #Voiture,Bus,Camion,Moto
ChanceAxe = [50,50]                 #1 ou 2
ChanceSens = [50,50]                #1 ou -1

Vert = 10
Orange = 3
RetardSynch = +0
Rouge = Vert+Orange+RetardSynch
Texplim = 5*60
pasDeTemps = 10**(-16)

log = []
use="random"
#Voie,ClasseVehicule,Axe,Sens,Tourner,Immatriculation
test = [(1, 1, 1, 1, 0, 5), (0, 0, 1, 1, 1, 4)]

###############################################################



pygame.init()                           
Simulation = pygame.sprite.Group()      

#Axe: Horizontal=1 / Vertical=2 et -1 ou +1 pour le Sens d'évolution
TypesVehicule = {0:'voiture', 1:'bus', 2:'camion', 3:'moto'}        
NumDirection = {1:'droite', -1:'gauche', 2:'bas', -2:'haut'}  

Carrefours = []
Decalage = 150
STOP = False
temps = 0
t = 0
Tmax = 0
listTps = []
Immatriculation = 0



if nbrCarrefour == 1:
    pasDeTempFeux,pasDeTempsInitV = 0.00000000000009,0.00000000000009
    Vitesse = {'voiture':0.16, 'bus':0.14, 'camion':0.14, 'moto':0.17}
    Supprimer = {1:750, -1:0, 2:750, -2:0}
    image = "images/"
    Gap = 15
    
elif nbrCarrefour == 2:
    pasDeTempFeux,pasDeTempsInitV = 0.000000000000005,0.000000000000005
    Vitesse = {'voiture':1.75, 'bus':1.5, 'camion':1.5, 'moto':2}
    Supprimer = {1:1350, -1:0, 2:750, -2:0}
    image = "images/"
    Gap = 15
    
elif nbrCarrefour == 4:
    pasDeTempFeux,pasDeTempsInitV = 0.00000000000001,0.00000000000001
    Vitesse = {'voiture':0.6, 'bus':0.55, 'camion':0.55, 'moto':0.65}    
    Supprimer = {1:770, -1:0, 2:770, -2:0}
    image = "images4C/"
    Gap = 10
   




class Carrefour:
    def __init__(self,PointsSpawn,Signal,Compteur,Virage,MaxAtt,Vehicules):

        self.PointsSpawn = PointsSpawn
        #Chaque carrefour a son dico Vehicules
        self.Vehicules = Vehicules
        self.Signal = Signal
        self.Compteur = Compteur
        self.Virage = Virage
        self.MaxAtt = MaxAtt
        #Il faut determiner les endroits ou on peut spawn
        #Il est donc nécéssaire de connaitre les voisins de chaque carrefour
        self.Voisins={1: None, -1: None, 2: None, -2: None}


    def ajouterVoisin(self, direction, voisin):
        self.Voisins[direction] = voisin




class Feux:
    def __init__(self, rouge, orange, vert, LigneStop):

        self.rouge = rouge                        
        self.orange = orange                      
        self.vert = vert                          
        self.timer = ""
        self.LigneStop = LigneStop





class Vehicule(pygame.sprite.Sprite):                        
    def __init__(self, Voie, ClasseVehicule, Axe, Sens, Tourner, Carrefour, Immatriculation):
        pygame.sprite.Sprite.__init__(self)  
                                                                                         
        self.ClasseVehicule = ClasseVehicule
        self.Vitesse = Vitesse[ClasseVehicule]

        self.Immatriculation = Immatriculation
        self.Tourner = Tourner
        self.Temps = 0
        self.Carrefour = Carrefour
        self.Franchi = False
        
        self.Voie = Voie 
        self.Axe = Axe
        self.Sens = Sens
        self.Direction = Axe*Sens

        #Chaque véhicule est reperé par un couple [x,y]                        
        self.Position = [self.Carrefour.PointsSpawn[self.Direction][Voie],self.Carrefour.PointsSpawn[self.Direction][Voie+2]]

        #Trouver l'image du véhicule dans les dossiers 
        chemin = image + NumDirection[self.Direction] + "/" + ClasseVehicule + ".png"         
        self.image = pygame.image.load(chemin)

        #Aouter le véhicule a la liste de sa voie en première position
        self.Carrefour.Vehicules[self.Direction][Voie].insert(0,self)     
        
        self.lVoie = self.Carrefour.Vehicules[self.Direction][self.Voie]  

        self.Mouv = False
    
        #Ajoute le véhicule à la simulation
        Simulation.add(self)        

                        
    def CalculStop(self):
        
        PasPremierVehicule = self.lVoie[-1] != self
        SensPositif = self.Sens == 1    
        SensNegatif = self.Sens == -1
        LigneStop = self.Carrefour.Signal[self.Direction].LigneStop
        if len(self.lVoie) > self.lVoie.index(self)+1: 
            PosDernierVehicule = self.lVoie[self.lVoie.index(self)+1].Position[self.Axe-1]             
            DimVehiculeDevant = self.lVoie[self.lVoie.index(self)+1].image.get_rect().size[self.Axe-1]            
                                            
        if(PasPremierVehicule and self.Sens*(PosDernierVehicule + DimVehiculeDevant*SensPositif - LigneStop) < 0):    
            self.stop = PosDernierVehicule + DimVehiculeDevant*SensNegatif - self.Sens*Gap  
        else:                                                                                                      
            self.stop = LigneStop - self.Sens*Gap

        
    def Mouvement(self):

        PosVehicule = self.Position[self.Axe-1]
        DimVehicule = self.image.get_rect().size[self.Axe-1]
        SensPositif = self.Sens == 1    
        SensNegatif = self.Sens == -1
        FeuxVert = self.Carrefour.Signal[self.Direction].vert
        PremierVehicule = self.lVoie[-1] == self
        LigneStop = self.Carrefour.Signal[self.Direction].LigneStop
        if len(self.lVoie) > self.lVoie.index(self)+1:
            DimVehiculeDevant = self.lVoie[self.lVoie.index(self)+1].image.get_rect().size[self.Axe-1]
            PosVehiculeDevant = self.lVoie[self.lVoie.index(self)+1].Position[self.Axe-1]
        
        self.Mouv = False
        if((self.Sens*(PosVehicule + DimVehicule*SensPositif - self.stop) <= 0 or       #Avant et sur la ligne stop           
            self.Sens*(PosVehicule + DimVehicule*SensPositif -  LigneStop) > 0 or       #Apres la ligne stop
            FeuxVert > 0) 
        and (PremierVehicule or self.Sens*(PosVehicule - PosVehiculeDevant)+ DimVehiculeDevant*SensNegatif + DimVehicule*SensPositif + Gap < 0)):
            self.Position[self.Axe-1] += self.Sens*self.Vitesse
            self.Mouv = True

        if self.Sens*(PosVehicule - LigneStop) > 0 and self.Franchi == False :
            self.Carrefour.Compteur[self.Direction] += 1
            self.Carrefour.Compteur[3] += 1
            self.Franchi = True
            if self.Mouv : listTps.append(self.Temps)
            self.Temps = 0

        if temps%pasDeTempFeux < pasDeTemps and not self.Mouv :
            self.Temps += 1

            
##            listTps.append(self.Temps)

            


    def ChangeVoie(self):

        if FonctionnementFeux == 1 and ((self.Direction == 1 and self.Voie == 0) or
                                        (self.Direction == 2 and self.Voie == 1) or
                                        (self.Direction == -1 and self.Voie == 1) or
                                        (self.Direction == -2 and self.Voie == 0)): self.Tourner = 0
            

        if self.Tourner == 1:
                   
            self.NewVoie = random.choice([0,1]) 
            self.NewDirection = (-1)**(self.Voie+1)*(self.Axe+(-1)**(self.Axe+1))        
            chemin = image + NumDirection[self.NewDirection] + "/" + self.ClasseVehicule + ".png"         
            self.NewImage = pygame.image.load(chemin)
                        
            LieuVirage = self.Carrefour.Virage[self.Direction][self.NewVoie+self.Voie*2]
            PosVoiture = self.Position[self.Axe-1]
                        
            if self.Sens*(PosVoiture - LieuVirage) >= 0:
                
                self.lVoie.remove(self)
                self.Voie = self.NewVoie
                self.Direction = self.NewDirection
                self.Axe = abs(self.Direction)
                if self.Direction < 0:
                    self.Sens = -1
                else:
                    self.Sens = 1
                self.image = self.NewImage
                #self.Surface = self.NewSurface
                self.lVoie = self.Carrefour.Vehicules[self.Direction][self.Voie]
                self.Tourner = 0

                if len(self.lVoie) == 0:
                    #lorsque la voie est vide 
                    #insert le vehicule à la dernière position ainsi il devient le premier vehicule de la voie
                    self.lVoie.append(self) 
                else:
                    VehiculeDevant = False
                    for Vehicule in self.lVoie[::-1]:  
                        PosVehiculeVoie = Vehicule.Position[self.Axe-1]
                        PosVehicule = self.Position[self.Axe-1]

                        #Sens*(self.pos - vehiculeVoie) > 0      
                        if self.Sens*(PosVehicule - PosVehiculeVoie) > 0:     
                            VehiculeDevant = True
                            self.lVoie.insert(self.lVoie.index(Vehicule)+1,self) 
                            break
                        
                    #Si le vehicule doit s'inserer en dernier         
                    if not VehiculeDevant:             
                        self.lVoie.insert(0,self)  
    

    def ChangeCarrefour(self):

        AxeVertical = abs(self.Axe) == 2
        PosVehicule = self.Position[self.Axe-1]
        LimiteCarrefourVoisin = self.Carrefour.PointsSpawn[-self.Direction][self.Voie+AxeVertical*2]
        CarrefourVoisin = self.Carrefour.Voisins[self.Direction] 

        if self.Sens*(PosVehicule - LimiteCarrefourVoisin + self.Sens*Decalage) > 0 and CarrefourVoisin != None:
            self.lVoie.remove(self)
            self.Carrefour = self.Carrefour.Voisins[self.Direction]
            self.lVoie = self.Carrefour.Vehicules[self.Direction][self.Voie]
            self.lVoie.insert(0,self)
            self.Tourner = random.choice([0,1])
            self.Franchi = False
            
            
    
    def ChangeFile(self):
        
        if self.Voie == 0 : Voisine = 1
        else : Voisine = 0
        
        Change = False

        FileVosine = self.Carrefour.Vehicules[self.Direction][Voisine]
        SensNegatif = self.Sens == -1
        VehiculeDevant = self.lVoie[self.lVoie.index(self)-1]
        if len(self.lVoie) > self.lVoie.index(self)+1:
            DimVehiculeDevant = self.lVoie[self.lVoie.index(self)+1].image.get_rect().size[self.Axe-1]
            PosVehiculeDevant = self.lVoie[self.lVoie.index(self)+1].Position[self.Axe-1]
        if len(FileVosine) > 1:
            DimVehiculeVoisin = self.Carrefour.Vehicules[self.Direction][Voisine][-1].image.get_rect().size[self.Axe-1]
            PosVehiculeVosin = self.Carrefour.Vehicules[self.Direction][Voisine][-1].Position[self.Axe-1]

        #Changer de voie si le vehicule devant est trop lent ou que la voie voisine est moins occupé                                             
        if ((len(self.lVoie) > self.lVoie.index(self)+1) and (len(FileVosine)+2 < len(self.lVoie) or self.Vitesse > VehiculeDevant.Vitesse)):
            
            Change = True

        if Change and self.Mouv:
            
            Change = False  
            self.lVoie.remove(self)
            self.lVoie = self.Carrefour.Vehicules[self.Direction][Voisine]
            
            if self.Axe == 1: 
                self.Position[1] = self.Carrefour.PointsSpawn[self.Direction][2+Voisine] #position en y qui change
            elif self.Axe == 2: 
                self.Position[0] = self.Carrefour.PointsSpawn[self.Direction][Voisine] #position en x qui change
            self.lVoie.insert(0,self)
            
                       
            
            
        # EspaceNeed = PosVehicule + DimVehicule
        # PosVehicule = self.Position[self.Axe-1]
        # DimVehicule = self.image.get_rect().size[self.Axe-1]
        #
        # for vehicule in self.Carrefour.Vehicules[self.Direction][Voisine]:
        #     DimVehiculeFile = vehicule.image.get_rect().size[self.Axe-1]
        #     PosVehiculeFile = self.Position[self.Axe-1]
        #     EspaceOwn = PosVehiculeFile + DimVehiculeFile
            
        #     DernierVehiculeFile = vehicule.lVoie[0] == vehicule
        #     PremierVehiculeFile = vehicule.lVoie[-1] == vehicule
            
        #     print(PosVehiculeFile > EspaceNeed + Gap and DernierVehiculeFile and Change)
            
        #     if PosVehiculeFile > EspaceNeed + Gap and DernierVehiculeFile and Change:
        #         Change = 0  
        #         self.lVoie.remove(self)
        #         self.Voie = Voisine
        #         self.Carrefour.Vehicules[self.Direction][self.Voie].insert(self.lVoie.index(Vehicule)+1,self)
                
        #     elif EspaceOwn + Gap < PosVehicule and PremierVehiculeFile and Change:
        #         Change = 0  
        #         self.lVoie.remove(self)
        #         self.Voie = Voisine
        #         self.Carrefour.Vehicules[self.Direction][self.Voie].insert(0,self)
                
                
                
            
        
                                
            

            
    def SeSupprime(self):
        
        PosVehicule = self.Position[self.Axe-1]
        ListeVoie = self.lVoie
        if (self.Sens*PosVehicule - Supprimer[self.Direction] > 0): 
            ListeVoie.pop()
            Simulation.remove(self)


    def __repr__(self):
        return str(self.ClasseVehicule)+" d'immatriculation "+str(self.Immatriculation)+" à la position "+str(self.Position) 

         


                    
def Repartition():
    x,y,z = random.random()*100,random.random()*100,random.random()*100    
    CV,CA,CS = ChanceVehicule,ChanceAxe,ChanceSens             
    
    if x < CV[0]: ClasseVehicule = 0
    elif x < CV[1]: ClasseVehicule = 1
    elif x < CV[2]: ClasseVehicule = 2
    elif x < CV[3]: ClasseVehicule = 3
        
    if y < CA[0]: Axe = 1 
    else: Axe = 2
        
    if z < CS[0]: Sens = 1
    else: Sens = -1
        
    return [ClasseVehicule,Axe,Sens]
        

def ChoixCarrefour(Carrefours,Axe,Sens):
    CarrefourPossible = []
    
    for carrefour in Carrefours:
        if carrefour.Voisins[-Sens*Axe] == None:
            CarrefourPossible.append(carrefour)
            
    return random.choice(CarrefourPossible)    


def InitFeux(i,LigneStop):
    
    if FonctionnementFeux == 1:
        if i == 1 or i == -1: return Feux(0,0,Vert,LigneStop[i])
        else: return Feux(Rouge,0,0,LigneStop[i])
        
    else:
        if i == 1:return Feux(0,0,Vert,LigneStop[i])
        elif i == 2:return Feux(Rouge,0,0,LigneStop[i])
        elif i == -1:return Feux(2*Rouge,0,0,LigneStop[i])
        elif i == -2:return Feux(3*Rouge,0,0,LigneStop[i])
       
          


    
class Main:

    global STOP,Immatriculation,temps,test

    if nbrCarrefour == 1:

        L,H = 800,800

        if FonctionnementFeux == 1:
            FondEcran = pygame.image.load("images/Intersection1.jpeg")
        else:
            FondEcran = pygame.image.load("images/Intersection2.jpeg")
            
        SignalRouge = pygame.image.load("images/feux/rouge.png")
        SignalOrange = pygame.image.load("images/feux/orange.png")
        SignalVert = pygame.image.load("images/feux/vert.png")
        
        CoordoFeux = {1:{0:(254,480)}, 2:{0:(288,195)}, -1:{0:(515,230)}, -2:{0:(480,515)}}
        CoordoTimer = {1:{0:(234,480)}, 2:{0:(268,195)}, -1:{0:(546,230)}, -2:{0:(511,515)}}
        CoordoCompteur = {1:{0:(234,500)}, 2:{0:(268,215)}, -1:{0:(546,250)}, -2:{0:(511,535)}}
        CoordoMaxAtt = {1:{0:(130,490)}, 2:{0:(220,290)}, -1:{0:(550,290)}, -2:{0:(490,490)}}

        #[x0,x1,y0,y1] sachant qu'il y a les voies 0 et 1
        PointsSpawn = {1:[0,0,410,445], -1:[800,800,330,370], 2:[330,370,0,0], -2:[410,445,800,800]}
        Virage = {1:[410,450,330,370], -1:[410,450,330,370], 2:[330,370,410,450], -2:[330,370,410,450]}
        Vehicules = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS = {1: 280, -1: 520, 2: 280, -2: 520}
        Signal = {1:InitFeux(1,LS), -1:InitFeux(-1,LS), 2:InitFeux(2,LS), -2:InitFeux(-2,LS)}
        Compteur = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn,Signal,Compteur,Virage,MaxAtt,Vehicules))
        
    elif nbrCarrefour == 2:

        L,H = 1400-2,800

        if FonctionnementFeux == 1:
            FondEcran = pygame.image.load("images/Double intersection1.png")
        else:
            FondEcran = pygame.image.load("images/Double intersection2.png")
            
        SignalRouge = pygame.image.load("images/feux/rouge.png")
        SignalOrange = pygame.image.load("images/feux/orange.png")
        SignalVert = pygame.image.load("images/feux/vert.png")

        CoordoFeux = {1:{0:(254,480), 1:(851,480)}, 2:{0:(288,195), 1:(885,195)}, -1:{0:(515,230), 1:(1112,230)}, -2:{0:(480,515), 1:(1077,515)}}
        CoordoTimer = {1:{0:(234,480), 1:(831,480)}, 2:{0:(268,195), 1:(865,195)}, -1:{0:(546,230), 1:(1143,230)}, -2:{0:(511,515), 1:(1108,515)}}
        CoordoCompteur = {1:{0:(234,500), 1:(831,500)}, 2:{0:(268,215), 1:(865,215)}, -1:{0:(546,250), 1:(1143,250)}, -2:{0:(511,535), 1:(1108,535)}}
        CoordoMaxAtt = {1:{0:(130,490), 1:(730,490)}, 2:{0:(220,290), 1:(820,290)}, -1:{0:(550,290), 1:(1150,290)}, -2:{0:(490,490), 1:(1090,490)}}
        
        PointsSpawn1 = {1:[0,0,410,447], -1:[700,700,328,368], 2:[328,368,0,0], -2:[410,447,800,800]}
        Virage1 = {1:[410,447,328,368], -1:[410,447,328,368], 2:[328,368,410,447], -2:[328,368,410,447]}
        Vehicules1 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS1 = {1: 280, -1: 520, 2: 280, -2: 520}
        Signal1 = {1:InitFeux(1,LS1), -1:InitFeux(-1,LS1), 2:InitFeux(2,LS1), -2:InitFeux(-2,LS1)}
        Compteur1 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt1 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn1,Signal1,Compteur1,Virage1,MaxAtt1,Vehicules1))
        
        PointsSpawn2 = {1:[700,700,410,447], -1:[1400,1400,328,368], 2:[928,968,0,0], -2:[1010,1047,800,800]}
        Virage2 = {1:[1010,1047,928,968], -1:[1010,1047,928,968], 2:[328,368,410,447], -2:[328,368,410,447]}
        Vehicules2 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS2 = {1: 880, -1: 1120, 2: 280, -2: 520}
        Signal2 = {1:InitFeux(1,LS2), -1:InitFeux(-1,LS2), 2:InitFeux(2,LS2), -2:InitFeux(-2,LS2)}
        Compteur2 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt2 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn2,Signal2,Compteur2,Virage2,MaxAtt2,Vehicules2))
        
        Carrefours[0].ajouterVoisin(1,Carrefours[1])
        Carrefours[1].ajouterVoisin(-1,Carrefours[0])
        
    elif nbrCarrefour == 4:

        L,H = 800-2,800-2
        
        if FonctionnementFeux == 1:
            FondEcran = pygame.image.load("images4C/4 intersection1.png")
        else:
            FondEcran = pygame.image.load("images4C/4 intersection2.png")
            
        SignalRouge = pygame.image.load("images4C/feux/rouge.png")
        SignalOrange = pygame.image.load("images4C/feux/orange.png")
        SignalVert = pygame.image.load("images4C/feux/vert.png")

        CoordoFeux = {1:{0:(149,275), 1:(489,275), 2:(149,615), 3:(489,615)}, 2:{0:(165,119), 1:(505,119), 2:(165,459), 3:(505,459)},
                      -1:{0:(294,135), 1:(634,135), 2:(294,475), 3:(634,475)}, -2:{0:(276,292), 1:(616,292), 2:(276,632), 3:(616,632)}}
        CoordoTimer = {1:{0:(127,275), 1:(469,275), 2:(127,615), 3:(469,615)}, 2:{0:(143,119), 1:(485,119), 2:(143,459), 3:(485,459)},
                      -1:{0:(310,135), 1:(650,135), 2:(310,475), 3:(650,475)}, -2:{0:(292,292), 1:(632,292), 2:(292,632), 3:(632,632)}}
        CoordoCompteur = {1:{0:(127,295), 1:(469,295), 2:(127,635), 3:(469,635)}, 2:{0:(143,139), 1:(485,139), 2:(143,479), 3:(485,479)},
                      -1:{0:(310,155), 1:(650,155), 2:(310,495), 3:(650,495)}, -2:{0:(292,312), 1:(632,312), 2:(292,652), 3:(632,652)}}
        CoordoMaxAtt = {1:{0:(40,275), 1:(380,275), 2:(40,615), 3:(380,615)}, 2:{0:(100,167), 1:(440,167), 2:(100,507), 3:(440,507)},
                      -1:{0:(330,167), 1:(670,167), 2:(330,507), 3:(670,507)}, -2:{0:(280,275), 1:(620,275), 2:(280,615), 3:(620,615)}}
        
        PointsSpawn1 = {1:[0,0,232,254], -1:[380,380,186,210], 2:[187,210,0,0], -2:[232,254,380,380]}
        Virage1 = {1:[232,255,187,209], -1:[232,255,187,209], 2:[187,209,232,255], -2:[187,209,232,255]}
        Vehicules1 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS1 = {1: 165, -1: 295, 2: 165, -2: 295}
        Signal1 = {1:InitFeux(1,LS1), -1:InitFeux(-1,LS1), 2:InitFeux(2,LS1), -2:InitFeux(-2,LS1)}
        Compteur1 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt1 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn1,Signal1,Compteur1,Virage1,MaxAtt1,Vehicules1))
        
        PointsSpawn2 = {1:[380,380,232,254], -1:[760,760,187,210], 2:[528,550,0,0], -2:[572,594,380,380]}
        Virage2 = {1:[574,595,528,550], -1:[574,595,528,550], 2:[187,209,232,255], -2:[187,209,232,255]}
        Vehicules2 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS2 = {1: 505, -1: 635, 2: 165, -2: 295}
        Signal2 = {1:InitFeux(1,LS2), -1:InitFeux(-1,LS2), 2:InitFeux(2,LS2), -2:InitFeux(-2,LS2)}
        Compteur2 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt2 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn2,Signal2,Compteur2,Virage2,MaxAtt2,Vehicules2))

        PointsSpawn3 = {1:[0,0,572,594], -1:[380,380,528,550], 2:[187,210,380,380], -2:[232,254,760,760]}
        Virage3 = {1:[232,255,185,209], -1:[232,255,185,209], 2:[528,550,574,595], -2:[528,550,574,595]}
        Vehicules3 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS3 = {1: 165, -1: 295, 2: 505, -2: 635}
        Signal3 = {1:InitFeux(1,LS3), -1:InitFeux(-1,LS3), 2:InitFeux(2,LS3), -2:InitFeux(-2,LS3)}
        Compteur3 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt3 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn3,Signal3,Compteur3,Virage3,MaxAtt3,Vehicules3))
        
        PointsSpawn4 = {1:[380,380,572,594], -1:[760,760,527,550], 2:[528,550,380,380], -2:[572,594,760,760]}
        Virage4 = {1:[574,595,528,550], -1:[574,595,528,550], 2:[528,550,574,595], -2:[528,550,574,595]}
        Vehicules4 = { 1: {0:[],1:[]}, -1: {0:[],1:[]}, 2: {0:[],1:[]}, -2: {0:[],1:[]} }
        LS4 = {1: 505, -1: 635, 2: 505, -2: 635}
        Signal4 = {1:InitFeux(1,LS4), -1:InitFeux(-1,LS4), 2:InitFeux(2,LS4), -2:InitFeux(-2,LS4)}
        Compteur4 = {1:0, 2:0, -1:0, -2:0, 3:0}
        MaxAtt4 = {1:0, 2:0, -1:0, -2:0}
        Carrefours.append(Carrefour(PointsSpawn4,Signal4,Compteur4,Virage4,MaxAtt4,Vehicules4))
        
        Carrefours[0].ajouterVoisin(1,Carrefours[1])
        Carrefours[0].ajouterVoisin(2,Carrefours[2])
        Carrefours[1].ajouterVoisin(-1,Carrefours[0])
        Carrefours[1].ajouterVoisin(2,Carrefours[3])
        Carrefours[2].ajouterVoisin(-2,Carrefours[0])
        Carrefours[2].ajouterVoisin(1,Carrefours[3])
        Carrefours[3].ajouterVoisin(-2,Carrefours[1])
        Carrefours[3].ajouterVoisin(-1,Carrefours[2])


    TailleEcran = (L,H)
    Police = pygame.font.Font(None, 30) #Definit la police d'écriture
    PoliceBis = pygame.font.Font(None, 20)
    PoliceBis2 = pygame.font.Font(None, 25)
    PoliceBis3 = pygame.font.Font(None, 35)
    Ecran = pygame.display.set_mode(TailleEcran)
    

    while not STOP:

        if t == Texplim:
            print("Tmax : "+str(Tmax))
            if len(listTps) != 0:
                print("Tmoy : "+str(round(sum(listTps)/len(listTps),1)))
                print("Tmed : "+str(statistics.median(listTps)))
            else:
                print("Tmoy : "+str(0.0))
                print("Tmed : "+str(0.0))
            for i in range(nbrCarrefour):
                print(Carrefours[i].Compteur[3])
            STOP = True
            pygame.quit()
            sys.exit()
            
            
        for event in pygame.event.get():

            if event.type == pygame.QUIT: #exit
                print("Tmax : "+str(Tmax))
                if len(listTps) != 0:
                    print("Tmoy : "+str(round(sum(listTps)/len(listTps),1)))
                    print("Tmed : "+str(statistics.median(listTps)))
                else:
                    print("Tmoy : "+str(0.0))
                    print("Tmed : "+str(0.0))
                for i in range(nbrCarrefour):
                    print(Carrefours[i].Compteur[3])
                STOP = True
                pygame.quit()
                sys.exit()
                
                
        Ecran.blit(FondEcran,(0,0)) #Dessine le fond d'écran
          
        
        if temps%pasDeTempFeux < pasDeTemps:
            t += 1
            for i in range(nbrCarrefour):
                for j in list(NumDirection.keys()):
                    Carrefours[i].Signal[j].vert -=1
                    Carrefours[i].Signal[j].orange -=1
                    Carrefours[i].Signal[j].rouge -=1
                    
                    if Carrefours[i].Signal[j].vert == 0:
                        Carrefours[i].Signal[j].orange = Orange
                        
                    elif Carrefours[i].Signal[j].orange == 0:
                        if FonctionnementFeux == 1:
                            Carrefours[i].Signal[j].rouge = Rouge
                        else:
                            Carrefours[i].Signal[j].rouge = 3*Rouge
                        
                    elif Carrefours[i].Signal[j].rouge == 0:
                        Carrefours[i].Signal[j].vert = Vert
        
        
        if temps%pasDeTempsInitV < pasDeTemps:  
            if use=="test":
                if test:
                    Voie,ClasseVehicule,Axe,Sens,Tourner,Immatriculation = test.pop()
                    Carrefour = ChoixCarrefour(Carrefours,Axe,Sens)
                    Vehicule(Voie, TypesVehicule[ClasseVehicule], Axe, Sens, Tourner, Carrefour, Immatriculation)

            elif use=="random": 
                    ClasseVehicule,Axe,Sens = Repartition()
                    Carrefour = ChoixCarrefour(Carrefours,Axe,Sens)
                    Tourner = random.choice([0,1])
                    Voie = random.choice([0,1])
                    Immatriculation += 1
    
                    log.insert(0,(Voie,ClasseVehicule,Axe,Sens,Tourner,Immatriculation))

                    Vehicule(Voie, TypesVehicule[ClasseVehicule], Axe, Sens, Tourner, Carrefour, Immatriculation)
                    

        for i in range(nbrCarrefour): #Changement de couleurs des feux
            for j in list(NumDirection.keys()):
                if(Carrefours[i].Signal[j].vert>0):
                    Carrefours[i].Signal[j].timer = Carrefours[i].Signal[j].vert
                    Ecran.blit(SignalVert, CoordoFeux[j][i]) #Dessine les feux sur le fond d'écran
                    
                if(Carrefours[i].Signal[j].orange>0):
                    Carrefours[i].Signal[j].timer = Carrefours[i].Signal[j].orange
                    Ecran.blit(SignalOrange, CoordoFeux[j][i])
                    
                if(Carrefours[i].Signal[j].rouge>0):
                    Carrefours[i].Signal[j].timer = Carrefours[i].Signal[j].rouge
                    Ecran.blit(SignalRouge, CoordoFeux[j][i])


        #Initialisation des timers sous forme de str
        timers = {1:[""]*nbrCarrefour, -1:[""]*nbrCarrefour, 2:[""]*nbrCarrefour, -2:[""]*nbrCarrefour}
        compteurs = {1:[""]*nbrCarrefour, -1:[""]*nbrCarrefour, 2:[""]*nbrCarrefour, -2:[""]*nbrCarrefour}
        maxAtt = {1:[""]*nbrCarrefour, -1:[""]*nbrCarrefour, 2:[""]*nbrCarrefour, -2:[""]*nbrCarrefour}
        noire = (0, 0, 0)           
        blanc = (255, 255, 255)
        color = (0, 0, 255)


        for i in range(nbrCarrefour): #Met à jour l'affichage des timers
            for j in list(NumDirection.keys()):
                #Definition de l'image correspondant au temps du timer puis dissine cette valeur
                timers[j][i] = Police.render(str(Carrefours[i].Signal[j].timer), True, blanc, noire)     
                Ecran.blit(timers[j][i],CoordoTimer[j][i])
                compteurs[j][i] = PoliceBis2.render(str(Carrefours[i].Compteur[j]), True, blanc, noire)
                Ecran.blit(compteurs[j][i],CoordoCompteur[j][i])
                if nbrCarrefour == 4: P = PoliceBis2
                else: P = Police
                maxAtt[j][i] = P.render("Tmax : "+str(Carrefours[i].MaxAtt[j]), True, blanc)
                Ecran.blit(maxAtt[j][i],CoordoMaxAtt[j][i])
                
        Ecran.blit(Police.render("Texp : "+str(t//60)+"min"+str(t%60)+"s", True, noire, blanc),(10,20))
        Ecran.blit(PoliceBis3.render("Tmax : "+str(Tmax), True, noire, blanc),(350,340))
        if len(listTps) != 0:
            Ecran.blit(PoliceBis3.render("Tmoy : "+str(round(sum(listTps)/len(listTps),1)), True, noire, blanc),(350,380))
            Ecran.blit(PoliceBis3.render("Tmed : "+str(statistics.median(listTps)), True, noire, blanc),(350,420))
        else:
            Ecran.blit(PoliceBis3.render("Tmoy : "+str(0.0), True, noire, blanc),(350,380))
            Ecran.blit(PoliceBis3.render("Tmed : "+str(0.0), True, noire, blanc),(350,420))


        for vehicule in Simulation: #Réalise les actions des véhicules (et les supprime)

            Ecran.blit(vehicule.image, vehicule.Position)
            if vehicule.Temps > Tmax:
                Tmax = vehicule.Temps
            if vehicule.Temps > vehicule.Carrefour.MaxAtt[vehicule.Direction]:
                vehicule.Carrefour.MaxAtt[vehicule.Direction] = vehicule.Temps
            vehicule.CalculStop()
            vehicule.Mouvement()
            vehicule.ChangeCarrefour()
            vehicule.ChangeVoie()
            #vehicule.ChangeFile()
            vehicule.SeSupprime()
             

            
        pygame.display.update()  #MAJ de tout l'écran

        
        time.sleep(pasDeTemps)  #Création d'un pas de temps
        temps += pasDeTemps


Main()  #Execute
