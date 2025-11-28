export * from './auth';
export * from './catalog';
export * from './providers';
export * from './orders';

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}
