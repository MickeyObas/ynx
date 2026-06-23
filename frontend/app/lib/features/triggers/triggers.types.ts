export type TriggerType = "poll" | "schedule" | "webhook"; 

export interface Trigger {
  id: string;
  type: TriggerType;
  integration_id: string | null;
  trigger_key: string;
  config: Record<string, any>;
}