#define SENSOR_BUS hi2c1
#define BOOT_TIME  10

#include "stdint.h"

typedef struct IMU_Handle IMU_Handle;

typedef void (*IMU_Data_cb)(IMU_Handle* this, uint32_t tick);

typedef struct IMU_Handle
{
	float Acc[3];
	float Gyro[3];
	float Temp;

	uint32_t LastAccTick;
	uint32_t LastGyroTick;
	uint32_t LastTempTick;

	uint32_t _dataInteval;  // in tics

	IMU_Data_cb _onNewAcc;
	IMU_Data_cb _onNewGyro;
	IMU_Data_cb _onNewTemp;
} IMU_Handle;

void IMU_Init(IMU_Handle* imu);

void IMU_CallbackSet(IMU_Handle* imu, IMU_Data_cb onNewAcc, IMU_Data_cb onNewGyro, IMU_Data_cb onNewTemp);

void IMU_Update(IMU_Handle* imu, uint32_t tick);
