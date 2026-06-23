import { Trigger } from "../triggers/triggers.types";

export interface Automation {
  id: string;
  workspace: string;
  name: string;
  description: string | null;
  owner: string;
  status: AutomationStatus;
  trigger: Trigger | null;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export type AutomationQueryParams = {
  workspace_id?: string;
  status?: string;
};

export type AutomationStatus =
  | "draft"
  | "active"
  | "paused"
  | "error";

export interface CreateAutomationDTO {
  workspace_id: string,
  name: string;
  description?: string;
}

export interface UpdateAutomationDTO {
  name?: string;
  description?: string;
}