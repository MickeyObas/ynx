"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

/* -------------------------
   API FUNCTIONS (inline for simplicity)
--------------------------*/

const getAutomation = async (id: string) => {
  const res = await api.get(`/automations/${id}/`);
  return res.data;
};

const getSteps = async (id: string) => {
  const res = await api.get(`/automations/${id}/steps/`);
  return res.data;
};

const createStep = async (id: string, data: any) => {
  const res = await api.post(`/automations/${id}/steps/`, data);
  return res.data;
};

const deleteStep = async (id: string, stepId: string) => {
  await api.delete(`/automations/${id}/steps/${stepId}/`);
};

const createTrigger = async (id: string, data: any) => {
  const res = await api.post(`/automations/${id}/triggers/`, data);
  return res.data;
};

const testTrigger = async (triggerId: string) => {
  const res = await api.post(`/automations/triggers/${triggerId}/test/`);
  return res.data;
};

const publishAutomation = async (id: string) => {
  const res = await api.post(`/automations/${id}/publish/`);
  return res.data;
};

/* -------------------------
   PAGE
--------------------------*/

export default function AutomationBuilderPage() {
  const params = useParams();
  const id = params.id as string;
  const queryClient = useQueryClient();

  /* -------------------------
     DATA
  --------------------------*/

  const { data: automation } = useQuery({
    queryKey: ["automation", id],
    queryFn: () => getAutomation(id),
  });

  const { data: steps } = useQuery({
    queryKey: ["steps", id],
    queryFn: () => getSteps(id),
  });

  /* -------------------------
     MUTATIONS
  --------------------------*/

  const createStepMutation = useMutation({
    mutationFn: (data: any) => createStep(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["steps", id] });
    },
  });

  const deleteStepMutation = useMutation({
    mutationFn: (stepId: string) => deleteStep(id, stepId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["steps", id] });
    },
  });

  const createTriggerMutation = useMutation({
    mutationFn: (data: any) => createTrigger(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation", id] });
    },
  });

  const publishMutation = useMutation({
    mutationFn: () => publishAutomation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation", id] });
    },
  });

  /* -------------------------
     UI
  --------------------------*/

  if (!automation) {
    return <div className="p-6">Loading...</div>;
  }

  const trigger = automation.trigger;

  return (
    <div className="p-6 space-y-6">

      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-semibold">
          {automation.name}
        </h1>

        <p className="text-sm text-gray-500">
          {automation.description}
        </p>
      </div>

      {/* ---------------- TRIGGER ---------------- */}
      <section className="border rounded-xl p-4 bg-white">
        <h2 className="font-medium mb-3">Trigger</h2>

        {trigger ? (
          <div className="space-y-2">
            <div className="text-sm">
              Type: {trigger.type}
            </div>

            <div className="text-sm text-gray-500">
              Integration: {trigger.integration_id}
            </div>

            <button
              onClick={() => testTrigger(trigger.id)}
              className="text-sm px-3 py-1 bg-gray-100 rounded"
            >
              Test Trigger
            </button>
          </div>
        ) : (
          <button
            onClick={() =>
              createTriggerMutation.mutate({
                type: "WEBHOOK",
                integration_id: "demo",
                connection_id: "demo",
                trigger_key: "default",
                config: {},
              })
            }
            className="px-3 py-2 bg-black text-white rounded"
          >
            Configure Trigger
          </button>
        )}
      </section>

      {/* ---------------- STEPS ---------------- */}
      <section className="border rounded-xl p-4 bg-white">
        <div className="flex justify-between mb-3">
          <h2 className="font-medium">Steps</h2>

          <button
            onClick={() =>
              createStepMutation.mutate({
                automation: id,
                kind: "ACTION",
                order: (steps?.length || 0) + 1,
                action_name: "new_step",
                config: {},
              })
            }
            className="text-sm px-3 py-1 bg-black text-white rounded"
          >
            + Add Step
          </button>
        </div>

        <div className="space-y-2">
          {steps?.map((step: any) => (
            <div
              key={step.id}
              className="border rounded p-3 flex justify-between"
            >
              <div>
                <div className="text-sm font-medium">
                  {step.action_name}
                </div>

                <div className="text-xs text-gray-500">
                  {step.kind}
                </div>
              </div>

              <button
                onClick={() =>
                  deleteStepMutation.mutate(step.id)
                }
                className="text-xs text-red-500"
              >
                delete
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* ---------------- PUBLISH ---------------- */}
      <section className="border rounded-xl p-4 bg-white">
        <h2 className="font-medium mb-3">
          Publish Workflow
        </h2>

        <button
          onClick={() => publishMutation.mutate()}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Publish Automation
        </button>
      </section>

    </div>
  );
}