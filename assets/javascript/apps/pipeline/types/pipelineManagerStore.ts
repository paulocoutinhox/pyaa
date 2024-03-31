import {Edge, Node, Viewport} from "reactflow";
import {PipelineType} from "./pipeline";

export type PipelineManagerStoreType = {
  currentPipeline: PipelineType | undefined;
  currentPipelineId: number | undefined;
  loadPipeline: (pipelineId: number) => void;
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  savePipeline: (pipelne: PipelineType, silent?: boolean) => Promise<void>;
  autoSaveCurrentPipline: (
    nodes: Node[],
    edges: Edge[],
    viewport: Viewport
  ) => void;
};
