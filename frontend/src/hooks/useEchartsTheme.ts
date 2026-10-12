import { useMemo } from 'react'
import { useTheme } from './useTheme'
import type { EChartsOption } from 'echarts'

export function useEchartsTheme() {
  const { isDark } = useTheme()

  const baseOption = useMemo((): EChartsOption => {
    return {
      backgroundColor: 'transparent',
      textStyle: {
        color: isDark ? '#e4e4e4' : '#1a1a1a',
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: isDark ? 'rgba(33, 34, 38, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: isDark ? 'rgba(90, 95, 105, 0.6)' : 'rgba(232, 229, 225, 0.5)',
        borderWidth: 1,
        textStyle: {
          color: isDark ? '#e4e4e4' : '#1a1a1a',
        },
      },
      legend: {
        textStyle: {
          color: isDark ? '#c4c4c4' : '#555555',
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 40,
        containLabel: true,
      },
      xAxis: {
        axisLine: {
          lineStyle: {
            color: isDark ? 'rgba(140, 145, 155, 0.55)' : 'rgba(232, 229, 225, 0.5)',
          },
        },
        axisLabel: {
          color: isDark ? '#9aa0a6' : '#888888',
        },
        splitLine: {
          show: false,
        },
      },
      yAxis: {
        axisLine: {
          lineStyle: {
            color: isDark ? 'rgba(140, 145, 155, 0.55)' : 'rgba(232, 229, 225, 0.5)',
          },
        },
        axisLabel: {
          color: isDark ? '#9aa0a6' : '#888888',
        },
        splitLine: {
          lineStyle: {
            color: isDark ? 'rgba(255, 255, 255, 0.09)' : 'rgba(232, 229, 225, 0.3)',
          },
        },
      },
    }
  }, [isDark])

  const colors = useMemo(() => {
    return {
      primary: isDark ? '#f0c070' : '#d97706',
      success: isDark ? '#10b981' : '#059669',
      warning: isDark ? '#f59e0b' : '#d97706',
      danger: isDark ? '#f43f5e' : '#dc2626',
      info: isDark ? '#3b82f6' : '#2563eb',
      purple: isDark ? '#a78bfa' : '#9333ea',
      cyan: isDark ? '#22d3ee' : '#0891b2',
      pink: isDark ? '#f472b6' : '#db2777',
    }
  }, [isDark])

  const mergeOption = (option: EChartsOption): EChartsOption => {
    return {
      ...baseOption,
      ...option,
    }
  }

  return {
    isDark,
    baseOption,
    colors,
    mergeOption,
  }
}
