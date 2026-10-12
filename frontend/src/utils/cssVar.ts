/**
 * 将 CSS 自定义属性（--xxx-rgb，值为 "R G B" 分量）转换为 ECharts/canvas 可用的颜色字符串。
 * canvas 的 fillStyle/strokeStyle 不解析 CSS 变量，必须读取计算值后拼接。
 * 主题切换后组件需重新调用（建议将 isDark 纳入 useMemo 依赖）。
 */
export function cssVarRgb(name: string, alpha?: number): string {
  if (typeof window === 'undefined') {
    return alpha !== undefined ? 'rgba(128, 128, 128, ' + alpha + ')' : 'rgb(128, 128, 128)'
  }
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  const parts = raw.split(/\s+/).filter(Boolean)
  if (parts.length >= 3) {
    if (alpha !== undefined) {
      return 'rgba(' + parts[0] + ', ' + parts[1] + ', ' + parts[2] + ', ' + alpha + ')'
    }
    return 'rgb(' + parts[0] + ', ' + parts[1] + ', ' + parts[2] + ')'
  }
  // 变量未定义时兜底灰色，避免 canvas 渲染成黑色
  return alpha !== undefined ? 'rgba(128, 128, 128, ' + alpha + ')' : 'rgb(128, 128, 128)'
}
