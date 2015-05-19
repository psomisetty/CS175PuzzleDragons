import time
import random
import math
class BlackGarden:
    def __init__(self, width=6, height=5, movesInUnit=9,
                 Damage=[0,0,0,0,0], ATK=[1,1,1,1,1],
                 Classes=["\033[91mF \033[0m", "\033[94mW \033[0m", "\033[92mE \033[0m", "\033[93mL \033[0m","\033[95mD \033[0m","\033[0mH "],
                 ElementNames=["Fire","Water","Earth","Light","Dark","Heal"],
                 RCV=1, H_P=50, MAX_HP=100, humanSwaps=20,
                 HEURISTIC_CHOICE=0, mseCutoff=0.85,
                 mseRunTillPerfect=1, UseAStar=0, Avgs=[]):

        self.width=width
        self.height=height
        self.movesInUnit=9
        self.Damage=Damage
        self.ATK=ATK
        self.MassAttack = []
        self.FinMassAttack = []
        for i in range(0,len(Classes)):
            self.MassAttack.append(0)
            self.FinMassAttack.append(0)
        self.Classes=Classes
        self.ElementNames=ElementNames
        self.RCV=RCV
        self.H_P=H_P
        self.MAX_HP=MAX_HP
        self.humanSwaps=humanSwaps
        #How many swaps is reasonable for one turn.
        self.HEURISTIC_CHOICE=HEURISTIC_CHOICE
        #0 for matches of 3
        #1 for clustering
        self.mseCutoff=mseCutoff
        #What mean squared error is acceptable.
        self.mseRunTillPerfect=mseRunTillPerfect
        #Boolean that determines whether the clustering heuristic will run as long as it deems necessary.
        self.UseAStar=UseAStar
        #Boolean that determines whether the building of the tree will use A* search.
        self.Avgs=Avgs
        #Empty list of average coordinates for each orb class. It is changed by functions.
    def populate(self,Board):
       for i in range(0,self.height):
           for j in range(0,self.width):
               if(Board[i][j]=='. '):
                   r = random.randint(0,len(self.Classes)-1)
                   Board[i][j]=self.Classes[r]
    def boardInit(self,Board,toClearX,toClearY):
        Board = [[]]
        for i in range(0,self.height):
            Board.append([])
            for j in range(0,self.width):
                Board[i].append(". ")
        self.populate(Board)
        while(self.isMatch(Board,toClearX,toClearY)):
            self.consecutiveClear(Board,toClearX,toClearY)
        return Board
    def swap(self,Board,x1,y1,x2,y2):
       C=Board[x1][y1]
       Board[x1][y1]=Board[x2][y2]
       Board[x2][y2]=C
    def printBoard(self,Board):
       for i in range(0,self.height):
           ends=""
           for j in range(0,self.width):
               if Board[i][j] in self.Classes:
                   print(Board[i][j],end="")
               else:
                   print(". ",end="")
           if self.HEURISTIC_CHOICE==1:
               BCopy=[]
               for k in range(0,self.height):
                   BCopy.append([])
                   for j in range(0,self.width):
                       BCopy[k].append(". ")
               for k in range(0,len(self.Avgs)):
                   BCopy[int(self.Avgs[k][0])][int(self.Avgs[k][1])]=self.Classes[k]
               if i==0:
                   print(" >-MEANS-> ",end="")
               else:
                   print("           ",end="")
               for k in range(0,self.width):
                   print(BCopy[i][k],end="")
           print(ends)
       print()
    def isMassAttack(self,Board,toClearX,toClearY,Final):
       if Final==1:
           for i in range(0,len(self.FinMassAttack)-1):
               self.FinMassAttack[i]+=self.MassAttack[i]
       for i in range(0,len(self.MassAttack)): self.MassAttack[i]=0
       for i in range(0,len(toClearX)-1):
           for j in range(i+1,len(toClearX)):
               if toClearX[i]==-1:
                   break
               if toClearX[i]==toClearX[j] and toClearY[i]==toClearY[j]:
                   Element=Board[toClearX[j]][toClearY[i]]
                   for q in range(0,len(self.Classes)-1):
                       if Element==self.Classes[q]:
                           self.MassAttack[q]=1
       return
    def isMatch(self,Board,toClearX,toClearY,Final=0):
       for i in range(0,128):
           toClearX[i]=-1
           toClearY[i]=-1
       isMatch=0
       for i in range(0,self.height):
           for j in range(0,self.width):
               if Board[i][j]!='. ':
                   if i<=self.height-3:
                       if Board[i][j]==Board[i+1][j]:
                           if Board[i][j]==Board[i+2][j]:
                               for F in range(0,128):
                                   if toClearX[F]==-1:
                                       toClearX[F]=i
                                       toClearX[F+1]=i+1
                                       toClearX[F+2]=i+2
                                       toClearX[F+3]=-1
                                       toClearY[F]=j
                                       toClearY[F+1]=j
                                       toClearY[F+2]=j
                                       toClearY[F+3]=-1
                                       break
                               isMatch=1
               if Board[i][j]!='. ':
                   if j<=self.width-3:
                       if Board[i][j]==Board[i][j+1]:
                           if Board[i][j]==Board[i][j+2]:
                               for F in range(0,128):
                                   if toClearX[F]==-1:
                                       toClearX[F]=i
                                       toClearX[F+1]=i
                                       toClearX[F+2]=i
                                       toClearX[F+3]=-1
                                       toClearY[F]=j
                                       toClearY[F+1]=j+1
                                       toClearY[F+2]=j+2
                                       toClearY[F+3]=-1
                                       break
                               isMatch=1
       self.isMassAttack(Board,toClearX,toClearY,Final)
       return isMatch
    def clusterHeuristic(self,Board,toClearX,toClearY,path=""):
       self.isMatch(Board,toClearX,toClearY)
       ElemCoords=[[] for i in range(0,len(self.Classes))]
       self.Avgs=[]
       for i in range(0,self.height):
           for j in range(0,self.width):
               for q in range(0,len(self.Classes)):
                   if Board[i][j]==self.Classes[q]:
                       ElemCoords[q].append([i,j])
       for i in range(0,len(self.Classes)):
           regx=0
           regy=0
           for j in range(0,len(ElemCoords[i])):
               regx+=ElemCoords[i][j][0]
               regy+=ElemCoords[i][j][1]
           if len(ElemCoords[i])>0:
               regx/=len(ElemCoords[i])
               regy/=len(ElemCoords[i])
           self.Avgs.append([regx,regy])
       squared_error = []
       for i in range(0,self.height):
           for j in range(0,self.width):
               for q in range(0,len(self.Classes)):
                   if Board[i][j]==self.Classes[q]:
                       squared_error.append(math.sqrt((self.Avgs[q][0]-i)**2+(self.Avgs[q][1]-j)**2))
       mse = sum(squared_error)/len(squared_error)
       mse*=-1
       if self.mseRunTillPerfect==0:
           mse+=len(path)/150
       if mse>-self.mseCutoff:
           return 100
       return mse
    def heuristic(self,Board,toClearX,toClearY,path=""):
       ret=0
       self.isMatch(Board,toClearX,toClearY)
       BCopy=[[]]
       for i in range(0,self.height):
           BCopy.append([])
           for j in range(0,self.width):
               BCopy[i].append(Board[i][j])
       for F in range(0,len(toClearX)):
           if toClearX[F]!=-1:
               if BCopy[toClearX[F]][toClearY[F]]!='. ':
                   Element=BCopy[toClearX[F]][toClearY[F]]
                   Health_Good=int(sum(self.ATK)/len(self.ATK))
                   for q in range(0,len(self.Classes)-1):
                       if Element==self.Classes[q]:
                           ret+=self.ATK[q]
                   if Element==self.Classes[-1]:
                       ret+=Health_Good
                       if self.H_P<self.MAX_HP:
                           ret+=1
                   BCopy[toClearX[F]][toClearY[F]]='. '
               toClearX[F]=-1
               toClearY[F]=-1
           else:
               break
       if len(path)>20:
           ret-=int((int(sum(self.ATK)/len(self.ATK))*(len(path)-self.humanSwaps)/4))
       return ret
    def orbsFall(self,Board):
       for k in range(1,self.height):
           for i in range(1,self.height):
               for j in range(0,self.width):
                   if Board[i][j]=='. ':
                       self.swap(Board,i,j,i-1,j)
    def matchOrbs(self,Board,toClearX,toClearY):
       ret = self.isMatch(Board,toClearX,toClearY)
       if ret:
           for i in range(128):
               if toClearX[i]==-1:
                   break
               else:
                   Element=Board[toClearX[i]][toClearY[i]]
                   for q in range(0,len(self.Classes)-1):
                       if Element==self.Classes[q]:
                           self.Damage[q]+=self.ATK[q]
                   if Element==self.Classes[-1]:
                       self.H_P+=self.RCV
                       if self.H_P>self.MAX_HP:
                           self.H_P=self.MAX_HP
                   Board[toClearX[i]][toClearY[i]]='. '
       return ret
    def printCube(self,Cube):
        for i in range(0,len(Cube)):
            print("".join(str(Cube[i][0])),end="")
            for j in range(len(Cube[i][0]),self.width):
                print("  ",end="")
            print("     ",end="")
        print()
        for i in range(0,len(Cube)):
            print("(",Cube[i][2],",",Cube[i][3],")",end="")
            for j in range(4,self.width):
                print("  ",end="")
            print("   ",end="")
        print()
        for i in range(0,self.height):
            for k in range(0,len(Cube)):
                for j in range(0,self.width):
                    print(Cube[k][1][i][j],end="")
                print("    ",end="")
            print("\033[0m")
        print()
    def consecutiveClear(self,Board,toClearX,toClearY):
       #self.printBoard(Board)
       self.matchOrbs(Board,toClearX,toClearY)
       time.sleep(0.5)
       #self.printBoard(Board)
       self.orbsFall(Board)
       time.sleep(0.5)
       #self.printBoard(Board)
       self.populate(Board)
       time.sleep(0.5)
       #self.printBoard(Board)
       time.sleep(0.5)
    def startNode(self,Board,CX,CY,toClearX,toClearY):
       switchBoard=[[]]
       for i in range(0,self.height):
           switchBoard.append([])
           for j in range(0,self.width):
               switchBoard[i].append(0)
       for i in range(0,self.height-1):
           for j in range(0,self.width):
               self.swap(Board,i,j,i+1,j)
               if self.HEURISTIC_CHOICE==0:
                   switchBoard[i][j]+=self.heuristic(Board,toClearX,toClearY)
               elif self.HEURISTIC_CHOICE==1:
                   switchBoard[i][j]+=self.clusterHeuristic(Board,toClearX,toClearY)
               self.swap(Board,i,j,i+1,j)
       for i in range(0,self.height):
           for j in range(0,self.width-1):
               self.swap(Board,i,j,i,j+1)
               if self.HEURISTIC_CHOICE==0:
                   switchBoard[i][j]+=self.heuristic(Board,toClearX,toClearY)
               elif self.HEURISTIC_CHOICE==1:
                   switchBoard[i][j]+=self.clusterHeuristic(Board,toClearX,toClearY)
               self.swap(Board,i,j,i,j+1)
       for i in range(1,self.height):
           for j in range(0,self.width):
               self.swap(Board,i,j,i-1,j)
               if self.HEURISTIC_CHOICE==0:
                   switchBoard[i][j]+self.heuristic(Board,toClearX,toClearY)
               elif self.HEURISTIC_CHOICE==1:
                   switchBoard[i][j]+=self.clusterHeuristic(Board,toClearX,toClearY)
               self.swap(Board,i,j,i-1,j)
       for i in range(0,self.height):
           for j in range(1,self.width):
               self.swap(Board,i,j,i,j-1)
               if self.HEURISTIC_CHOICE==0:
                   switchBoard[i][j]+=self.heuristic(Board,toClearX,toClearY)
               elif self.HEURISTIC_CHOICE==1:
                   switchBoard[i][j]+=self.clusterHeuristic(Board,toClearX,toClearY)
               self.swap(Board,i,j,i,j-1)
       maximum=0
       for i in range(0,self.height):
           for j in range(0,self.width):
               if switchBoard[i][j]>maximum:
                   CX=i
                   CY=j
                   maximum=switchBoard[i][j]
       return (CX,CY)
    def maxIndex(self,Cube,toClearX,toClearY,BPath):
       k=0
       if self.HEURISTIC_CHOICE==0:
           max=self.heuristic(Cube[0][1],toClearX,toClearY,BPath+Cube[0][0])
       elif self.HEURISTIC_CHOICE==1:
           max=self.clusterHeuristic(Cube[0][1],toClearX,toClearY,BPath+Cube[0][0])
       for i in range(0,len(Cube)):
           if self.HEURISTIC_CHOICE==0:
               holder=self.heuristic(Cube[i][1],toClearX,toClearY,BPath+Cube[i][0])
           elif self.HEURISTIC_CHOICE==1:
               holder=self.clusterHeuristic(Cube[i][1],toClearX,toClearY,BPath+Cube[i][0])
           if holder>max:
               max=holder
               k=i
       return k
    def appendMatrix(self,Cube,Board,counter,CurX,CurY):
       Cube.append(["",[],0,0])
       for i in range(0,self.height):
           Cube[counter][1].append([])
           for j in range(0,self.width):
               Cube[counter][1][i].append(Board[i][j])
       Cube[counter][2]=CurX
       Cube[counter][3]=CurY
       return
    def cubeInit(self,Cube,Board,CurX,CurY,Prev="N"):
       counter=0
       if CurX<self.height-1 and Prev!="U":
           self.appendMatrix(Cube,Board,counter,CurX+1,CurY)
           self.swap(Cube[counter][1],CurX,CurY,CurX+1,CurY)
           Cube[counter][0]+="D"
           counter+=1
       if CurX>0 and Prev!="D":
           self.appendMatrix(Cube,Board,counter,CurX-1,CurY)
           self.swap(Cube[counter][1],CurX,CurY,CurX-1,CurY)
           Cube[counter][0]+="U"
           counter+=1
       if(CurY>0) and Prev!="R":
           self.appendMatrix(Cube,Board,counter,CurX,CurY-1)
           self.swap(Cube[counter][1],CurX,CurY,CurX,CurY-1)
           Cube[counter][0]+="L"
           counter+=1
       if(CurY<self.width-1) and Prev!="L":
           self.appendMatrix(Cube,Board,counter,CurX,CurY+1)
           self.swap(Cube[counter][1],CurX,CurY,CurX,CurY+1)
           Cube[counter][0]+="R"
           counter+=1
    def cubeNext(self,Cube):
       TempCube=[]
       for q in range(0,len(Cube)):
           if len(Cube[q][0])==len(Cube[-1][0]):
               C1=[]
               regis=Cube[q]
               tempX=Cube[q][2]
               tempY=Cube[q][3]
               self.cubeInit(C1,regis[1],tempX,tempY,regis[0][-1])
               for i in range(0,len(C1)):
                   C1[i][0]=regis[0]+C1[i][0]
                   TempCube.append(C1[i])
       for i in range(0,len(TempCube)):
           Cube.append(TempCube[i])
    def cubeNextAStar(self,Cube,toClearX,toClearY,BPath):
        TempCube=[i for i in Cube]
        del TempCube[0]
        Max=self.maxIndex(TempCube,toClearX,toClearY,BPath)+1
        Best=Cube[Max]
        if self.HEURISTIC_CHOICE==0:
            if self.heuristic(Cube[Max][1],toClearX,toClearY,Cube[Max][0])>self.heuristic(Cube[0][1],toClearX,toClearY,Cube[0][0]):
                Cube[0]=Cube[Max]
        else:
            if self.clusterHeuristic(Cube[Max][1],toClearX,toClearY,Cube[Max][0])>self.clusterHeuristic(Cube[0][1],toClearX,toClearY,Cube[0][0]):
                Cube[0]=Cube[Max]
        C1=[]
        self.cubeInit(C1,Cube[Max][1],Cube[Max][2],Cube[Max][3],Cube[Max][0][-1])
        for i in range(0,len(C1)):
            C1[i][0]=Cube[Max][0]+C1[i][0]
            Cube.append(C1[i])
        del Cube[Max]
    def incrementalReadout(self,BPath,Orig,OX,OY):
       print("Optimal path: ",BPath)
       self.printBoard(Orig)
       for i in range(0,len(BPath)):
           if BPath[i]=="D":
               self.swap(Orig,OX,OY,OX+1,OY)
               OX+=1
           elif BPath[i]=="U":
               self.swap(Orig,OX,OY,OX-1,OY)
               OX-=1
           elif BPath[i]=="R":
               self.swap(Orig,OX,OY,OX,OY+1)
               OY+=1
           elif BPath[i]=="L":
               self.swap(Orig,OX,OY,OX,OY-1)
               OY-=1
           if self.HEURISTIC_CHOICE==0:
               time.sleep(0.25)
           elif self.HEURISTIC_CHOICE==1:
               time.sleep(0.0625)
           self.printBoard(Orig)
       return Orig
    def cubeLoop(self,Board,CurX,CurY,BPath):
       while 1:
           Cube=[]
           self.cubeInit(Cube,Board,CurX,CurY)
           if self.UseAStar==1:
               Cube.insert(0,Cube[0])
           for i in range(0,self.movesInUnit):
               if self.UseAStar==0:
                   self.cubeNext(Cube)
               else:
                   for j in range(0,3**i):
                       self.cubeNextAStar(Cube,toClearX,toClearY,BPath)
                       if len(Cube)>256:
                           print("Migrating starting node to new optimum...")
                           break
           if self.UseAStar==0:
               Max = self.maxIndex(Cube,toClearX,toClearY,BPath)
           else:
               Max = 0
           Best = Cube[Max]
           # if self.HEURISTIC_CHOICE==0:
           #     print("Best board updated. New heuristic: "+str(self.heuristic(Cube[Max][1],toClearX,toClearY,BPath+Cube[Max][0])))
           # elif self.HEURISTIC_CHOICE==1:
           #     print("Best board updated. New heuristic: "+str(self.clusterHeuristic(Cube[Max][1],toClearX,toClearY,BPath+Cube[Max][0])))
           #     print("PATH: ",BPath+Cube[Max][0])
           #     self.printBoard(Cube[Max][1])
           BPath+=Best[0]
           for i in range(0,len(Best[0])):
               if Best[0][i]=="D": CurX+=1
               if Best[0][i]=="U": CurX-=1
               if Best[0][i]=="R": CurY+=1
               if Best[0][i]=="L": CurY-=1
           if(Board==Best[1]):
               break
           if self.HEURISTIC_CHOICE==0:
               if(self.heuristic(Board,toClearX,toClearY)==self.heuristic(Best[1],toClearX,toClearY,BPath+Best[0])):
                   break
           elif self.HEURISTIC_CHOICE==1:
               if(self.clusterHeuristic(Board,toClearX,toClearY)==self.clusterHeuristic(Best[1],toClearX,toClearY,BPath+Best[0])):
                   break
           Board=Best[1]
       return (BPath,Board)
    def makeMove(self,Board,CurX,CurY,toClearX,toClearY):
       self.Damage=[0,0,0,0,0]
       (CurX,CurY)=self.startNode(Board,CurX,CurY,toClearX,toClearY)
       #print("Starting at (",CurX,",",CurY,")")
       Orig=Board
       OX=CurX
       OY=CurY
       BPath=""
       (BPath,Board)=self.cubeLoop(Board,CurX,CurY,BPath)
       #Board=self.incrementalReadout(BPath,Orig,OX,OY)
       matchedBoard=Board
       while(self.isMatch(Board,toClearX,toClearY,1)):
           self.consecutiveClear(Board,toClearX,toClearY)
       print("Health: "+str(self.H_P)+"\nDamage dealt:")
       for i in range(0,len(self.Classes)-1):
           print("\t"+str(self.Damage[i])+" "+self.ElementNames[i]+(" Mass" if self.FinMassAttack[i]>=1 else ""))
       for i in range(0, len(self.Damage)): self.Damage[i]=0
       self.HEURISTIC_CHOICE=0
       return Board,BPath,matchedBoard
# -------------------- MAIN --------------------
if __name__ == "__main__":
    #quick test
    CurX=0
    CurY=0
    Board = [[]]
    toClearX = []
    toClearY = []
    game = BlackGarden(HEURISTIC_CHOICE=0,UseAStar=0)
    # I advise against implementing HEURISTIC_CHOICE=1 and UseAStar=1 at the same time, under the simple logic that
    # a human brain (UseAStar) cannot easily implement a clustering algorithm (HEURISTIC_CHOICE=1) unless severe
    # lookahead is used, so the machine ends up with bad short-term results.
    for i in range(0,128):
       toClearX.append(-1)
       toClearY.append(-1)
    Board=game.boardInit(Board,toClearX,toClearY)
    game.printBoard(Board)
    (Board,BPath,matchedBoard)=game.makeMove(Board,CurX,CurY,toClearX,toClearY)
    game.printBoard(matchedBoard)
    game.printBoard(Board)