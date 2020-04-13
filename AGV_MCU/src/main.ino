#include <ArduinoJson.h>
// #include <EEPROM.h>

void Serialavailable();
//Timer
    unsigned long previousMillis = 0; 
    int oneSTask;
//Serial
    String Rx0;


void setup() {
  Serial.begin(57600);
  delay(100);
  Serial.println("\n\n{\"name\":\"AGV\"}");

}

void loop() {
    unsigned long currentMillis = millis();
    if((unsigned long)(currentMillis - previousMillis) >= 1) { // 1000 = 1 second
        previousMillis = currentMillis; 
        // 50mSecond task
        oneSTask++;
        if (oneSTask > 2000){
            oneSTask=0;
            
            // Serial.println("{\"delay\":\"2 second\"}");
        }
    }
    Serialavailable();
}

void Serialavailable(){ 
    StaticJsonBuffer<200> jsonBuffer;
    if ( Serial.available() > 0 ) {
        Rx0 = Serial.readStringUntil('\n');
        // Rx0.toCharArray(serial_0_buffer,Rx0.length()+1); 
        JsonObject& root = jsonBuffer.parseObject(Rx0);

        if (!root.success()) {
            Serial.println("{\"Error\":\"parseObject\"}");
            return;
        }
        if (root["neme"] == 1){
            Serial.println("{\"name\":\"AGV\"}");
        }
        if (root["mode"] == 1){
            Serial.println("{\"mode\":1}");
        }
        if (root["mode"] == 2){
            Serial.println("{\"mode\":2}");
        }
        if (root["mode"] == 3){
            Serial.println("{\"mode\":3}");
        }
        if (root["mode"] == 4){
            Serial.println("{\"mode\":4}");
        }
        if (root["mode"] == 5){
            Serial.println("{\"mode\":5}");
        }
    }
}

/*
{"NAME":1}
{"mode":1}

*/