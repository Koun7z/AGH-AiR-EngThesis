#ifndef HAL_TIME_H__
#define HAL_TIME_H__

#include "stdint.h"
#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim2;
extern volatile uint32_t TIME_us_overflow_cnt;

static inline void SYS_Time_Init(void)
{
	TIME_us_overflow_cnt = 0;

	htim2.Instance->SR = ~(TIM_SR_UIF);  // Clear update interrupt flag
	HAL_TIM_Base_Start_IT(&htim2);
}

static inline uint32_t SYS_Tick_ms(void)
{
	return uwTick;
}

static inline uint32_t SYS_Tick_us(void)
{
	return htim2.Instance->CNT;
}

static inline int64_t SYS_Tick_us_i64(void)
{
	return (int64_t)((uint64_t)TIME_us_overflow_cnt << 32 | (uint32_t)htim2.Instance->CNT);
}

#endif /* HAL_TIME_H__ */