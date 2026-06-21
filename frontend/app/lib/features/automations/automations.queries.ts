"use client";

import { useQuery } from "@tanstack/react-query";
import { automationKeys } from "./automations.keys";
import { getAutomations } from "./automations.api";
import { AutomationQueryParams } from "./automations.types";

export function useAutomations(params?: AutomationQueryParams) {
  return useQuery({
    queryKey: automationKeys.list(params),
    queryFn: () => getAutomations(params),
  });
}