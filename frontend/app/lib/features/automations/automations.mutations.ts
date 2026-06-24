// automations.mutations.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createAutomation,
  updateAutomation,
  deleteAutomation,
  publishAutomation,
} from "./automations.api";
import { automationKeys } from "./automations.keys";
import type { Automation, CreateAutomationDTO, UpdateAutomationDTO } from "./automations.types";

export function useAutomationMutations() {
  const queryClient = useQueryClient();

  return {
    createMutation: useMutation({
      mutationFn: (data: CreateAutomationDTO) => createAutomation(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: automationKeys.all });
      },
    }),

    updateMutation: useMutation({
      mutationFn: ({ id, data }: { id: string; data: UpdateAutomationDTO }) =>
        updateAutomation(id, data),
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries({ queryKey: automationKeys.detail(variables.id) });
        queryClient.invalidateQueries({ queryKey: automationKeys.all });
      },
    }),

    publishMutation: useMutation({
      mutationFn: (automationId: string) => publishAutomation(automationId),
      onSuccess: (_, automationId) => {
        queryClient.invalidateQueries({ queryKey: automationKeys.detail(automationId)})
      }
    })
  };
}