import { create } from "zustand";
import { Workspace } from "./workspaces.types";
import { api } from "@/lib/api-client";


type WorkspaceStore = {
  activeWorkspace: Workspace | null;
  loading: boolean;

  setActiveWorkspace: (ws: Workspace) => void;
  setLoading: (v: boolean) => void;
  fetchActiveWorkspace: () => void
};


export const useWorkspaceStore = create<WorkspaceStore>((set, get) => ({
  activeWorkspace: null,
  workspaces: [],
  loading: true,

  setActiveWorkspace: (ws) => set({ activeWorkspace: ws }),
  setLoading: (v) => set({ loading: v }),

  fetchActiveWorkspace: async () => {
    set({ loading: true });

    try {
      const res = await api.get("/auth/me");
        if (res.status !== 200) throw new Error("Failed to fetch me");
        const data = res.data;
        set({
          activeWorkspace: data.active_workspace,
        });
      } catch (err) {
        console.error("Active workspace fetch failed:", err);
      } finally {
        set({ loading: false });
      }
    }
  }
));