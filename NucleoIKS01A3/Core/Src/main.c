/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2026 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

#include "IMU.h"
#include "Config.h"
#include "Time.h"
#include "DSP_AHRS_NC.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */


/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

static IMU_Handle himu;
static DSP_AHRS_NC_Instance_f32 NC_Filter;
static DSP_AHRS_DataInstance_f32 AHRS_Data;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

int _write(int file, char* ptr, int len);

void OnNewAccData(IMU_Handle* imu, uint32_t tick);
void OnNewGyroData(IMU_Handle* imu, uint32_t tick);

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void)
{
	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_USART2_UART_Init();
	MX_I2C1_Init();
	MX_TIM2_Init();
	/* USER CODE BEGIN 2 */

	IMU_Init(&himu);
	IMU_CallbackSet(&himu, &OnNewAccData, &OnNewGyroData, NULL);

	// TODO: Move params to Config.h
	DSP_AHRS_NC_Init_f32(&NC_Filter, 0.1f, 0.0f, 0.9f, 0.1f, 0.2f);
	DSP_AHRS_DataInit_f32(&AHRS_Data);
	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while(1)
	{
		IMU_Update(&himu, SYS_Tick_ms());

		static uint32_t last_ahrs_tick = 0;
		if(SYS_Tick_ms() - last_ahrs_tick >= AHRS_UPDATE_INTERVAL_MS)
		{
			DSP_AHRS_NC_FilterUpdate_f32(&NC_Filter, &AHRS_Data, (AHRS_UPDATE_INTERVAL_MS / 1000.0f));
			last_ahrs_tick += AHRS_UPDATE_INTERVAL_MS;

			printf("FC_Attitude: %0.8f, %0.8f, %0.8f, %0.8f\r\n", AHRS_Data.AttitudeEstimate.r,
			  AHRS_Data.AttitudeEstimate.i, AHRS_Data.AttitudeEstimate.j, AHRS_Data.AttitudeEstimate.k);

			// printf("$%0.2f %0.2f %0.2f;\r\n", AHRS_Data.GyroData[0], AHRS_Data.GyroData[1], AHRS_Data.GyroData[2]);
		}


		static uint32_t updt_cnt      = 0;
		static uint32_t last_log_tick = 0;
		const uint32_t interval_ms    = 1000;

		updt_cnt++;
		const uint32_t loop_end_tick = SYS_Tick_ms();
		if(loop_end_tick - last_log_tick >= interval_ms)
		{
			last_log_tick = loop_end_tick;

			printf("UPS: %0.2f\r\n", (float)updt_cnt / (interval_ms / 1000.0f));
			updt_cnt = 0;
		}
	}

	/* USER CODE END WHILE */

	/* USER CODE BEGIN 3 */
}
/* USER CODE END 3 */


/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void)
{
	RCC_OscInitTypeDef RCC_OscInitStruct = {0};
	RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

	/** Configure the main internal regulator output voltage
	 */
	__HAL_RCC_PWR_CLK_ENABLE();
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSIState            = RCC_HSI_ON;
	RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
	RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSI;
	RCC_OscInitStruct.PLL.PLLM            = 8;
	RCC_OscInitStruct.PLL.PLLN            = 100;
	RCC_OscInitStruct.PLL.PLLP            = RCC_PLLP_DIV2;
	RCC_OscInitStruct.PLL.PLLQ            = 4;
	if(HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
	{
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

	if(HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
	{
		Error_Handler();
	}
}

/* USER CODE BEGIN 4 */

int _write(int file, char* ptr, int len)
{
	HAL_UART_Transmit(&huart2, (uint8_t*)ptr, len, HAL_MAX_DELAY);
	return len;
}

void OnNewAccData(IMU_Handle* imu, uint32_t tick)
{
	DSP_AHRS_UpdateAccData_f32(&AHRS_Data, imu->Acc);
}

void OnNewGyroData(IMU_Handle* imu, uint32_t tick)
{
	DSP_AHRS_UpdateGyroData_f32(&AHRS_Data, imu->Gyro);
}

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void)
{
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while(1)
	{
	}
	/* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t* file, uint32_t line)
{
	/* USER CODE BEGIN 6 */
	/* User can add his own implementation to report the file name and line number,
	   ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
	/* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
