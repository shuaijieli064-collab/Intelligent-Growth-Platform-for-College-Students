/**
 * HTML 转义 —— 用于 ECharts tooltip formatter 等 HTML 字符串拼接场景。
 * tooltip 默认 renderMode 为 'html'，未转义的用户数据会导致存储型 XSS。
 */
export function escapeHtml(input: unknown): string {
  if (input === null || input === undefined) return ''
  return String(input)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/** 安全的 http(s) URL 校验，拒绝 javascript: 等危险协议 */
export function isSafeUrl(url: unknown): boolean {
  if (typeof url !== 'string' || !url) return false
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}
