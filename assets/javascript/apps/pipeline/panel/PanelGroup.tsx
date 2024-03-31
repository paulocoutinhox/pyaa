import React from "react";

export default function PanelGroup ({name, children}: {name: string, children: React.ReactNode}) {
  return (
    <div className="collapse collapse-arrow join-item border border-base-300 bg-base-200">
      <input type="checkbox"/>
      <div className="collapse-title">{name}</div>
      <div className="collapse-content">
        {children}
      </div>
    </div>
  )
}
