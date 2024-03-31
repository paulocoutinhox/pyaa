import {Edge, Node, Viewport} from "reactflow";
import {create} from "zustand";
import {PipelineType} from "../types/pipeline";
import {PipelineManagerStoreType} from "../types/pipelineManagerStore";
import {apiClient} from "../api/api";

let saveTimeoutId: NodeJS.Timeout | null = null;

const usePipelineManagerStore = create<PipelineManagerStoreType>((set, get) => ({
  currentPipeline: undefined,
  currentPipelineId: undefined,
  loadPipeline: async (pipelineId: number) => {
    set({isLoading: true});
    apiClient.getPipeline(pipelineId).then((pipeline) => {
      if (pipeline) {
        set({currentPipeline: pipeline, currentPipelineId: pipelineId});
        set({isLoading: false});
      }
    }).catch((e) => {
      console.log(e);
    });
  },
  isLoading: true,
  setIsLoading: (isLoading: boolean) => set({isLoading}),
  autoSaveCurrentPipline: (nodes: Node[], edges: Edge[], viewport: Viewport) => {
    // Clear the previous timeout if it exists.
    if (saveTimeoutId) {
      clearTimeout(saveTimeoutId);
    }

    // Set up a new timeout.
    saveTimeoutId = setTimeout(() => {
      if (get().currentPipeline) {
        get().savePipeline(
          {...get().currentPipeline!, data: {nodes, edges, viewport}},
          true
        );
      }
    }, 300); // Delay of 300ms.
  },
  savePipeline: (pipeline: PipelineType) => {
    return new Promise<void>((resolve, reject) => {
      apiClient.updatePipeline(get().currentPipelineId!, pipeline)
        .then((updatedFlow) => {
          if (updatedFlow) {
            resolve();
          }
        })
        .catch((err) => {
          console.log(err);
          reject(err);
        });
    });
  },
}));

export default usePipelineManagerStore;
