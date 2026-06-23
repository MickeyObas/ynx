"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useWorkspaces } from "@/lib/features/workspaces/workspaces.queries";
import { useWorkspaceStore } from "@/lib/features/workspaces/workspace.store";
import { switchWorkspaceMutation, useSwitchWorkspaceMutation } from "@/lib/features/workspaces/workspaces.mutations";

// Dummy types
type Workspace = {
  id: string;
  name: string;
  role: "owner" | "admin" | "member";
};

const dummyWorkspaces: Workspace[] = [
  { id: "1", name: "Personal Automation", role: "owner" },
  { id: "2", name: "Company Workflows", role: "admin" },
  { id: "3", name: "Client Projects", role: "member" },
];

export default function WorkspacesPage() {
  const router = useRouter();
  const { data: workspaces } = useWorkspaces(); 
  const switchWorkspaceMutation = useSwitchWorkspaceMutation();

  const activeWorkspace = useWorkspaceStore((s) => s.activeWorkspace);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold">Workspaces</h1>
        <p>Active --- {activeWorkspace?.name}</p>
        <p className="text-sm text-gray-500">
          Switch between your workspaces
        </p>
      </div>

      {/* List */}
      <div className="grid gap-3">
        {workspaces?.map((ws: Workspace) => {
          const isActive = ws.id === activeWorkspace?.id;

          return (
            <div
              key={ws.id}
              className={`p-4 border rounded-xl bg-white flex items-center justify-between transition ${
                isActive ? "border-black" : ""
              }`}
            >
              {/* Left */}
              <div>
                <div className="font-medium flex items-center gap-2">
                  {ws.name}

                  {isActive && (
                    <span className="text-xs px-2 py-1 rounded-full bg-black text-white">
                      Active
                    </span>
                  )}
                </div>

                <div className="text-sm text-gray-500 capitalize">
                  {ws.role}
                </div>
              </div>

              {/* Right */}
              <div className="flex items-center gap-2">
                {!isActive ? (
                  <button
                    onClick={() => switchWorkspaceMutation.mutate(ws)}
                    className="px-3 py-1.5 text-sm rounded-lg border hover:bg-gray-50"
                  >
                    Switch
                  </button>
                ) : (
                  <button
                    onClick={() => router.push("/dashboard")}
                    className="px-3 py-1.5 text-sm rounded-lg bg-black text-white"
                  >
                    Enter
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}