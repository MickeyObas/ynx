import { api } from "@/lib/api-client";

export const switchActiveWorkspace = async (id: string) => {
  const response = await api.patch("/workspaces/set-active/", {
    "workspaceId": id
  });
  return response.data;
};

export const getWorkspaces = async () => {
  const response = await api.get("/workspaces");
  return response.data;
}
