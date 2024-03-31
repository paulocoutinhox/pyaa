import {Handle, Node, NodeProps, NodeToolbar, Position} from 'reactflow';
import React, {useState} from "react";
import {classNames} from "./utils";
import usePipelineStore from "./stores/pipelineStore";

type NodeData = {
  label: string,
  value: number;
};

export type PipelineNode = Node<NodeData>;

export function PipelineNode({id, data, selected}: NodeProps<NodeData>) {
  const [value, setValue] = useState(data?.value ?? 0)
  const setNode = usePipelineStore((state) => state.setNode);
  const deleteNode = usePipelineStore((state) => state.deleteNode);

  const updateValue = () => {
    const newValue = value + 1;
    setValue(newValue);
    setNode(id, (old) => ({
      ...old,
      data: {
        ...old.data,
        value: newValue,
      },
    }));
  }

  return (
    <>
      <NodeToolbar position={Position.Top}>
        <div className="join">
          <button className="btn btn-xs join-item" onClick={() => deleteNode(id)}>
            <i className="fa fa-trash-o"></i>
          </button>
        </div>
      </NodeToolbar>
      <div className={classNames(
        selected ? "border border-primary" : "border",
        "w-32 rounded relative flex flex-col justify-center bg-base-100"
      )}>
        <Handle type="target" position={Position.Left} id="input"/>
        <div className="m-1 text-center">{data.label}</div>
        <div className="m-1 text-center">{value}</div>
        <div className="btn btn-xs" onClick={() => updateValue()}>+</div>
        <Handle type="source" position={Position.Right} id="output"/>
      </div>
    </>
  )
}
