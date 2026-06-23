"use client";

import { useState } from "react";
import { useAutomations } from "@/lib/features/automations/automations.queries";
import { useRouter } from "next/navigation";
import { useAutomationMutations } from "@/lib/features/automations/automations.mutations";


export default function Automations() {
  const router = useRouter();
  const { data, isLoading, error } = useAutomations();
  const { createMutation } = useAutomationMutations();

  const automations = data || [];

  // -----------------------
  // Modal State
  // -----------------------
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleNewAutomationClick = () => {
    setOpen(true);
    setName("");
    setDescription("");
    setFormError(null);
  };

  const handleCreate = () => {
    if (!name.trim()) {
      setFormError("Name is required");
      return;
    }

    setFormError(null);

    createMutation.mutate(
      { name, description },
      {
        onSuccess: (created) => {
          setOpen(false);
          router.push(`/automations/${created.id}`);
        },
        onError: (err) => {
          setFormError(err instanceof Error ? err.message : "Failed to create automation");
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Automations
          </h1>
          <p className="text-sm text-gray-500">
            Manage and monitor your workflows
          </p>
        </div>

        <button
          onClick={handleNewAutomationClick}
          className="px-4 py-2 bg-black text-white rounded-lg text-sm hover:bg-gray-800"
        >
          New Automation
        </button>
      </div>

      {/* States */}
      {isLoading && (
        <div className="text-sm text-gray-500">
          Loading automations...
        </div>
      )}

      {error && (
        <div className="text-sm text-red-500">
          Failed to load automations
        </div>
      )}

      {/* Empty state */}
      {!isLoading && automations.length === 0 && (
        <div className="border rounded-xl p-10 text-center text-sm text-gray-500 bg-white">
          No automations yet. Create your first workflow.
        </div>
      )}

      {/* List */}
      <div className="grid gap-3">
        {automations.map((a: any) => (
          <div
            key={a.id}
            onClick={() => router.push(`/automations/${a.id}`)}
            className="p-4 border rounded-xl bg-white hover:shadow-sm transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div className="font-medium text-gray-900">{a.name}</div>

              <span className="text-xs px-2 py-1 rounded-full bg-gray-100">
                {a.status}
              </span>
            </div>

            <div className="text-sm text-gray-500 mt-1">
              {a.description || "No description"}
            </div>

            {a.trigger && (
              <div className="text-xs text-gray-400 mt-2">
                Trigger: {a.trigger.name || "Configured"}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ----------------------- */}
      {/* MODAL */}
      {/* ----------------------- */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white w-full max-w-md rounded-xl p-6 space-y-4 shadow-lg">
            <h2 className="text-lg font-semibold">
              Create Automation
            </h2>

            {/* Name */}
            <div className="space-y-1">
              <label className="text-sm text-gray-600">Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. Welcome Email Flow"
              />
            </div>

            {/* Description */}
            <div className="space-y-1">
              <label className="text-sm text-gray-600">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Optional description"
              />
            </div>

            {/* Error */}
            {formError && (
              <p className="text-sm text-red-500">{formError}</p>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setOpen(false)}
                className="px-3 py-2 text-sm rounded-lg border"
              >
                Cancel
              </button>

              <button
                onClick={handleCreate}
                disabled={submitting}
                className="px-3 py-2 text-sm rounded-lg bg-black text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {submitting ? "Creating..." : "Create"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}