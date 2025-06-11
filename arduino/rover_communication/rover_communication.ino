#include <SPI.h>
#include <RF24.h>

// Pin definitions for nRF24L01+
#define CE_PIN 9
#define CSN_PIN 10

// Radio pipe addresses for the 2 nodes to communicate
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

// Initialize RF24 object
RF24 radio(CE_PIN, CSN_PIN);

// Buffer for serial communication
const int BUFFER_SIZE = 64;
char serialBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Telemetry structure
struct TelemetryData {
  float temperature;
  float humidity;
  int tagId;
  uint32_t timestamp;
};

TelemetryData telemetry;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize radio communication
  if (!radio.begin()) {
    Serial.println("Radio hardware not responding!");
    while (1); // Hold in infinite loop
  }
  
  // Radio configuration
  radio.setPALevel(RF24_PA_LOW);      // Set power amplifier level
  radio.setChannel(76);               // Set RF channel
  radio.setDataRate(RF24_250KBPS);    // Set data rate
  radio.enableDynamicPayloads();      // Enable dynamic payloads
  radio.setRetries(5, 15);            // Set retry count and delay
  
  // Open pipes for communication
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1, pipes[1]);
  
  // Start listening
  radio.startListening();
}

void loop() {
  // Handle incoming serial data from laptop
  while (Serial.available() > 0) {
    char inChar = Serial.read();
    
    if (inChar == '\n') {
      serialBuffer[bufferIndex] = '\0';  // Null terminate the string
      processSerialCommand(serialBuffer);
      bufferIndex = 0;  // Reset buffer
    } else if (bufferIndex < BUFFER_SIZE - 1) {
      serialBuffer[bufferIndex++] = inChar;
    }
  }
  
  // Check for incoming radio data
  if (radio.available()) {
    radio.read(&telemetry, sizeof(telemetry));
    sendTelemetryToLaptop();
  }
}

void processSerialCommand(const char* command) {
  // Stop listening to send data
  radio.stopListening();
  
  // Send command through radio
  radio.write(command, strlen(command) + 1);
  
  // Resume listening
  radio.startListening();
  
  // Echo command back to laptop for confirmation
  Serial.print("CMD_SENT:");
  Serial.println(command);
}

void sendTelemetryToLaptop() {
  // Format: TELEMETRY,temp,humidity,tagId,timestamp
  Serial.print("TELEMETRY,");
  Serial.print(telemetry.temperature);
  Serial.print(",");
  Serial.print(telemetry.humidity);
  Serial.print(",");
  Serial.print(telemetry.tagId);
  Serial.print(",");
  Serial.println(telemetry.timestamp);
} 