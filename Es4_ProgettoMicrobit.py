from turtle import width
import pygame
import time
import random
from threading import Thread,Lock
import threading, queue
import serial 
import keyboard
 
pygame.init() #faccio partire pygame
lock = Lock() #utilizzo il Lock per il thread del microbit, sincronizzo i thread con race condition
 
white = (255, 255, 255) #inizializzo i vari colori che mi servono per il videogioco
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
 
dis_width = 1400 #setto le dimensioni dello schermo
dis_height = 800
 
dis = pygame.display.set_mode((dis_width, dis_height)) #a pygame assegno le dimensioni della schermata
pygame.display.set_caption('Snake di Galieti Marco')#do il nome alla finestra di pygame
#serpente = pygame.image.load("serpente.png")
inizio = pygame.image.load("inizio2.png") #schermata iniziale
iniziorect = inizio.get_rect()
istruzioni = pygame.image.load("istruzioni.png")#istruzioni del gioco
istrurect = istruzioni.get_rect()
fill = pygame.image.load('sfondo.png')#sfondo del videogioco
dis.blit(fill, [0,0])
#snakerect = serpente.get_rect()
 
clock = pygame.time.Clock()#utilizzo il modulo time di pygame per i vari delay
 
snake_velocita = 10 #velocita e dimensione del serpente 
snake_blocco = 20
 
font_style = pygame.font.SysFont("bahnschrift", 25) #font del punteggio
punteggio_font = pygame.font.SysFont("comicsansms", 100)

q = queue.Queue() #coda dove inserisco i dati letti da microbit tramite seriale

class Read_Microbit(threading.Thread): #thread per leggere i dati del microbit da seriale
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True
      
    def terminate(self):
        self._running = False
        
    def run(self):
        #serial config
        port = "COM9" #do a port il nome della porta seriale utilizzata
        s = serial.Serial(port) #assegno ad s la lettura seriale della porta
        s.baudrate = 115200 #numero di informazioni che leggo dal seriale
        while self._running:
            data = s.readline().decode() #decode della stampa di microbit 
            q.put(data) #metto la stampa di microbit dentro data e poi dentro la coda
            #time.sleep(0.01)
            
def tuo_punteggio(punteggio): #funzione per visualizzare il punteggio dello snake
    valore = punteggio_font.render(str(punteggio), True, black) 
    punteggio = pygame.image.load('score.png')
    dis.blit(punteggio, [10, 25])
    dis.blit(valore,[450,10])
    pygame.display.flip()
 
 
def nostro_snake(snake_blocco, snake_list): #disegno del serpente rettangolo 
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_blocco, snake_blocco])


def gameLoop():
    game_over = False #metto le due variabili di chiusura del gioco a false per iniziare
    game_close = False
 
    x1 = dis_width / 2 #setto la x e la y in centro dove poi spuntera il serpente
    y1 = dis_height / 2
 
    x1_variazione = 0 #inizializzo la variazione delle variabili x ed y a 0
    y1_variazione = 0
 
    snake_List = [] #
    lunghezza_snake = 1 #lunghezza iniziale del serpente
 
    cibox = round(random.randrange(0, dis_width - snake_blocco) / 20) * 20 #cibo del serpente, quadrati da mangiare
    ciboy = round(random.randrange(100, dis_height - snake_blocco) / 20) * 20
    tasto = "x" #inizializzo il tasto a x per il menu

    if tasto == "x": #entra sempre all'inizio 
        while keyboard.is_pressed("x") == False:
            dis.blit(inizio, iniziorect)
            pygame.display.flip()
        tasto = "r"
        time.sleep(0.5)
    elif tasto == "r": #se il tasto è uguale a r entro nelle istruzioni
        while keyboard.is_pressed("y") == False:
            dis.blit(istruzioni, istrurect)
            pygame.display.flip()
        tasto = "m"

    time.sleep(0.2)
    rm = Read_Microbit()
    rm.start()
    
    while not game_over:
        while game_close == True:
            fine = pygame.image.load("gameover.gif")
            finerect = fine.get_rect()
            dis.blit(fine, finerect)
            #tuo_punteggio(lunghezza_snake - 1)
            pygame.display.update()
 
            for event in pygame.event.get():#registro gli eventi e se premo q esco dal gioco c continuo a giocare
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: #se è uguale a q chiudo gioco e thread
                        game_over = True
                        game_close = False
                        rm.terminate()
                        rm.join
                    if event.key == pygame.K_c: #se continuo chiudo comunque il thread per non inviare altri dati e poi richiamo il gameloop
                        rm.terminate()
                        rm.join()
                        time.sleep(0.5)
                        gameLoop()

        data = q.get() #prendo dalla queue il data
        print(data[:-1]) #lo stampo per conferma
        '''for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                '''
        #if event.key == pygame.K_LEFT:
        if data[:-1] == "SINISTRA": #prendo in data tutto apparte l'ultimo carattere che è \n
            x1_variazione = -snake_blocco #modifico la x invertendo il serpente
            y1_variazione = 0 #essendo un movimento in orizzontale non cambio la y
        #elif event.key == pygame.K_RIGHT:
        elif data[:-1] == "DESTRA":
            x1_variazione = snake_blocco
            y1_variazione = 0
        #elif event.key == pygame.K_UP:
        elif data[:-1] == "SU":
            y1_variazione = -snake_blocco
            x1_variazione = 0
        #elif event.key == pygame.K_DOWN:
        elif data[:-1] == "GIU":
            y1_variazione = snake_blocco
            x1_variazione = 0
 
        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0: #barriere del gioco
            game_close = True
        x1 += x1_variazione #aggiungo alla x e alla y del serpente la sua variazione
        y1 += y1_variazione
        fill = pygame.image.load('sfondo.png') #inserisco l'immagine di sfondo
        dis.blit(fill, [0,0])
        pygame.draw.rect(dis, red, [cibox, ciboy, snake_blocco, snake_blocco])
        snake_testa = [] #list della testa del serpente
        snake_testa.append(x1) #aggiungo alla lista la x e la y del serpente
        snake_testa.append(y1)
        snake_List.append(snake_testa) #alla lista principale aggiungo quella del serpente
        if len(snake_List) > lunghezza_snake: #se il numero di elementi della lista è superiore rispetto alla lunghezza del serpente elimino il primo elemento 
            del snake_List[0]
 
        for x in snake_List[:-1]: 
            if x == snake_testa:
                game_close = True
 
        nostro_snake(snake_blocco, snake_List)
        #dis.blit(serpente, [x1,y1])
        tuo_punteggio(lunghezza_snake - 1)
 
        pygame.display.update()
 
        if x1 == cibox and y1 == ciboy:
            cibox = round(random.randrange(0, dis_width - snake_blocco) / 20) * 20
            ciboy = round(random.randrange(0, dis_height - snake_blocco) / 20) * 20
            lunghezza_snake += 1
 
        clock.tick(snake_velocita)

    rm.terminate()
    rm.join()
    
    pygame.quit()
    quit()
gameLoop()