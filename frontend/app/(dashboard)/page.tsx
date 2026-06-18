"use client";

import { useAutomations } from "@/lib/react-query/queries/useAutomations";
import { useRouter } from "next/navigation";

export default function DashboardHome() {
  const router = useRouter();
  const { data, isLoading, error } = useAutomations();

  const automations = data || [];

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

        <button className="px-4 py-2 bg-black text-white rounded-lg text-sm hover:bg-gray-800">
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
              <div className="font-medium text-gray-900">
                {a.name}
              </div>

              <span className="text-xs px-2 py-1 rounded-full bg-gray-100">
                {a.status}
              </span>
            </div>

            <div className="text-sm text-gray-500 mt-1">
              {a.description || "No description"}
            </div>

            {/* Trigger preview */}
            {a.trigger && (
              <div className="text-xs text-gray-400 mt-2">
                Trigger: {a.trigger.name || "Configured"}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}