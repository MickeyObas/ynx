"use client";

import { useEffect } from "react";
import { useWorkspaceStore } from "@/lib/features/workspaces/workspace.store";

export function WorkspaceInitializer() {
  const fetchActiveWorkspace = useWorkspaceStore(
    (s) => s.fetchActiveWorkspace
  );

  useEffect(() => {
    console.log("Running the effect");
    fetchActiveWorkspace();
  }, [fetchActiveWorkspace]);

  return null;
}