/*DECLARAÇÃO DE VARIAVEIS MOTORES PWM */
#define MotorA_sentido1 2
#define MotorA_sentido2 4
#define MotorB_sentido1 6
#define MotorB_sentido2 7
#define MotorA_PWM 3  
#define MotorB_PWM 5

// * VELOCIDADES 0 - 255 - \\ 0 - PARADO, 1 - DEVAGAR, 2 - NORMAL e 3 - RÁPIDO * //
#define veloc0 0
#define veloc1 15
#define veloc2 35
#define veloc3 60
 
// * SENSORES DIREITA - ESQUERDA * //
#define Sensor_direita 10
#define Sensor_esquerda 9
bool direita, esquerda;
 
void setup() {
  delay(5000);
  Serial.begin(9600);
  pinMode(MotorA_sentido1, OUTPUT);
  pinMode(MotorA_sentido2, OUTPUT);
  pinMode(MotorB_sentido1, OUTPUT);
  pinMode(MotorB_sentido2, OUTPUT);
  pinMode(MotorA_PWM, OUTPUT);
  pinMode(MotorB_PWM, OUTPUT);
  pinMode(Sensor_direita, INPUT);
  pinMode(Sensor_esquerda, INPUT);   
 
}
 
void loop() {
   //Define o sentido de rotação dos motores
  digitalWrite(MotorA_sentido1, HIGH); //
  digitalWrite(MotorA_sentido2, LOW);
  digitalWrite(MotorB_sentido1, LOW);
  digitalWrite(MotorB_sentido2, HIGH);
 
  //Leituras dos Sensores
  direita = digitalRead(Sensor_direita);
  esquerda = digitalRead(Sensor_esquerda);
  Serial.print(direita);
  Serial.print(" || ");
  Serial.println(esquerda);
 
  //Rodando os motores dependendo das leituras
 if(direita == false && esquerda == false){
 analogWrite(MotorA_PWM, veloc2);
 analogWrite(MotorB_PWM, veloc2);
 } else if(direita == false && esquerda == true){
 delay(0);
 analogWrite(MotorA_PWM, veloc2);
 analogWrite(MotorB_PWM, veloc0);
 delay(0);
 }else if(direita == true && esquerda == false){
 delay(0);
 analogWrite(MotorA_PWM, veloc0);
 analogWrite(MotorB_PWM, veloc2);
 delay(0);
 
 }else if(direita == true && esquerda == true){
 analogWrite(MotorA_PWM, veloc0);
 analogWrite(MotorB_PWM, veloc0);
 }
}
