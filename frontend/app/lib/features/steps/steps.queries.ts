import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { stepKeys } from "./steps.keys";
import { createStep, deleteStep, getStep, getSteps, updateStep } from "./steps.api";

export function useSteps(automationId: string) {
  return useQuery({
    queryKey: stepKeys.all(automationId),
    queryFn: () => getSteps(automationId)
  })
}

export function useStep(automationId: string, stepId: string) {
  return useQuery({
    queryKey: stepKeys.detail(stepId),
    queryFn: () => getStep(automationId, stepId)
  })
}

