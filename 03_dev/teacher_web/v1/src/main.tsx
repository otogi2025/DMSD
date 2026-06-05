import React from "react";
import ReactDOM from "react-dom/client";
import "./fonts.css";
import "./styles.css";

// 阶段2 占位入口 —— 验证公共层（theme/api/css/字体）能编译打包。
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
