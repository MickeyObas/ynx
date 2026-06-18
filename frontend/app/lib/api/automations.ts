import { api } from "./client";

export type AutomationQueryParams = {
  workspace_id?: string;
  status?: string;
};

export const getAutomations = async (params?: AutomationQueryParams) => {
  const res = await api.get("/automations/", {
    params,
  });

  return res.data;
};

export const getAutomation = async (id: string) => {
  const res = await api.get(`/automations/${id}/`);
  return res.data;
};

export const updateAutomation = async (id: string, data: any) => {
  const res = await api.patch(`/automations/${id}/`, data);
  return res.data;
};