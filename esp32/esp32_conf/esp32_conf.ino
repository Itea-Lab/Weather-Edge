#include <Wire.h>
#include <WiFi.h>
#include <U8g2lib.h>
#include <PubSubClient.h>

// Replace with your own WiFi credentials
const char *ssid = "SSID";
const char *password = "WIFI_PASSWORD";

const char *mqtt_server = "MQTT_BROKER_IP";
const int mqtt_port = 1883;
const char *mqtt_topic = "test/topic";
const char *mqtt_username = "username";
const char *mqtt_password = "password";

WiFiClient espClient;
PubSubClient client(espClient);

// OLED Display Setup (for SSD1306 128x64 using I2C) delete this if you do not use OLED Display
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/U8X8_PIN_NONE);

void setup()
{
    Serial.begin(115200);
    Wire.begin(21, 18);
    u8g2.begin();
    u8g2.enableUTF8Print(); // Enable UTF-8 support

    // Display "Connecting to WiFi..."
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x10_tf);
    u8g2.drawStr(10, 20, "Connecting to WiFi...");
    u8g2.sendBuffer();

    // Start WiFi connection
    WiFi.begin(ssid, password);

    // Wait until connected
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
    }

    // Get WiFi details
    String ipAddress = WiFi.localIP().toString();

    // Delete this if you do not use OLED Display
    u8g2.clearBuffer();
    u8g2.drawStr(10, 30, "Connected");
    u8g2.drawStr(10, 50, "IP:");
    u8g2.drawStr(35, 50, ipAddress.c_str()); // Show IP Address
    u8g2.sendBuffer();

    client.setServer(mqtt_server, mqtt_port);
    // Connect to MQTT Broker
    Serial.println("Connecting to MQTT...");
    while (!client.connected())
    {
        if (client.connect("ESP32_Client", mqtt_username, mqtt_password))
        {
            Serial.println("MQTT Connected");
        }
        else
        {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            Serial.println(". Trying again...");
            delay(500);
        }
    }
}

void loop()
{
    if (!client.connected())
    {
        Serial.println("Reconnecting to MQTT...");
        while (!client.connected())
        {
            if (client.connect("ESP32_Client", mqtt_username, mqtt_password))
            {
                Serial.println("MQTT Reconnected");
            }
            else
            {
                Serial.print("Failed, rc=");
                Serial.print(client.state());
                Serial.println(". Trying again...");
                delay(500);
            }
        }
    }

    int randomValue = random(0, 101);
    char message[10];
    snprintf(message, sizeof(message), "%d", randomValue);

    // Publish random value to MQTT
    if (client.publish(mqtt_topic, message))
    {
        Serial.print("Sent: ");
        Serial.println(message);
    }
    else
    {
        Serial.println("Failed to send message");
    }

    client.loop();
    delay(1000);
}
