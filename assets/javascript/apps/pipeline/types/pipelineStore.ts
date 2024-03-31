import {Connection, Edge, Node, OnEdgesChange, OnNodesChange, ReactFlowInstance, Viewport,} from "reactflow";

export type PipelineStoreType = {
  reactFlowInstance: ReactFlowInstance | null;
  setReactFlowInstance: (newState: ReactFlowInstance) => void;
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  setNodes: (update: Node[] | ((oldState: Node[]) => Node[])) => void;
  setEdges: (update: Edge[] | ((oldState: Edge[]) => Edge[])) => void;
  setNode: (id: string, update: Node | ((oldState: Node) => Node)) => void;
  getNode: (id: string) => Node | undefined;
  deleteNode: (nodeId: string | Array<string>) => void;
  deleteEdge: (edgeId: string | Array<string>) => void;
  onConnect: (connection: Connection) => void;
  addNode: (
    node: any,
    position: { x: number; y: number; paneX?: number; paneY?: number }
  ) => void;
  resetFlow: (flow: {
    nodes: Node[];
    edges: Edge[];
    viewport: Viewport;
  }) => void;
};
