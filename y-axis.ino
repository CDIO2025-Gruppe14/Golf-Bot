const int dirPin = 4;
const int stepPin = 3;



//skal lige vide hvad det her er
int stepDelayMicros = 800; // standardhastighed

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "LEFT") {
      digitalWrite(dirPin, LOW);
      stepMotor(200);
    } else if (command == "RIGHT") {
      digitalWrite(dirPin, HIGH);
      stepMotor(200);
    } else if (command.startsWith("STEP")) {
      int numSteps = command.substring(5).toInt();
      stepMotor(numSteps);
    } else if (command.startsWith("SPEED")) {
      int newDelay = command.substring(6).toInt();
      if (newDelay > 0) {
        stepDelayMicros = newDelay;
        Serial.println("Speed set to " + String(stepDelayMicros) + " µs");
      }
    }
  }
}

void stepMotor(int steps) {
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepDelayMicros);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepDelayMicros);
  }
}
