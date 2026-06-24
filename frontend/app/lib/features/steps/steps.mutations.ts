import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createStep, deleteStep, updateStep } from "./steps.api";
import { stepKeys } from "./steps.keys";

export function useStepMutations(automationId: string) {
  const queryClient = useQueryClient();

  return {
    createMutation: useMutation({
      mutationFn: (data: any) => createStep(automationId, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: stepKeys.all(automationId) });
      },
    }),
    updateMutation: useMutation({
      mutationFn: ({ stepId, data }: { stepId: string, data: any }) => updateStep(automationId, stepId, data),
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries({ queryKey: stepKeys.detail(variables.stepId) });
        queryClient.invalidateQueries({ queryKey: stepKeys.all(automationId) });
      },
    }),
    deleteMutation: useMutation({
      mutationFn: (stepId: string) => deleteStep(automationId, stepId),
      onSuccess: (_, stepId) => {
        queryClient.invalidateQueries({ queryKey: stepKeys.all(automationId) });
        queryClient.removeQueries({ queryKey: stepKeys.detail(stepId) });
      },
    }),
  }
}