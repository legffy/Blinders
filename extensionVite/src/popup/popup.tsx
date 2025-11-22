import "../index.css";

export default function Popup() {
  return (
    <div className="p-4 w-72">
      <h1 className="text-lg font-bold">Blinders</h1>
      <p className="text-sm opacity-70">Popup is alive.</p>
    </div>
  );
}

import { createRoot } from "react-dom/client";
const root = createRoot(document.getElementById("root")!);
root.render(<Popup />);
