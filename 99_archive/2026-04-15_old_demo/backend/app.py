# DMSD 宿舍点呼 Demo 后端 —— 只用于 2026-04-15 演示
# 用 Flask 做最简实现：内存字典存签到记录，不接数据库

import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# 创建 Flask 应用实例
app = Flask(__name__)
# CORS 全开：允许 iPhone 前端从任意来源访问（demo 场景，不考虑安全）
CORS(app)

# 启动时读取花名册 students.json，载入到内存
with open("students.json", "r", encoding="utf-8") as f:
    roster_list = json.load(f)

# 把花名册转成字典 {student_id: {name, seat_no}} 方便快速查找
roster = {s["student_id"]: {"name": s["name"], "seat_no": s["seat_no"]} for s in roster_list}

# 已签到学生的内存记录（重启服务就清空）
checked_in = {}


# 签到接口：前端刷 NFC 后调这个
@app.route("/checkin", methods=["POST"])
def checkin():
    # 从 URL 查询参数里取 student_id
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"ok": False, "error": "missing student_id"}), 400

    # 花名册里没这个学号 → 404
    if student_id not in roster:
        return jsonify({"ok": False, "error": "unknown student"}), 404

    # 记录签到：姓名、座位号、时间戳（Unix 秒）
    info = roster[student_id]
    ts = int(time.time())
    checked_in[student_id] = {
        "name": info["name"],
        "seat_no": info["seat_no"],
        "timestamp": ts,
    }
    return jsonify({
        "ok": True,
        "student_id": student_id,
        "name": info["name"],
        "seat_no": info["seat_no"],
        "timestamp": ts,
    })


# 查询所有已签到的人，按时间从早到晚排序
@app.route("/events", methods=["GET"])
def events():
    items = [
        {"student_id": sid, "name": v["name"], "seat_no": v["seat_no"], "timestamp": v["timestamp"]}
        for sid, v in checked_in.items()
    ]
    items.sort(key=lambda x: x["timestamp"])
    return jsonify({"checked_in": items})


# 重置签到记录（演示中途可以清空重来）
@app.route("/reset", methods=["POST"])
def reset():
    checked_in.clear()
    return jsonify({"ok": True})


# 返回完整花名册，前端用来渲染空座位格子
@app.route("/students", methods=["GET"])
def students():
    return jsonify({"students": roster_list})


if __name__ == "__main__":
    # 0.0.0.0 让同 WiFi 的 iPhone 能访问 Mac；端口 8000；debug 方便看报错
    app.run(host="0.0.0.0", port=8000, debug=True)
