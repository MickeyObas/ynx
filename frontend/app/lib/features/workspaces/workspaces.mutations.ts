import { useMutation } from "@tanstack/react-query";
import { switchActiveWorkspace } from "./workspaces.api";
import { useWorkspaceStore } from "./workspace.store";
import { Workspace } from "./workspaces.types";

export function useSwitchWorkspaceMutation() {
  return useMutation({
    mutationFn: (workspace: Workspace) => switchActiveWorkspace(workspace.id),
    onSuccess: (data) => {
      useWorkspaceStore
        .getState()
        .setActiveWorkspace(data.workspace)
    }
  })
}