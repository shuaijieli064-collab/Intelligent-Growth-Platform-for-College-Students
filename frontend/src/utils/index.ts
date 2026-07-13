export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

export const getGenderText = (gender: string): string => {
  return gender === 'M' ? '男' : '女'
}
