import { AutomationQueryParams } from "./automations.types";

export const automationKeys = {
  all: ['automations'] as const,
  list: (params?: AutomationQueryParams) => [...automationKeys.all, 'list', params] as const,
  detail: (id: string) => [...automationKeys.all, 'detail', id] as const,
}