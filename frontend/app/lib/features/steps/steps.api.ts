import { api } from "@/lib/api-client";

export const getSteps = async (automationId: string) => {
  const res = await api.get(`/automations/${automationId}/steps/`);
  return res.data;
};

export const getStep = async (automationId: string, stepId: string) => {
  const res = await api.get(`/automations/${automationId}/steps/${stepId}`);
  return res.data;
};

export const createStep = async (automationId: string, data: any) => {
  const res = await api.post(`/automations/${automationId}/steps/`, data);
  return res.data;
};

export const updateStep = async (automationId: string, stepId: string, data: any) => {
  const res = await api.patch(`/automations/${automationId}/steps/${stepId}`, data);
  return res.data;
}

export const deleteStep = async (automationId: string, stepId: string) => {
  await api.delete(`/automations/${automationId}/steps/${stepId}/`);
};