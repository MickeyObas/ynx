"use client"

import { useQuery } from "@tanstack/react-query";
import { workspaceKeys } from "./workspaces.keys";
import { getWorkspaces } from "./workspaces.api";

export function useWorkspaces() {
  return useQuery({
    queryKey: workspaceKeys.all,
    queryFn: () => getWorkspaces()
  })
}