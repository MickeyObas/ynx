import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createTrigger, updateTrigger } from "./triggers.api"

export const useTriggerMutations = (automationId: string) => {
  const queryClient = useQueryClient();

  return {
    createMutation: useMutation({
      mutationFn: (data: any) => createTrigger(automationId, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["automation", automationId] });
      },      
    }),

    updateMutation: useMutation({
      mutationFn: ({ triggerId, data }: {triggerId: string, data: any}) => updateTrigger(automationId, triggerId, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["automation", automationId] });
      }
    })
  }
}