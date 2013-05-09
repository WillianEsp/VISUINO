boolean sync;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  
  sync=false;
}

void loop() {

  if (!sync)
    handshake(); 

  int counter = -5;
  while(1)
  {
    Serial.println(counter);
    counter++;
    delay(500);
    if (counter == 10)
    {
      counter = -5;
      Serial.println("Close Serial Communication");
    }
  }
}

void handshake() {
  boolean finish = false;
  char dataRead;
  while(!finish)
  {
    if (Serial.available() >= 4)
    {
       dataRead = Serial.read();
       //Serial.println(dataRead);
       if (dataRead == 'P' && Serial.peek() == 'i')
       {
         dataRead = Serial.read();
         if (Serial.peek() == 'n')
         {
           dataRead = Serial.read();
           if (Serial.peek() == 'g')
           {
             finish = true;
             Serial.println("Pong");
           }
         }
       }
    }
   }
 }
