/*************************************************** 
  This is a library for our optical Fingerprint sensor

  Designed specifically to work with the Adafruit Fingerprint sensor 
  ----> http://www.adafruit.com/products/751

  These displays use TTL Serial to communicate, 2 pins are required to 
  interface
  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include "Pi_Fingerprint.h"
#include "Pi_Serial.h"
#include <unistd.h>
#include <stdio.h>

Pi_Fingerprint::Pi_Fingerprint(Pi_Serial *ss) {
  thePassword = 0;
  theAddress = 0xFFFFFFFF;
  mySerial = ss;
}

void Pi_Fingerprint::begin(uint16_t baudrate) {
  sleep(1);  // one second delay to let the sensor 'boot up'
  mySerial->begin(baudrate);
}

bool Pi_Fingerprint::verifyPassword(void) {
  uint8_t packet[] = {FINGERPRINT_VERIFYPASSWORD, 
                      (thePassword >> 24), (thePassword >> 16),
                      (thePassword >> 8), thePassword}; // 4 bytes of password separated byte by byte
  printf("writing packet\n");
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, 7, packet);
  printf("\ndone writing\n");
  uint8_t len = getReply(packet);
  printf("got reply of length %02x\n", len);
  
  if ((len == 1) && (packet[0] == FINGERPRINT_ACKPACKET) && (packet[1] == FINGERPRINT_OK))
    return true;

  // printf("\nGot packet type ");
  // printf("%02x", packet[0]);
  // for (int i=1; i<len+1;i++) {
  //   printf(" 0x");
  //   printf("%02x", packet[i]);
  // }
  return false;
}

uint8_t Pi_Fingerprint::getImage(void) {
  uint8_t packet[] = {FINGERPRINT_GETIMAGE};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, 3, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;
  return packet[1];
}

uint8_t Pi_Fingerprint::image2Tz(uint8_t slot) {
  uint8_t packet[] = {FINGERPRINT_IMAGE2TZ, slot};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;
  return packet[1];
}


uint8_t Pi_Fingerprint::createModel(void) {
  uint8_t packet[] = {FINGERPRINT_REGMODEL};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;
  return packet[1];
}


uint8_t Pi_Fingerprint::storeModel(uint16_t id) {
  uint8_t packet[] = {FINGERPRINT_STORE, 0x01, id >> 8, id & 0xFF};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;
  return packet[1];
}
    
//read a fingerprint template from flash into Char Buffer 1
uint8_t Pi_Fingerprint::loadModel(uint16_t id) {
    uint8_t packet[] = {FINGERPRINT_LOAD, 0x01, id >> 8, id & 0xFF};
    writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
    uint8_t len = getReply(packet);
    
    if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
        return -1;
    return packet[1];
}

//transfer a fingerprint template from Char Buffer 1 to host computer
uint8_t Pi_Fingerprint::getModel(void) {
    uint8_t packet[] = {FINGERPRINT_UPLOAD, 0x01};
    writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
    uint8_t len = getReply(packet);
    
    if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
        return -1;
    return packet[1];
}
    
uint8_t Pi_Fingerprint::deleteModel(uint16_t id) {
    uint8_t packet[] = {FINGERPRINT_DELETE, id >> 8, id & 0xFF, 0x00, 0x01};
    writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
    uint8_t len = getReply(packet);
        
    if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
        return -1;
    return packet[1];
}

uint8_t Pi_Fingerprint::emptyDatabase(void) {
  uint8_t packet[] = {FINGERPRINT_EMPTY};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;
  return packet[1];
}

uint8_t Pi_Fingerprint::fingerFastSearch(void) {
  fingerID = 0xFFFF;
  confidence = 0xFFFF;
  // high speed search of slot #1 starting at page 0x0000 and page #0x00A3 
  uint8_t packet[] = {FINGERPRINT_HISPEEDSEARCH, 0x01, 0x00, 0x00, 0x00, 0xA3};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET))
   return -1;

  fingerID = packet[2];
  fingerID <<= 8;
  fingerID |= packet[3];
  
  confidence = packet[4];
  confidence <<= 8;
  confidence |= packet[5];
  
  return packet[1];
}

uint8_t Pi_Fingerprint::getTemplateCount(void) {
  templateCount = 0xFFFF;
  // get number of templates in memory
  uint8_t packet[] = {FINGERPRINT_TEMPLATECOUNT};
  writePacket(theAddress, FINGERPRINT_COMMANDPACKET, sizeof(packet)+2, packet);
  uint8_t len = getReply(packet);
  
  if ((len != 1) && (packet[0] != FINGERPRINT_ACKPACKET)){
   return -1;
  }

  templateCount = packet[2];
  templateCount <<= 8;
  templateCount |= packet[3];
  
  return packet[1];
}



void Pi_Fingerprint::writePacket(uint32_t addr, uint8_t packettype, 
				       uint16_t len, uint8_t *packet) {
#ifdef FINGERPRINT_DEBUG
  printf("---> 0x");
  printf("%02x", (uint8_t)(FINGERPRINT_STARTCODE >> 8));
  printf(" 0x");
  printf("%02x", (uint8_t)FINGERPRINT_STARTCODE);
  printf(" 0x");
  printf("%02x", (uint8_t)(addr >> 24));
  printf(" 0x");
  printf("%02x", (uint8_t)(addr >> 16));
  printf(" 0x");
  printf("%02x", (uint8_t)(addr >> 8));
  printf(" 0x");
  printf("%02x", (uint8_t)(addr));
  printf(" 0x");
  printf("%02x", (uint8_t)packettype);
  printf(" 0x");
  printf("%02x", (uint8_t)(len >> 8));
  printf(" 0x");
  printf("%02x", (uint8_t)(len));
#endif
 
mySerial->writebyte((uint8_t)(FINGERPRINT_STARTCODE >> 8)); // first byte of start code
mySerial->writebyte((uint8_t)FINGERPRINT_STARTCODE); // second byte of start code
mySerial->writebyte((uint8_t)(addr >> 24)); // first byte of module address
mySerial->writebyte((uint8_t)(addr >> 16));
mySerial->writebyte((uint8_t)(addr >> 8));
mySerial->writebyte((uint8_t)(addr)); // 4th byte of module address
mySerial->writebyte((uint8_t)packettype);
mySerial->writebyte((uint8_t)(len >> 8)); // first byte of length
mySerial->writebyte((uint8_t)(len)); // second byte of length
  
uint16_t sum = (len>>8) + (len&0xFF) + packettype; // (first byte of len) + (second byte of len) + (packet type)
// write packet except sum
for (uint8_t i=0; i< len-2; i++) {
  mySerial->writebyte((uint8_t)(packet[i]));
  #ifdef FINGERPRINT_DEBUG
      printf(" 0x"); printf("%02x", (uint8_t)(packet[i]));
  #endif
  sum += packet[i];
}
#ifdef FINGERPRINT_DEBUG
  //printf("Checksum = 0x"); printfln(sum);
  printf(" 0x"); printf("%02x", (uint8_t)(sum>>8));
  printf(" 0x"); printf("%02x", (uint8_t)(sum));
#endif
mySerial->writebyte((uint8_t)(sum>>8));
mySerial->writebyte((uint8_t)sum);
}


uint8_t Pi_Fingerprint::getReply(uint8_t packet[], uint16_t timeout) {
  uint8_t reply[20], idx;
  uint16_t timer=0;
  
  printf("Start of packet printing:\n");
  for(int i=0; i<7; i++){
    printf("0x%02x\n", packet[i]);
  }
  printf("End of packet printing:\n");

  idx = 0;
  #ifdef FINGERPRINT_DEBUG
    printf("<---");
  #endif
  while (true) {
    while (!mySerial->available()) {
      usleep(1000);
      timer++;
      if (timer >= timeout) {
        printf("Returned: Reached timeout\n");
        return FINGERPRINT_TIMEOUT;
      }
    }

    // something to read!
    reply[idx] = mySerial->readbyte();

    #ifdef FINGERPRINT_DEBUG
        printf("%d: 0x%02x\n", idx, reply[idx]);
        // printf(" 0x%02x", reply[idx]);
        fflush(stdout);
    #endif
    if ((idx == 0) && (reply[0] != (FINGERPRINT_STARTCODE >> 8)))
      continue;
    idx++;
    
    // starts from reply code (OK, invalid, etc)
    if (idx >= 9) {
      // must begin with start code
      if ((reply[0] != (FINGERPRINT_STARTCODE >> 8)) ||
          (reply[1] != (FINGERPRINT_STARTCODE & 0xFF))) {
          printf("Returned: BadPacket\n");
          return FINGERPRINT_BADPACKET;
        }
      uint8_t packettype = reply[6];
      printf("Packet type: %d\n", packettype);
      uint16_t len = reply[7]; // first byte 
      len <<= 8; // len = first byte of len + 0x0
      len |= reply[8]; // len = first byte + second byte
      len -= 2; // exclude sum
      printf("Packet len: %d\n", len);
      if (idx <= (len+10)) // maybe this should be just < ?
        continue;
      // done receiving packets
      packet[0] = packettype;      
      for (uint8_t i=0; i<len; i++) {
        packet[1+i] = reply[9+i]; // package packet
      }
      #ifdef FINGERPRINT_DEBUG
      printf("LEN: 0x%02x\n", len);
      #endif
      return len;
    }
  }
}