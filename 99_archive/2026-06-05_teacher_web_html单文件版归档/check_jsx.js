#!/usr/bin/env node
/* check_jsx.js — 老师网页 index.html 的 JSX 语法检查器
 *
 * 这个网页没有常规构建工具，靠浏览器里的 babel.min.js 现场把 JSX 编译成 JS。
 * 命令行没法直接发现语法错，只有打开浏览器才报。本脚本用项目自带的
 * src/vendor/babel.min.js，在命令行把 index.html 里每段 <script type="text/babel">
 * 逐个编译一遍，哪段语法错就报哪段（按 data-source 标签定位）。
 *
 * 用法：node check_jsx.js
 * 返回码：0 = 全过，1 = 有语法错（可接 CI / 改完即跑）
 */
const fs = require("fs");
const path = require("path");
const Babel = require("./src/vendor/babel.min.js");

const htmlPath = path.join(__dirname, "src/index.html");
const html = fs.readFileSync(htmlPath, "utf8");

// 抓所有 <script type="text/babel" ...>BODY</script>（非贪婪，停在第一个 </script>）
const re = /<script type="text\/babel"([^>]*)>([\s\S]*?)<\/script>/g;
let m;
let total = 0;
let failed = 0;
while ((m = re.exec(html)) !== null) {
  total += 1;
  const attrs = m[1] || "";
  const srcMatch = attrs.match(/data-source="([^"]*)"/);
  const label = srcMatch ? srcMatch[1] : `block#${total}`;
  const code = m[2];
  try {
    Babel.transform(code, { presets: ["react"], filename: label });
  } catch (e) {
    failed += 1;
    const firstLine = String(e.message).split("\n")[0];
    console.error(`❌ ${label}: ${firstLine}`);
  }
}

console.log(`\n检查 ${total} 个 JSX 块，${failed} 个语法错误`);
process.exit(failed > 0 ? 1 : 0);
