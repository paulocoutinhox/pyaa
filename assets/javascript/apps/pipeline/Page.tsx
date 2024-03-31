import React from "react";
import Pipeline from "./Pipeline";
import SidePanel from "./panel/SidePanel";

export default function Page() {
  return (
    <div className="flex h-full overflow-hidden">
      <div className="flex flex-1">
        <div className="h-full w-full">
          <div id="react-flow-id" className="h-full w-full">
            <Pipeline/>
          </div>
        </div>
      </div>
      <div>
        <SidePanel/>
      </div>
    </div>
  )
}
