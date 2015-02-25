#include "Pi_Serial.h"
#include "Pi_Fingerprint.h"
#include <stdio.h>

int main() {
  // Pi_Serial mySerial(6, 11);
  Pi_Serial mySerial(16, 15);
  Pi_Fingerprint finger = Pi_Fingerprint(&mySerial);

  // mySerial.begin(9600);
  // set the data rate for the sensor serial port
  finger.begin(57600);
  // finger.begin(9600);

  if (finger.verifyPassword()) {
    printf("Found fingerprint sensor!\n");
  } else {
    printf("Did not find fingerprint sensor :(\n");
  }
  printf("Waiting for valid finger...\n");

}