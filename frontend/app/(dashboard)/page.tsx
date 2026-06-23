"use client";

import { useWorkspaceStore } from "@/lib/features/workspaces/workspace.store";
import React from "react";

type Execution = {
  id: string;
  workflowName: string;
  status: "success" | "failed" | "running";
  duration: string;
  time: string;
};

type Workflow = {
  id: string;
  name: string;
  triggers: number;
  lastRun: string;
  enabled: boolean;
};

// --------------------
// Dummy Data
// --------------------

const stats = [
  { label: "Total Executions", value: "1,284" },
  { label: "Success Rate", value: "96.4%" },
  { label: "Active Workflows", value: "12" },
  { label: "Failed Runs", value: "18" },
];

const recentExecutions: Execution[] = [
  {
    id: "1",
    workflowName: "Email Welcome Flow",
    status: "success",
    duration: "2.1s",
    time: "2 mins ago",
  },
  {
    id: "2",
    workflowName: "Slack Notification",
    status: "failed",
    duration: "1.4s",
    time: "10 mins ago",
  },
  {
    id: "3",
    workflowName: "CRM Sync",
    status: "running",
    duration: "—",
    time: "Just now",
  },
  {
    id: "4",
    workflowName: "Daily Report Generator",
    status: "success",
    duration: "5.8s",
    time: "1 hour ago",
  },
];

const workflows: Workflow[] = [
  {
    id: "w1",
    name: "Email Welcome Flow",
    triggers: 3,
    lastRun: "2 mins ago",
    enabled: true,
  },
  {
    id: "w2",
    name: "Slack Alerts",
    triggers: 5,
    lastRun: "10 mins ago",
    enabled: false,
  },
  {
    id: "w3",
    name: "Analytics Pipeline",
    triggers: 2,
    lastRun: "1 hour ago",
    enabled: true,
  },
];

// --------------------
// UI Helpers
// --------------------

const statusColor = (status: Execution["status"]) => {
  switch (status) {
    case "success":
      return "text-green-600 bg-green-50";
    case "failed":
      return "text-red-600 bg-red-50";
    case "running":
      return "text-yellow-600 bg-yellow-50";
  }
};

// --------------------
// Component
// --------------------

export default function DashboardPage() {

  const activeWorkspace = useWorkspaceStore((state) => state.activeWorkspace);
  console.log("Active Workspace: ", activeWorkspace);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p>Active --- {activeWorkspace?.name} </p>
        <p className="text-gray-500 text-sm">
          Monitor workflows, executions, and system health in real time.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white p-4 rounded-xl border shadow-sm"
          >
            <p className="text-gray-500 text-sm">{stat.label}</p>
            <p className="text-xl font-semibold">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Executions */}
        <div className="lg:col-span-2 bg-white rounded-xl border shadow-sm p-4">
          <h2 className="font-semibold mb-4">Recent Executions</h2>

          <div className="space-y-3">
            {recentExecutions.map((exec) => (
              <div
                key={exec.id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50"
              >
                <div>
                  <p className="font-medium">{exec.workflowName}</p>
                  <p className="text-xs text-gray-500">{exec.time}</p>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500">
                    {exec.duration}
                  </span>

                  <span
                    className={`text-xs px-2 py-1 rounded-full ${statusColor(
                      exec.status
                    )}`}
                  >
                    {exec.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-xl border shadow-sm p-4">
            <h2 className="font-semibold mb-3">Quick Actions</h2>

            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
                + Create Workflow
              </button>
              <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
                View Logs
              </button>
              <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
                Manage Integrations
              </button>
            </div>
          </div>

          {/* System Health */}
          <div className="bg-white rounded-xl border shadow-sm p-4">
            <h2 className="font-semibold mb-3">System Health</h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span>API Status</span>
                <span className="text-green-600">Operational</span>
              </div>

              <div className="flex justify-between">
                <span>Queue</span>
                <span className="text-yellow-600">Normal load</span>
              </div>

              <div className="flex justify-between">
                <span>Workers</span>
                <span className="text-green-600">Healthy</span>
              </div>
            </div>
          </div>

          {/* Active Workflows */}
          <div className="bg-white rounded-xl border shadow-sm p-4">
            <h2 className="font-semibold mb-3">Active Workflows</h2>

            <div className="space-y-3">
              {workflows.map((wf) => (
                <div
                  key={wf.id}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-sm">{wf.name}</p>
                    <p className="text-xs text-gray-500">
                      Last run {wf.lastRun}
                    </p>
                  </div>

                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      wf.enabled
                        ? "bg-green-50 text-green-600"
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {wf.enabled ? "ON" : "OFF"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}