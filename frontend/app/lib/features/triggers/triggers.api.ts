import { api } from "@/lib/api-client";

export const createTrigger = async (automationId: string, data: any) => {
  const res = await api.post(`/automations/${automationId}/triggers/`, data);
  return res.data;
};

export const updateTrigger = async (automationId: string, triggerId: string, data: any) => {
  const res = await api.patch(`/automations/${automationId}/triggers/${}`)
}

export const testTrigger = async (triggerId: string) => {
  const res = await api.post(`/automations/triggers/${triggerId}/test/`);
  return res.data;
};