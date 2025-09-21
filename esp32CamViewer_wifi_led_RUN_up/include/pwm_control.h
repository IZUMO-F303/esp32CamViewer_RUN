#ifndef PWM_CONTROL_H
#define PWM_CONTROL_H

#define MAX_PWM_CHANNELS 8 // We use channels 4, 5, 6, 7. Array size 8 is safe.

struct PwmChannelState {
    bool enabled = false;
    int duty = 0;
};

// Declare this as extern so it can be shared between main.cpp and app_httpd.cpp
extern PwmChannelState pwm_states[MAX_PWM_CHANNELS];
extern int spd_state;
extern int trim_state;

#endif // PWM_CONTROL_H
