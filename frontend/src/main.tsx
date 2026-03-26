// main.tsx — Entry point của React app
// Vite đọc file này đầu tiên, render App vào DOM element có id="root"

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// StrictMode: chỉ active trong development
// Render component 2 lần để phát hiện side effects không pure
// (production build tự tắt, không ảnh hưởng performance)
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
