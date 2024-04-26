import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from matplotlib.widgets import Button
from PyQt6.QtCore import QTimer
import serial
from playsound import playsound

# Configuración del puerto serial
puerto_serial = serial.Serial('COM5', 9600)  # Cambia 'COM5' al puerto en el que está conectado tu Arduino

def enviar_celdas_vivas(): 
    # Contar células vivas
    celdas_vivas = np.sum(grid)
    print("Enviando celdas vivas:", celdas_vivas)
    # Enviar la cantidad de células vivas al Arduino
    if celdas_vivas >= 5000:
        puerto_serial.write(b'E')
    elif 5000 > celdas_vivas >= 3000:
        puerto_serial.write(b'S')
    else:
        puerto_serial.write(b'A')

def reset_game(event):
    global grid, vida
    N = 100  # Tamaño de la grilla NxN
    grid = np.random.choice([0, 1], N * N, p=[0.8, 0.2]).reshape(N, N)  # Inicialización aleatoria
    vida = np.zeros((N, N), dtype=int)  # Inicializar matriz de vida

def nuke(event=None):
    global grid
    # Generar posición aleatoria dentro de la grilla
    random_row = np.random.randint(10, N - 10)  # Rango para evitar los bordes
    random_col = np.random.randint(10, N - 10)

    # Establecer las células dentro de un rango de 21x21 alrededor de la posición aleatoria como muertas
    grid[random_row - 10:random_row + 11, random_col - 10:random_col + 11] = 0

    # Actualizar la visualización
    img.set_data(grid)
    plt.draw()

def heal(event=None):
    global grid, vida
    # Generar posición aleatoria dentro de la grilla
    random_row = np.random.randint(10, N - 10)  # Rango para evitar los bordes
    random_col = np.random.randint(10, N - 10)

    # Rebanadas para el rango dentro del cual operar
    row_slice = slice(random_row - 10, random_row + 11)
    col_slice = slice(random_col - 10, random_col + 11)

    # Revivir las células muertas dentro del rango con 70 puntos de vida
    grid[row_slice, col_slice][grid[row_slice, col_slice] == 0] = 1
    vida_increment = 50
    vida[row_slice, col_slice][grid[row_slice, col_slice] == 1] += vida_increment

    # Limitar la vida máxima a 100 puntos
    vida[vida > 100] = 100

    # Actualizar la visualización
    img.set_data(grid)
    plt.draw()


def update(frame, img, grid, live_cells_text):
    global vida
    # Definimos el kernel: todos los vecinos cuentan igual, la celda central no se cuenta
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    # Usamos convolve2d para aplicar el kernel a la grilla, considerando condiciones de frontera periódicas
    convolved = convolve2d(grid, kernel, mode='same', boundary='wrap')
    
    # Aplicamos las reglas del Juego de la Vida de Conway
    birth = (convolved == 3) & (grid == 0)  # Una célula muerta con exactamente 3 vecinos vivos "nace"
    survive = ((convolved == 2) | (convolved == 3)) & (grid == 1)  # Una célula viva con 2 o 3 vecinos vivos sobrevive
    
    # Aplicar reglas adicionales
    for i in range(N):
        for j in range(N):
            if grid[i, j] == 1:  # Si la célula está viva
                vecinos_vivos = convolved[i, j] - 1  # Restar 1 para excluir la propia célula
                if vecinos_vivos < 2 or vecinos_vivos > 3:  # Menos de 2 o más de 3 vecinos vivos
                    vida[i, j] -= 30  # Reducir la vida en 30 puntos
            elif convolved[i, j] == 3:  # Si la célula está muerta y tiene exactamente 3 vecinos vivos
                grid[i, j] = 1  # Renacer
                vida[i, j] = 100  # Establecer la vida en 100 puntos

    # Actualizamos la vida de las células
    grid[vida <= 0] = 0  # Células con vida menor o igual a 0 mueren
    vida[grid == 1] -= 1  # Reducir la vida de las células vivas

    # Verificar si todas las células han muerto
    if np.sum(grid) == 0:
        playsound('C:/Users/ivanr/Documents/tic/defeat.mp3') 
        reset_game(None)
    # Actualizamos la imagen con el nuevo estado
    img.set_data(grid)
    # Actualizamos el texto con la cantidad de células vivas
    live_cells_text.set_text(f'Live Cells: {np.sum(grid)}')

    return img, live_cells_text

# Configuración inicial
N = 100  # Tamaño de la grilla NxN
grid = np.random.choice([0, 1], N * N, p=[0.8, 0.2]).reshape(N, N)  # Inicialización aleatoria
vida = np.zeros((N, N), dtype=int)  # Inicializar matriz de vida

# Configuración de la visualización
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest')
live_cells_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)

# Crear botones
ax_nuke = plt.axes([0.81, 0.02, 0.1, 0.05])
ax_heal = plt.axes([0.70, 0.02, 0.1, 0.05])
button_nuke = Button(ax_nuke, 'Nuke')
button_heal = Button(ax_heal, 'Heal')
button_nuke.on_clicked(nuke)
button_heal.on_clicked(heal)

# Agregar widget Text para mostrar la temperatura
temperature_text = plt.text(0.02, 0.90, 'Temperature: ', transform=fig.transFigure, color='black', fontsize=10)

# Definimos la función que actualizará la animación
def update_animation():
    global vida
    
    # Actualizar la vida de las células basada en la temperatura recibida
    while puerto_serial.in_waiting > 0:
        mensaje = puerto_serial.readline().decode().strip()
        if mensaje == "Reiniciar":
            print("Reiniciar")
            reset_game(None)
        elif mensaje == "nuke":
            print("nuking")
            nuke()
        elif mensaje=="heal":
            print("healing")
            heal()
        elif mensaje.startswith("T"):
            temperatura = float(mensaje[1:])
            # Actualizar la vida de las células según la temperatura
            if temperatura < 19:
                vida -= 10
            elif temperatura > 22:
                vida += 20
            temperature_text.set_text(f'Temperature: {temperatura}')  # Actualizar el texto de temperatura    
        else:
            pass

    # Lógica de actualización de la animación
    update(0, img, grid, live_cells_text)
    plt.pause(0.1)  # Pausa para controlar la velocidad de la animación

# Creamos los QTimer para controlar la velocidad de la animación y enviar la cantidad de células vivas
timer = QTimer()
timer.timeout.connect(update_animation)
timer.start(10)  # Intervalo de actualización inicial

timer2 = QTimer()
timer2.timeout.connect(enviar_celdas_vivas)
timer2.start(1000)  # Intervalo de actualización inicial

plt.show()