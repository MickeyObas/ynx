"use client";

import { useQuery } from "@tanstack/react-query";
import { automationKeys } from "./automations.keys";
import { getAutomation, getAutomations } from "./automations.api";
import { AutomationQueryParams } from "./automations.types";

export function useAutomations(params?: AutomationQueryParams) {
  return useQuery({
    queryKey: automationKeys.list(params),
    queryFn: () => getAutomations(params),
  });
}

export function useAutomation(id: string) {
  return useQuery({
    queryKey: automationKeys.detail(id),
    queryFn: () => getAutomation(id)
  })
}