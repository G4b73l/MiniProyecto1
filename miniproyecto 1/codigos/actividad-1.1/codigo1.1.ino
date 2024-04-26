// Definición de pines para LEDs y botones
const int ledPins[] = {2, 3, 4, 5};       // Pines para los LEDs (4 LEDs)
const int buttonPins[] = {6, 7, 8, 9};     // Pines para los botones (4 botones)
const int buzzerPin = 10;                  // Pin para el buzzer pasivo
const int resetButtonPin = 11;             // Pin para el botón de reinicio

// Variables de juego
int puntos = 30;        // Puntaje inicial del jugador
int nivel = 1;         // Nivel de dificultad inicial
int successfulHits = 0; // Contador de golpes exitosos

// Tiempo de espera inicial para cada LED (en milisegundos)
int initialDelay = 1000;

void resetGame() {
  Serial.println("Juego reiniciado.");
  puntos = 30;
  nivel = 1;
  successfulHits = 0;
  initialDelay = 1000;
}

void playDefeatMelody() {
  tone(buzzerPin, 150, 200);
  delay(250);
  tone(buzzerPin, 100, 300);
  delay(400);
}

void setup() {
  // Configurar pines de LEDs como salidas
  for (int i = 0; i < sizeof(ledPins) / sizeof(ledPins[0]); i++) {
    pinMode(ledPins[i], OUTPUT);
  }

  // Configurar pines de botones como entradas con pull-up interno
  for (int i = 0; i < sizeof(buttonPins) / sizeof(buttonPins[0]); i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }

  // Configurar pin del buzzer como salida
  pinMode(buzzerPin, OUTPUT);

  // Configurar pin del botón de reinicio como entrada con pull-up interno
  pinMode(resetButtonPin, INPUT_PULLUP);

  // Iniciar comunicación serial
  Serial.begin(9600);

  // Inicializar la generación de números aleatorios
  randomSeed(analogRead(0));
}

void loop() {
  // Verificar si se presiona el botón de reinicio
  if (digitalRead(resetButtonPin) == LOW) {
    resetGame();
    delay(1000); // Pequeño retraso para evitar rebotes
    return;
  }

  // Generar un LED aleatorio para esta ronda
  int activeLed = random(0, sizeof(ledPins) / sizeof(ledPins[0]));

  // Encender el LED activo
  digitalWrite(ledPins[activeLed], HIGH);

  // Esperar el tiempo de espera actual
  delay(initialDelay);

  // Apagar el LED
  digitalWrite(ledPins[activeLed], LOW);

  // Verificar si se presionó el botón correspondiente al LED activo
  if (digitalRead(buttonPins[activeLed]) == LOW) {
    // Golpe exitoso, sumar puntos y contar golpe exitoso
    puntos += 10;
    successfulHits++;

    // Reproducir tono de acierto
    tone(buzzerPin, 1000, 200);

    // Verificar si se alcanzó la cantidad de golpes exitosos para subir de nivel
    if (successfulHits >= 5) {
      nivel++; // Aumentar el nivel
      successfulHits = 0; // Reiniciar contador de golpes exitosos

      // Reducir el tiempo de espera para la siguiente ronda
      if (initialDelay > 200) {
        initialDelay -= 200; // Reducir en 200 milisegundos
      }
    }
  } else {
    // Golpe fallido, restar puntos
    puntos -= 20;
    // Reproducir tono de error
    tone(buzzerPin, 200, 200);
  }

  // Mostrar información del juego por el monitor serial
  Serial.print("nivel: ");
  Serial.println(nivel);
  Serial.print("puntos: ");
  Serial.println(puntos);

  // Verificar condiciones de finalización del juego
  if (puntos <= 0) {
    // El jugador perdió el juego
    playDefeatMelody(); // Reproducir melodía de derrota
    delay(2000); // Esperar antes de reiniciar el juego
    resetGame(); // Reiniciar el juego
  }

  // Esperar un breve momento antes de iniciar la siguiente ronda
  delay(1000);
}
