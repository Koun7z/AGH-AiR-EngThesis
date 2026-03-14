#include "Time.h"

volatile uint32_t TIME_us_overflow_cnt = 0;

/*
** Timers
*/

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef* htim)
{
	if(htim->Instance == TIM2)
	{
		TIME_us_overflow_cnt++;
	}
}


/*
** I2C
*/

void HAL_I2C_ErrorCallback(I2C_HandleTypeDef* hi2c)
{
	// printf("I2C Error Callback triggered: %d\r\n", hi2c->ErrorCode);
}