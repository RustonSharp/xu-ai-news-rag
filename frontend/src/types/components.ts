// 组件相关类型定义
import { ReactNode } from 'react'

// 基础组件 Props
export interface BaseComponentProps {
  className?: string
  children?: ReactNode
}

// 按钮组件 Props
export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

// Input component Props
export interface InputProps {
  type?: 'text' | 'email' | 'password' | 'search' | 'number'
  placeholder?: string
  value?: string
  defaultValue?: string
  disabled?: boolean
  required?: boolean
  className?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  onFocus?: () => void
}

// Modal component Props
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  closable?: boolean
}

// 表格列定义
export interface TableColumn<T = any> {
  key: string
  title: string
  dataIndex?: keyof T
  width?: number | string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  render?: (value: any, record: T, index: number) => ReactNode
}

// 表格组件 Props
export interface TableProps<T = any> extends BaseComponentProps {
  columns: TableColumn<T>[]
  data: T[]
  loading?: boolean
  pagination?: PaginationProps
  rowKey?: keyof T | ((record: T) => string | number)
  onRowClick?: (record: T, index: number) => void
}

// 分页组件 Props
export interface PaginationProps {
  current: number
  total: number
  pageSize: number
  showSizeChanger?: boolean
  showQuickJumper?: boolean
  onChange: (page: number, pageSize: number) => void
}

// 标签组件 Props
export interface TagProps extends BaseComponentProps {
  color?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  closable?: boolean
  onClose?: () => void
}

// 卡片组件 Props
export interface CardProps extends BaseComponentProps {
  title?: string
  extra?: ReactNode
  bordered?: boolean
  hoverable?: boolean
}

// 加载组件 Props
export interface LoadingProps {
  spinning?: boolean
  size?: 'small' | 'default' | 'large'
  tip?: string
  children?: ReactNode
}

// 表单项组件 Props
export interface FormItemProps extends BaseComponentProps {
  label?: string
  required?: boolean
  error?: string
  help?: string
}

// 选择器选项
export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

// 选择器组件 Props
export interface SelectProps {
  options: SelectOption[]
  value?: string | number
  defaultValue?: string | number
  placeholder?: string
  disabled?: boolean
  multiple?: boolean
  searchable?: boolean
  className?: string
  onChange?: (value: string | number | (string | number)[]) => void
}

// 搜索框组件 Props
export interface SearchBoxProps extends BaseComponentProps {
  placeholder?: string
  value?: string
  loading?: boolean
  onSearch: (value: string) => void
  onChange?: (value: string) => void
}