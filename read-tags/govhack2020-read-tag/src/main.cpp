#include <Arduino.h>

struct tagData {
  uint64_t GUID;
  uint64_t UPC;
  float longitude;
  float latitude;
  uint32_t purchaseTime;
  uint8_t recycle;
};

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_IRQ   (D5)
#define PN532_RESET (D6) 
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

struct tagData datum1; 

void setup(void) {
  Serial.begin(115200);
  while (!Serial) delay(10); // for Leonardo/Micro/Zero

  Serial.println("Hello!");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  Serial.println("Waiting for an ISO14443A Card ...");

  datum1.GUID = random(100000);
  datum1.UPC = 9300605120693;
  datum1.longitude = -27.506610;
  datum1.latitude = 152.947870;
  datum1.purchaseTime = random(1597403508,1597463508);
  datum1.recycle = random(8);
}


void loop(void) {

}

