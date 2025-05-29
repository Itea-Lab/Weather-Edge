#include <SoftwareSerial.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
// If you use OLED display
#include <U8g2lib.h>
#include <Wire.h>

// Pins for SoftwareSerial
#define MYPORT_TX 12
#define MYPORT_RX 13

// Wi-Fi credentials
const char *ssid = "SSID";
const char *password = "WIFI_PASSWORD";

// MQTT broker details
const char *mqtt_server = "192.168.0.7";
const int mqtt_port = 1883;
const char *mqtt_user = "testclient";
const char *mqtt_password = "testpassword";
const char *mqtt_topic = "test/topic";

// Create an instance of the PubSubClient
WiFiClient espClient;
PubSubClient client(espClient);

// OLED Display Setup (for SSD1306 128x64 using I2C) delete this if you do not use OLED Display
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/U8X8_PIN_NONE);

// Create a SoftwareSerial object
EspSoftwareSerial::UART myPort;

// Data buffer for weather station data
char databuffer[35];
double temp;

void getBuffer()
{
    int index = 0;
    while (index < 35)
    {
        if (myPort.available())
        {
            databuffer[index] = myPort.read();
            if (index == 0 && databuffer[0] != 'c')
            {
                index = -1; // Restart if first character is not 'c'
            }
            index++;
        }
    }
}

int transCharToInt(char *_buffer, int _start, int _stop)
{
    int result = 0;
    for (int i = _start; i <= _stop; i++)
    {
        result = 10 * result + (_buffer[i] - '0');
    }
    return result;
}

int transCharToInt_T(char *_buffer)
{
    int result = (_buffer[13] == '-') ? -(((_buffer[14] - '0') * 10) + (_buffer[15] - '0')) : ((_buffer[13] - '0') * 100) + ((_buffer[14] - '0') * 10) + (_buffer[15] - '0');
    return result;
}

int WindDirection()
{
    return transCharToInt(databuffer, 1, 3);
}

float WindSpeedAverage()
{
    return 0.44704 * transCharToInt(databuffer, 5, 7);
}

float WindSpeedMax()
{
    return 0.44704 * transCharToInt(databuffer, 9, 11);
}

float Temperature()
{
    return (transCharToInt_T(databuffer) - 32.00) * 5.00 / 9.00;
}

float RainfallOneHour()
{
    return transCharToInt(databuffer, 17, 19) * 25.40 * 0.01;
}

float RainfallOneDay()
{
    return transCharToInt(databuffer, 21, 23) * 25.40 * 0.01;
}

int Humidity()
{
    return transCharToInt(databuffer, 25, 26);
}

float BarPressure()
{
    return transCharToInt(databuffer, 28, 32) / 10.00;
}

void connectWifi()
{
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x10_tf);
    u8g2.drawStr(10, 20, "Connecting to WiFi...");
    u8g2.sendBuffer();

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    // Get WiFi details
    String ipAddress = WiFi.localIP().toString();

    // Delete this if you do not use OLED Display
    u8g2.clearBuffer();
    u8g2.drawStr(10, 30, "Connected");
    u8g2.drawStr(10, 50, "IP:");
    u8g2.drawStr(35, 50, ipAddress.c_str()); // Show IP Address
    u8g2.sendBuffer();
}

void displayWiFiStats()
{
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x10_tf);

    String ip = WiFi.localIP().toString();
    int rssi = WiFi.RSSI();
    int channel = WiFi.channel();
    int txPower = 19.5; // Default max power for ESP32

    u8g2.setCursor(10, 10);
    u8g2.print("IP: ");
    u8g2.print(ip);

    u8g2.setCursor(10, 20);
    u8g2.print("Signal: ");
    u8g2.print(rssi);
    u8g2.print(" dBm");

    u8g2.setCursor(10, 30);
    u8g2.print("Channel: ");
    u8g2.print(channel);

    u8g2.setCursor(10, 40);
    u8g2.print("TX Power: ");
    u8g2.print(txPower);
    u8g2.print(" dBm");

    u8g2.sendBuffer();
}

void connectToMQTT()
{
    client.setServer(mqtt_server, mqtt_port);
    Serial.println("Connecting to MQTT...");

    while (!client.connected())
    {
        if (client.connect("ESP32", mqtt_user, mqtt_password))
        {
            Serial.println("Connected to MQTT broker");
        }
        else
        {
            Serial.print("Failed to connect, rc=");
            Serial.print(client.state());
            Serial.println(" Trying again in 5 seconds...");
            delay(5000);
        }
    }
}

void publishDataToMQTT(const char *data)
{
    if (!client.connected())
    {
        connectToMQTT();
    }
    client.loop();

    Serial.print("Publishing message: ");
    Serial.println(data);

    client.publish(mqtt_topic, data);
}

void setup()
{
    Serial.begin(9600);
    Wire.begin(21, 22);
    u8g2.begin();
    u8g2.enableUTF8Print(); // Enable UTF-8 support

    // Initialize the software serial port
    myPort.begin(9600, SWSERIAL_8N1, MYPORT_RX, MYPORT_TX, false);

    if (!myPort)
    {
        Serial.println("Invalid EspSoftwareSerial pin configuration, check config");
        while (1)
        {
            delay(1000);
        }
    }

    connectWifi();
    connectToMQTT();
}

void loop()
{
    getBuffer();
    static unsigned long lastCheck = 0;
    if (millis() - lastCheck >= 5000) // Update OLED every 5 seconds
    {
        lastCheck = millis();
        displayWiFiStats();
    }
    // Serial.print("Wind Direction: ");
    // Serial.print(WindDirection());
    // Serial.println("  ");
    // Serial.print("Average Wind Speed (One Minute): ");
    // Serial.print(WindSpeedAverage());
    // Serial.println(" m/s  ");
    // Serial.print("Max Wind Speed (Five Minutes): ");
    // Serial.print(WindSpeedMax());
    // Serial.println(" m/s");
    // Serial.print("Rain Fall (One Hour): ");
    // Serial.print(RainfallOneHour());
    // Serial.println(" mm  ");
    // Serial.print("Rain Fall (24 Hour): ");
    // Serial.print(RainfallOneDay());
    // Serial.println(" mm");
    // Serial.print("Temperature: ");
    // Serial.print(Temperature());
    // Serial.println(" C  ");
    // Serial.print("Humidity: ");
    // Serial.print(Humidity());
    // Serial.println("%  ");
    // Serial.print("Barometric Pressure: ");
    // Serial.print(BarPressure());
    // Serial.println(" hPa");
    // Serial.println("");
    // Serial.println("");
    StaticJsonDocument<256> doc;

    // Populate the JSON document with weather data
    doc["Wind Direction"] = WindDirection();
    doc["Avg Wind Speed"] = WindSpeedAverage();
    doc["Max Wind Speed"] = WindSpeedMax();
    doc["Rainfall (1hr)"] = RainfallOneHour();
    doc["Rainfall (24hr)"] = RainfallOneDay();
    doc["Temperature"] = Temperature();
    doc["Humidity"] = Humidity();
    doc["Barometric Pressure"] = BarPressure();

    // JSON document to string
    char jsonString[256];
    serializeJson(doc, jsonString);
    Serial.println(jsonString);

    publishDataToMQTT(jsonString);

    delay(10000); // Set delay time
}
