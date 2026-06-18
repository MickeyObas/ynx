"use client";

import { useQuery } from "@tanstack/react-query";
import { getAutomations, AutomationQueryParams } from "@/lib/api/automations";

export function useAutomations(params?: AutomationQueryParams) {
  return useQuery({
    queryKey: ["automations", params],
    queryFn: () => getAutomations(params),
  });
}