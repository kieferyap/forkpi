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

  if (finger.emptyDatabase()) {
    printf("Found fingerprint sensor!\n");
  } else {
    printf("Did not find fingerprint sensor :(\n");
  }
  printf("Waiting for valid finger...\n");

}

/*
  sudo python
  import wiringpi2 as wp
  fd = wp.serialOpen("/dev/ttyAMAO", 57600)
  wp.serialPutchar(fd, __)
  wp.serialDataAvail(fd)
  wp.serialGetchar(fd)
*/
// getImage:        EF  01  FF  FF  FF  FF  01  00  03  01  00  05
// emptyDatabase:   EF  01  FF  FF  FF  FF  01  00  03  0D  00  11
// verifyPassword:  EF  01  FF  FF  FF  FF  01  00  07  13  00  00  00  00  00  1B

