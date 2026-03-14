#ifndef CONFIG_H__
#define CONFIG_H__

#include "DSP_Constants.h"

#define FIRMWARE_VERSION_MAJOR 0
#define FIRMWARE_VERSION_MINOR 6
#define FIRMWARE_VERSION_PATCH 9

#define IMU_TICK_RESOLUTION 1000.0f  // Number of ticks in second
#define IMU_MS_TO_TICK(ms)  ((uint32_t)((ms) * IMU_TICK_RESOLUTION / 1000.0f))
#define IMU_US_TO_TICK(us)  ((uint32_t)((us) * IMU_TICK_RESOLUTION / 1000000.0f))

#define IMU_USE_RADIAN    (1)
#define IMU_X_DIR         (1)
#define IMU_Y_DIR         (-1)
#define IMU_Z_DIR         (1)
#define IMU_FROM_DEG(deg) (IMU_USE_RADIAN ? ((deg) * DEG_TO_RAD_F32) : (deg))

#define AHRS_UPDATE_INTERVAL_MS 50

#endif /* CONFIG_H__ */