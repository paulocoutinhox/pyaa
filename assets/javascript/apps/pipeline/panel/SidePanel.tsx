import React from "react";
import PanelGroup from "./PanelGroup";
import Component from "./Component";

const groupedComponents = [
  {
    "label": "Inputs", "components": [
      {"label": "File", "type": "file"},
    ]
  },
  {
    "label": "Steps", "components": [
      {"label": "LLM", "type": "llm"},
    ]
  }
]


export default function SidePanel() {
  function onDragStart(
    event: React.DragEvent<any>,
    data: { type: string, label: string }
  ): void {
    event.dataTransfer.setData("nodedata", JSON.stringify(data));
  }

  return (
    <div className="join join-vertical w-full">
      {groupedComponents.map((group) => (
        <PanelGroup name={group.label} key={group.label}>
          {group.components.map((component) => (
            <Component
              key={component.label + group.label}
              label={component.label}
              onDragStart={(event) =>
                onDragStart(event, {
                  label: component.label,
                  type: component.type,
                })
              }/>
          ))}
        </PanelGroup>
      ))}
    </div>
  )
}
