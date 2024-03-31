import React, {DragEventHandler} from "react";

export default function Component({label, onDragStart}: {label: string, onDragStart: DragEventHandler<HTMLDivElement>}) {
  return (
    <div draggable={true} onDragStart={onDragStart}>
      <div className="border p-1 rounded">{label}</div>
    </div>
  )
}
