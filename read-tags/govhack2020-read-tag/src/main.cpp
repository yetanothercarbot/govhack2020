#include <Arduino.h>
#include <ezTime.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include "WiFiCredentials.h" // NOT in Git Repo!
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#ifndef WIFI_SSID
#define WIFI_SSID "your-ssid"
#define WIFI_PASS  "your-password"
#endif

#define SERVER_HOSTNAME "ec2-3-106-166-215.ap-southeast-2.compute.amazonaws.com"

struct tagData {
  uint64_t GUID;
  uint64_t UPC;
  float longitude;
  float latitude;
  uint32_t purchaseTime;
  uint8_t recycle;
};



#define PN532_IRQ   (D5)
#define PN532_RESET (D6) 
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);
ESP8266WiFiMulti WiFiMulti;

struct tagData datum1;
#define ledActive LOW; // NodeMCU LEDs are active low
bool ledStatus = !ledActive;
#define ledPin D0

void setup(void) {
  pinMode(ledPin, ledStatus);

  Serial.begin(115200);
  while (!Serial) {}

  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(WIFI_SSID, WIFI_PASS);

  while ((WiFiMulti.run() != WL_CONNECTED)) {
    ledStatus = !ledStatus;
    digitalWrite(ledPin, ledStatus);
    delay(50);
  }
  nfc.begin();

  // Turn LEDs off
  ledStatus = !ledActive;
  digitalWrite(ledPin, ledStatus);

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1) yield(); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  Serial.println("Waiting for an ISO14443A Card ...");

}


void loop(void) {
  datum1.GUID = random(100000);
  datum1.UPC = 9300605120693;
  datum1.longitude = -27.506610;
  datum1.latitude = 152.947870;
  datum1.purchaseTime = random(1597403508,1597463508);
  datum1.recycle = random(8);


  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
    
  // Wait for an NTAG203 card.  When one is found 'uid' will be populated with
  // the UID, and uidLength will indicate the size of the UUID (normally 7)
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
  
  if (success) {
    // Display some basic information about the card
    Serial.println("Found an ISO14443A card");
    Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("  UID Value: ");
    nfc.PrintHex(uid, uidLength);
    Serial.println("");
    
    if (uidLength == 7) {
      uint8_t data[32];
      
      // We probably have an NTAG2xx card (though it could be Ultralight as well)
      Serial.println("Seems to be an NTAG2xx tag (7 byte UID)");	  
      
      for (uint8_t i = 0; i < 13; i++) {
        success = nfc.ntag2xx_ReadPage(i, data);
        

        Serial.print("PAGE ");
        if (i < 10) {
          Serial.print("0");
          Serial.print(i);
        } else {
          Serial.print(i);
        }
        Serial.print(": ");

        // Display the results, depending on 'success'
        if (success) {
          // Dump the page data
          nfc.PrintHexChar(data, 4);
        } else {
          Serial.println("Unable to read the requested page!");
        }
      }
      WiFiClient client;
      HTTPClient http;
      // http.begin(client, "http://" SERVER_HOSTNAME ":8080/");
      // http.addHeader("Content-Type", "text/csv");
      char toSend[104];
      uint32_t current_time = 0;
      sprintf(toSend, "%032.18u,%032.18u", current_time, datum1.GUID);
      Serial.println(toSend);
      // http.POST()
      int httpCode = http.POST("{\"hello\":\"world\"}");

    }
    else {
      Serial.println("This doesn't seem to be an NTAG203 tag (UUID length != 7 bytes)!");
    }
    delay(1000);
  }
}

