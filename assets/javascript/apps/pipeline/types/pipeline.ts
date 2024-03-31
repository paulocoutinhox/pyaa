import {ReactFlowJsonObject} from "reactflow";

export type PipelineType = {
  id: bigint;
  team: string;
  name: string;
  data: ReactFlowJsonObject | null;
  description: string;
  date_created?: string;
  updated_at?: string;
};
