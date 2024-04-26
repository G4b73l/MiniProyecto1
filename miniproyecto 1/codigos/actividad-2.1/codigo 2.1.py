import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
import matplotlib.animation as animation
from PyQt6.QtCore import QTimer
import serial
import time

# Configuración del puerto serial
puerto_serial = serial.Serial('COM5', 9600)  # Cambia 'COM5' al puerto en el que está conectado tu Arduino

def enviar_celdas_vivas():
    # Contar células vivas
    celdas_vivas = np.sum(grid)
    print("Enviando celdas vivas:", celdas_vivas)
    # Enviar la cantidad de células vivas al Arduino
    if celdas_vivas>= 1000:
        puerto_serial.write(b'E')
    elif celdas_vivas <1000 and celdas_vivas>=500:
        puerto_serial.write(b'S')
    else :
        puerto_serial.write(b'A')
def reset_game():
    global grid
    N = 100  # Tamaño de la grilla NxN
    grid = np.random.choice([0, 1], N * N, p=[0.8, 0.2]).reshape(N, N)  # Inicialización aleatoria

def update(frame, img, grid, live_cells_text):
    # Definimos el kernel: todos los vecinos cuentan igual, la celda central no se cuenta
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    # Usamos convolve2d para aplicar el kernel a la grilla, considerando condiciones de frontera periódicas
    convolved = convolve2d(grid, kernel, mode='same', boundary='wrap')
    # Aplicamos las reglas del Juego de la Vida de Conway
    birth = (convolved == 3) & (grid == 0)  # Una célula muerta con exactamente 3 vecinos vivos "nace"
    survive = ((convolved == 2) | (convolved == 3)) & (grid == 1)  # Una célula viva con 2 o 3 vecinos vivos sobrevive
    grid[:, :] = 0  # Primero, seteamos todas las células a "muertas"
    grid[birth | survive] = 1  # Luego, actualizamos las células que deben "nacer" o sobrevivir
    
    # Actualizamos la imagen con el nuevo estado
    img.set_data(grid)
    # Actualizamos el texto con la cantidad de células vivas
    live_cells_text.set_text(f'Live Cells: {np.sum(grid)}')

    return img, live_cells_text

# Configuración inicial
N = 100  # Tamaño de la grilla NxN
grid = np.random.choice([0, 1], N * N, p=[0.8, 0.2]).reshape(N, N)  # Inicialización aleatoria

# Configuración de la visualización
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest')
live_cells_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)

# Definimos la función que actualizará la animación
def update_animation():
    update(0, img, grid, live_cells_text)
    plt.pause(0.1)  # Pausa para controlar la velocidad de la animación
    
    # Leer datos del puerto serial de manera no bloqueante
    while puerto_serial.in_waiting > 0:
        mensaje = puerto_serial.readline().decode().strip()
        if mensaje == "Reiniciar":
            print("Reiniciar")
            reset_game()
        else:
            pass

# Creamos un QTimer para controlar la velocidad de la animación y enviar la cantidad de células vivas cada 10 segundos
timer = QTimer()
timer.timeout.connect(update_animation)
timer.start(200)  # Intervalo de actualización inicial: 10 segundos

timer2 = QTimer()
timer2.timeout.connect(enviar_celdas_vivas)
timer2.start(1000)  # Intervalo de actualización inicial: 10 segundos


plt.show()