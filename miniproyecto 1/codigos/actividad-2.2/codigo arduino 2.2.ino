#include <DHT.h>

#define DHTPIN 5     // Pin donde está conectado el sensor DHT11
#define DHTTYPE DHT11   // Tipo de sensor DHT (DHT11 en este caso)

DHT dht(DHTPIN, DHTTYPE);

const int rojo = 9;
const int verde = 10;
const int azul = 11;
const int BUTTON_PIN = 7;
const int Nuke = 3; // Pin del joystick
const int Heal = 2; // Pin del potenciometro
int celdas_vivas;

void setup() {
  // Configurar pines como salida
  pinMode(rojo, OUTPUT);
  pinMode(verde, OUTPUT);
  pinMode(azul, OUTPUT);

  // Configurar pin del botón como entrada con pullup
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(Nuke, INPUT_PULLUP);
  pinMode(Heal, INPUT_PULLUP);
  // Inicializar comunicación serial
  Serial.begin(9600);
  dht.begin(); // Inicializar el sensor DHT11
}

void loop() {
  // Leer la temperatura del sensor DHT11
  // Verificar si se presionó el botón
  if (digitalRead(Nuke) == LOW) {
    // Enviar un mensaje a Python indicando "nuke"
    Serial.println("nuke");
    // Espera un breve periodo para evitar múltiples detecciones del botón
    delay(100);
  }

  // Verificar si la fotoresistencia está en la oscuridad
  if (digitalRead(Heal) == LOW) {
    // Enviar un mensaje a Python indicando "heal"
    Serial.println("heal");
    // Espera un breve periodo para evitar múltiples detecciones
    delay(100);
  }

  float temperatura = dht.readTemperature();
  // Verificar si se presionó el botón
  if (digitalRead(BUTTON_PIN) == LOW) {
    // Enviar un mensaje a Python indicando que se debe reiniciar el juego
    Serial.println("Reiniciar");
    // Espera un breve periodo para evitar múltiples detecciones del botón
    delay(100);
  }
  // Verificar si la lectura fue exitosa
  if (!isnan(temperatura)) {
    // Enviar la temperatura al código Python a través del puerto serial
    Serial.print("T");
    Serial.println(temperatura);
  }

  // Verificar si hay datos disponibles en el puerto serial
  if (Serial.available() > 0) {
    // Leer el número de células vivas desde Python
    celdas_vivas = Serial.read();

    if (celdas_vivas == 'E') {       
      digitalWrite(azul, HIGH);
      digitalWrite(verde, LOW);
      digitalWrite(rojo, LOW);
    }
    if (celdas_vivas == 'S') {             
      digitalWrite(azul, LOW);
      digitalWrite(verde, HIGH);
      digitalWrite(rojo, LOW);
    }
    if (celdas_vivas == 'A') {                 
      digitalWrite(azul, LOW);
      digitalWrite(verde, LOW);
      digitalWrite(rojo, HIGH);
    }
  }
}
