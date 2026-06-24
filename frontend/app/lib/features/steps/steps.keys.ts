import { automationKeys } from "../automations/automations.keys";


export const stepKeys = {
  all: (automationId: string) => [automationKeys.detail(automationId), 'steps'] as const,
  detail: (stepId: string) => ['steps', stepId] as const
}