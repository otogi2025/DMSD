import React from "react";
import ReactDOM from "react-dom/client";

// 阶段1 占位入口 —— 验证 Vite + TypeScript 构建链跑通。
// 阶段4 会替换成真正的 <App />。
function Placeholder() {
  return (
    <div style={{ padding: 40, fontFamily: "sans-serif", color: "#14171f" }}>
      Tomoshibi Vite 骨架 OK
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Placeholder />
  </React.StrictMode>,
);
