#include "esp_camera.h"
#include <WiFi.h>
#include "camera_pins.h"
#include "pwm_control.h"

// Forward declaration of the function from app_httpd.cpp
void startCameraServer();

// Wi-Fi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";


#define LED_GPIO 2

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Configure GPIOs for PWM output
  const int freq = 20000; //memo:可聴範囲より上に上げる事
  const int resolution = 8;
  
  // GPIO 12, Channel 4
  ledcSetup(4, freq, resolution);
  ledcAttachPin(12, 4);
  ledcWrite(4, 0);

  // GPIO 13, Channel 5
  ledcSetup(5, freq, resolution);
  ledcAttachPin(13, 5);
  ledcWrite(5, 0);

  // GPIO 14, Channel 6
  ledcSetup(6, freq, resolution);
  ledcAttachPin(14, 6);
  ledcWrite(6, 0);

  // GPIO 15, Channel 7
  ledcSetup(7, freq, resolution);
  ledcAttachPin(15, 7);
  ledcWrite(7, 0);


  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Best quality for streaming
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the blightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void loop() {
    static unsigned long last_phase_change_time = 0;
    static bool is_on_phase = false;
    unsigned long current_time = millis();

    // Check if it's time to toggle the phase (every 25ms)
    if (current_time - last_phase_change_time >= 25) {
        last_phase_change_time = current_time;
        is_on_phase = !is_on_phase;

        if (is_on_phase) {
            // --- ON-PHASE: Calculate and apply PWM duty ---
            int base_duty = spd_state;
            int right_duty = base_duty;
            int left_duty = base_duty;

            // Apply trim only when moving forward or backward
            bool is_moving_forward = pwm_states[4].enabled && pwm_states[5].enabled;
            bool is_moving_backward = pwm_states[6].enabled && pwm_states[7].enabled;

            if (is_moving_forward || is_moving_backward) {
                right_duty = constrain(base_duty + trim_state, 0, 255);
                left_duty  = constrain(base_duty - trim_state, 0, 255);
            }

            // Right motor channels (GPIO12 -> ch4, GPIO14 -> ch6)
            ledcWrite(4, pwm_states[4].enabled ? right_duty : 0);
            ledcWrite(6, pwm_states[6].enabled ? right_duty : 0);

            // Left motor channels (GPIO13 -> ch5, GPIO15 -> ch7)
            ledcWrite(5, pwm_states[5].enabled ? left_duty : 0);
            ledcWrite(7, pwm_states[7].enabled ? left_duty : 0);
        } else {
            // --- OFF-PHASE: Set all motor outputs to LOW ---
            ledcWrite(4, 0);
            ledcWrite(5, 0);
            ledcWrite(6, 0);
            ledcWrite(7, 0);
        }
    }
}