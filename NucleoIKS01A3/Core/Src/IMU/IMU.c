#include "IMU.h"
#include "Config.h"

#include "stm32f4xx_hal.h"

#include "lsm6dso_reg.h"

#include <string.h>
#include <stdio.h>

extern I2C_HandleTypeDef SENSOR_BUS;

static stmdev_ctx_t dev_ctx;

static int16_t data_raw_temperature;
static int16_t data_raw_acceleration[3];
static int16_t data_raw_angular_rate[3];

static int32_t lsm6dso_platform_write(void* handle, uint8_t reg, const uint8_t* bufp, uint16_t len)
{
	I2C_HandleTypeDef* hi2c = (I2C_HandleTypeDef*)handle;
	return HAL_I2C_Mem_Write(hi2c, 0xD6, reg, I2C_MEMADD_SIZE_8BIT, (uint8_t*)bufp, len, 1000);
}

static int32_t lsm6dso_platform_read(void* handle, uint8_t reg, uint8_t* bufp, uint16_t len)
{
	I2C_HandleTypeDef* hi2c = (I2C_HandleTypeDef*)handle;
	return HAL_I2C_Mem_Read(hi2c, 0xD6, reg, I2C_MEMADD_SIZE_8BIT, bufp, len, 1000);
}

static void lsm6dso_platform_delay(uint32_t ms)
{
	HAL_Delay(ms);
}


void IMU_Init(IMU_Handle* imu)
{
	memset(imu, 0, sizeof(IMU_Handle));

	/* Initialize mems driver interface */
	dev_ctx.write_reg = lsm6dso_platform_write;
	dev_ctx.read_reg  = lsm6dso_platform_read;
	dev_ctx.mdelay    = lsm6dso_platform_delay;
	dev_ctx.handle    = &SENSOR_BUS;

	HAL_Delay(10);

	/* Check device ID */
	uint8_t whoamI = 0;
	while(whoamI != LSM6DSO_ID)
	{
		int32_t status = lsm6dso_device_id_get(&dev_ctx, &whoamI);
		printf("LSM6DSO: 0x%X, Status: %d\r\n", whoamI, status);

		HAL_Delay(1000);
	}

	lsm6dso_reset_set(&dev_ctx, PROPERTY_ENABLE);

	uint8_t rst;
	do
	{
		lsm6dso_reset_get(&dev_ctx, &rst);
	}
	while(rst);

	imu->_dataInteval = IMU_US_TO_TICK(1000000 / 833);

	lsm6dso_i3c_disable_set(&dev_ctx, LSM6DSO_I3C_DISABLE);
	/* Enable Block Data Update */
	lsm6dso_block_data_update_set(&dev_ctx, PROPERTY_ENABLE);
	/* Set Output Data Rate */
	lsm6dso_xl_data_rate_set(&dev_ctx, LSM6DSO_XL_ODR_833Hz);
	lsm6dso_gy_data_rate_set(&dev_ctx, LSM6DSO_GY_ODR_833Hz);

	/* Set full scale */
	lsm6dso_xl_full_scale_set(&dev_ctx, LSM6DSO_8g);
	lsm6dso_gy_full_scale_set(&dev_ctx, LSM6DSO_2000dps);

	/* Configure filtering chain(No aux interface)
	 * Accelerometer - LPF1 + LPF2 path
	 */
	// lsm6dso_xl_hp_path_on_out_set(&dev_ctx, LSM6DSO_HP_PATH_DISABLE_ON_OUT);
	// lsm6dso_xl_filter_lp2_set(&dev_ctx, PROPERTY_ENABLE);
}

void IMU_CallbackSet(IMU_Handle* imu, IMU_Data_cb onNewAcc, IMU_Data_cb onNewGyro, IMU_Data_cb onNewTemp)
{
	imu->_onNewAcc  = onNewAcc;
	imu->_onNewGyro = onNewGyro;
	imu->_onNewTemp = onNewTemp;
}

void IMU_Update(IMU_Handle* imu, uint32_t tick)
{
	uint8_t reg;

	if((tick - imu->LastAccTick) >= imu->_dataInteval)
	{
		lsm6dso_xl_flag_data_ready_get(&dev_ctx, &reg);
		if(reg)
		{
			/* Read acceleration field data */
			lsm6dso_acceleration_raw_get(&dev_ctx, data_raw_acceleration);
			imu->Acc[0] = lsm6dso_from_fs8_to_mg(data_raw_acceleration[0]) * IMU_X_DIR / 1000.0f;
			imu->Acc[1] = lsm6dso_from_fs8_to_mg(data_raw_acceleration[1]) * IMU_Y_DIR / 1000.0f;
			imu->Acc[2] = lsm6dso_from_fs8_to_mg(data_raw_acceleration[2]) * IMU_Z_DIR / 1000.0f;

			imu->LastAccTick += imu->_dataInteval;
			if(imu->_onNewAcc)
			{
				imu->_onNewAcc(imu, tick);
			}
		}
	}

	if((tick - imu->LastGyroTick) >= imu->_dataInteval)
	{
		lsm6dso_gy_flag_data_ready_get(&dev_ctx, &reg);
		if(reg)
		{
			/* Read angular rate field data */
			lsm6dso_angular_rate_raw_get(&dev_ctx, data_raw_angular_rate);
			imu->Gyro[0] = IMU_FROM_DEG(lsm6dso_from_fs2000_to_mdps(data_raw_angular_rate[0]) * -IMU_X_DIR / 1000.0f);
			imu->Gyro[1] = IMU_FROM_DEG(lsm6dso_from_fs2000_to_mdps(data_raw_angular_rate[1]) * -IMU_Y_DIR / 1000.0f);
			imu->Gyro[2] = IMU_FROM_DEG(lsm6dso_from_fs2000_to_mdps(data_raw_angular_rate[2]) * -IMU_Z_DIR / 1000.0f);

			imu->LastGyroTick += imu->_dataInteval;
			if(imu->_onNewGyro)
			{
				imu->_onNewGyro(imu, tick);
			}
		}
	}

	if((tick - imu->LastTempTick) >= imu->_dataInteval)
	{
		lsm6dso_temp_flag_data_ready_get(&dev_ctx, &reg);
		if(reg)
		{
			/* Read temperature data */
			memset(&data_raw_temperature, 0x00, sizeof(int16_t));
			lsm6dso_temperature_raw_get(&dev_ctx, &data_raw_temperature);
			imu->Temp = lsm6dso_from_lsb_to_celsius(data_raw_temperature);

			imu->LastTempTick += imu->_dataInteval;
			if(imu->_onNewTemp)
			{
				imu->_onNewTemp(imu, tick);
			}
		}
	}
}