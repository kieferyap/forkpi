#include "Pi_Serial.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <wiringPi.h>
#include <wiringSerial.h>

Pi_Serial::Pi_Serial(uint16_t rxPin, uint16_t txPin) {
  myRxPin = rxPin;
  myTxPin = txPin;
}

Pi_Serial::~Pi_Serial(void) {
  // close(fd);
  serialClose(fd);
}

int Pi_Serial::begin(uint16_t baudrate) {

  if (wiringPiSetup() == -1)
    return -1;

  // Open the Port. We want read/write, no "controlling tty" status, and open it no matter what state DCD is in
  // fd = open("/dev/ttyAMA0", O_RDWR | O_NOCTTY | O_NDELAY);
  fd = serialOpen("/dev/ttyAMA0", baudrate);
  serialFlush(fd);
  printf("%d\n\n", fd);
  if (fd == -1) {
    printf("open_port: Unable to open /dev/ttyAMA0 - ");
    return(-1);
  }

  // pinMode (myRxPin, INPUT) ; // 11
  // pinMode (myTxPin, OUTPUT) ; // 6

  // Turn off blocking for reads, use (fd, F_SETFL, FNDELAY) if you want that
  fcntl(fd, F_SETFL, 0);
  // fcntl(fd, F_SETFL, FNDELAY);
}

bool Pi_Serial::available() {
  return serialDataAvail(fd);
}

char Pi_Serial::readbyte() {
  return serialGetchar(fd);
  // char buf;
  // int n = read(fd, (void*)&buf, sizeof(buf));
  // if (n < 0) {
  //   perror("Read failed - ");
  //   return -1;
  // } else if (n == 0){
  //   printf("No data on port\n");
  //   return -2;
  // } else {
  //   // buf[n] = '\0';
  //   printf("%i bytes read : %s", n, buf);
  //   return buf;
  // }
}

int Pi_Serial::writebyte(uint8_t val) {
  serialPutchar(fd, val);
  serialFlush(fd);
  // int NumBytes = sizeof(uint8_t);
  // int n = write(fd, (void*)&val, NumBytes);
  // if (n < 0) {
  //   perror("Write failed - ");
  //   return -1;
  // }
  // return n;
}