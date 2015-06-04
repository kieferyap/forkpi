#include <stdint.h>
#ifndef _PI_SERIAL_H
#define _PI_SERIAL_H 

class Pi_Serial {
 public:
  Pi_Serial(uint16_t rxPin, uint16_t txPin);
  ~Pi_Serial(void);
  int begin(uint16_t baud);

  bool available(void);
  char readbyte(void);
  int writebyte(uint8_t val);

 private: 
  int fd;
  int myRxPin, myTxPin;
};

#endif
