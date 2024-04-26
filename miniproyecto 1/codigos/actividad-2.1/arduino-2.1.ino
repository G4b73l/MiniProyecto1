const int rojo = 9;
const int verde = 10;
const int azul = 11;
const int BUTTON_PIN = 7;
int celdas_vivas;

void setup() {
  // Configurar pines como salida
  pinMode(rojo, OUTPUT);
  pinMode(verde, OUTPUT);
  pinMode(azul, OUTPUT);

  // Configurar pin del botón como entrada con pullup
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Inicializar comunicación serial
  Serial.begin(9600);
}

void loop() {
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

  // Verificar si se presionó el botón
  if (digitalRead(BUTTON_PIN) == LOW) {
    // Enviar un mensaje a Python indicando que se debe reiniciar el juego
    Serial.println("Reiniciar");
    // Espera un breve periodo para evitar múltiples detecciones del botón
    delay(100);
  }
}
