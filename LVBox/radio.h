#ifndef RADIO_H
#define RADIO_H

/// Initialize the radio
void radio_init();
/// Send the data in the global packet over LoRa
void radio_send();

#endif // RADIO_H