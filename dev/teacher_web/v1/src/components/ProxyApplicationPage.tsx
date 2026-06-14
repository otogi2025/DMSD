import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type {
  StudentBrief,
  StayLocation,
  MealSkip,
  ApplicationCreateBody,
} from "../api/types";

// 源 index.html 19128-20031（pages-records-search-etc 块）。界面原样搬，仅作用域引用改写。
// 代録（出寮届）页 — 老师代学生提交帰省 / 外泊 / 帰国届。
export function ProxyApplicationPage({ authToken }: { authToken: string }) {
  const T = RYO;

  // 交通手段选项（与 iOS ApplyStubs LEAVE/RETURN_TRANSPORTS 完全一致）
  const LEAVE_TRANSPORTS = [
    "西口1便",
    "西口2便",
    "金川1便",
    "金川2便",
    "寮生特別運行",
    "JR",
    "自家用車",
    "タクシー",
    "教員",
    "その他",
  ];
  const RETURN_TRANSPORTS = [
    "西口登校便",
    "金川登校便",
    "寮生特別運行",
    "JR",
    "自家用車",
    "タクシー",
    "教員",
    "その他",
  ];
  const MEALS = ["朝食", "昼食", "夕食"];
  const todayStr = new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);

  // ── 学生选择 ──
  const [q, setQ] = React.useState("");
  const [candidates, setCandidates] = React.useState<StudentBrief[]>([]);
  const [picked, setPicked] = React.useState<StudentBrief | null>(null);
  const [loadingC, setLoadingC] = React.useState(false);
  // 搜学生网络失败标志 — 区分「真没这学生」vs「网络出错」，别让老师误判
  const [candErr, setCandErr] = React.useState(false);

  // ── 申請种类 ──
  const [kind, setKind] = React.useState<"帰省" | "外泊" | "帰国">("帰省");

  // ── 共有字段 ──
  const [leaveDate, setLeaveDate] = React.useState(todayStr);
  const [leaveMethod, setLeaveMethod] = React.useState("JR");
  const [leaveTime, setLeaveTime] = React.useState("17:00");
  const [returnDate, setReturnDate] = React.useState(todayStr);
  const [returnMethod, setReturnMethod] = React.useState("JR");
  const [returnTime, setReturnTime] = React.useState("18:00");
  const [contactPhone, setContactPhone] = React.useState("");
  const [reason, setReason] = React.useState("");
  // 出租车预约希望时刻（仅出寮方法选「出租车」那项时用，独立于出寮时刻，同 iOS）
  const [taxiResvTime, setTaxiResvTime] = React.useState("17:00");

  // ── 帰省 ──
  const [isLongVacation, setIsLongVacation] = React.useState(false);

  // ── 外泊 / 帰国 ──
  const [companion, setCompanion] = React.useState("");
  const [destCities, setDestCities] = React.useState("");
  const [stayText, setStayText] = React.useState("");

  // ── 帰国 飞机 ──
  const [departAirport, setDepartAirport] = React.useState("");
  const [departFlightTime, setDepartFlightTime] = React.useState("10:00");
  const [arriveAirport, setArriveAirport] = React.useState("");
  const [arriveFlightTime, setArriveFlightTime] = React.useState("12:00");

  // ── 食事（留学生用）──
  const [mealNote, setMealNote] = React.useState("");
  const [skipEnabled, setSkipEnabled] = React.useState(false);
  const [skipStartDate, setSkipStartDate] = React.useState(todayStr);
  const [skipStartMeal, setSkipStartMeal] = React.useState("夕食");
  const [skipEndDate, setSkipEndDate] = React.useState(todayStr);
  const [skipEndMeal, setSkipEndMeal] = React.useState("朝食");

  const [submitting, setSubmitting] = React.useState(false);
  // 提交结果提示 {type:'ok'|'err', text}
  const [msg, setMsg] = React.useState<{
    type: "ok" | "err";
    text: string;
  } | null>(null);

  const isOverseas = !!(picked && picked.is_overseas);

  // 搜学生（输入 250ms 后再查，避免每个字都打后端）
  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    setLoadingC(true);
    const timer = setTimeout(() => {
      api
        .proxyCandidates(authToken, q)
        .then((rows) => {
          if (!cancelled) {
            setCandidates(rows || []);
            setCandErr(false);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setCandidates([]);
            setCandErr(true);
          }
        })
        .finally(() => {
          if (!cancelled) setLoadingC(false);
        });
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [q, authToken]);

  // 食事不要期间展开成 [{date, meal}]（照抄 iOS StayForm.expandMealsSkip）
  function expandMealsSkip(
    startDate: string,
    startMeal: string,
    endDate: string,
    endMeal: string,
  ): MealSkip[] {
    const order = ["朝食", "昼食", "夕食"];
    const result: MealSkip[] = [];
    const fmt = (d: Date) =>
      new Date(d.getTime() - d.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 10);
    let cur = new Date(startDate + "T00:00:00");
    const end = new Date(endDate + "T00:00:00");
    while (cur <= end) {
      const isFirst = fmt(cur) === startDate;
      const isLast = fmt(cur) === endDate;
      const lo = isFirst ? order.indexOf(startMeal) : 0;
      const hi = isLast ? order.indexOf(endMeal) : 2;
      if (lo <= hi) {
        for (let i = lo; i <= hi; i++)
          result.push({ date: fmt(cur), meal: order[i] as MealSkip["meal"] });
      }
      cur.setDate(cur.getDate() + 1);
    }
    return result;
  }

  async function submit() {
    if (!picked) {
      setMsg({ type: "err", text: "学生を選択してください" });
      return;
    }
    // 时刻补秒：网页 time 输入是 "HH:mm"，后端要 "HH:mm:ss"
    const hms = (t: string) => (t && t.length === 5 ? t + ":00" : t);
    // 帰寮必须晚于出寮 —— 合成 日期+时刻 完整比较（同日 17:00 出 / 08:00 帰 这种
    // 倒挂也拦；ISO 定宽字符串可直接按字典序比）
    if (
      returnDate + "T" + hms(returnTime) <=
      leaveDate + "T" + hms(leaveTime)
    ) {
      setMsg({
        type: "err",
        text: "帰寮日時は出寮日時より後にしてください",
      });
      return;
    }
    const needStay = kind === "外泊" || kind === "帰国";
    const stayRaw = stayText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    if (needStay && stayRaw.length === 0) {
      setMsg({ type: "err", text: "宿泊先を1件以上入力してください" });
      return;
    }
    // 宿泊先单行上限 200（后端 StayLocation.name max_length=200，前端先拦给提示）
    if (stayRaw.some((s) => s.length > 200)) {
      setMsg({
        type: "err",
        text: "宿泊先は1行200文字以内で入力してください",
      });
      return;
    }
    const stayLocations: StayLocation[] = stayRaw.map((s) => ({
      kind: "その他",
      name: s,
      address: s,
      phone: null,
    }));
    // 出租车预约时刻：出寮方法选「出租车」才填，是独立时刻（可不同于出寮时刻），同 iOS
    const taxiTimeValue = leaveMethod === "タクシー" ? hms(taxiResvTime) : null;

    let mealsSkip: MealSkip[] = [];
    if (isOverseas && skipEnabled) {
      mealsSkip = expandMealsSkip(
        skipStartDate,
        skipStartMeal,
        skipEndDate,
        skipEndMeal,
      );
      if (mealsSkip.length === 0) {
        setMsg({
          type: "err",
          text: "食事不要期間が空です（開始・終了の食事の順序を確認）",
        });
        return;
      }
    }

    // reason 三种届共通（后端 ApplicationBase 已定义）→ 放 base 不在各分支重复
    const base = {
      kind,
      leave_date: leaveDate,
      leave_method: leaveMethod,
      leave_time: hms(leaveTime),
      return_date: returnDate,
      return_method: returnMethod,
      return_time: hms(returnTime),
      contact_phone: contactPhone.trim() || null,
      meal_note: isOverseas ? mealNote.trim() || null : null,
      taxi_reservation_time: taxiTimeValue,
      reason: reason.trim() || null,
    };
    let body: ApplicationCreateBody;
    if (kind === "帰省") {
      // is_long_vacation 是后端 KiseiCreateIn(schemas.py:127) 的字段，但 types.ts 的
      // ApplicationCreateBody 暂未列入 → 断言带上，运行时负载与源一致（待 types.ts 补字段）
      body = {
        ...base,
        is_long_vacation: isLongVacation,
      } as ApplicationCreateBody;
    } else if (kind === "外泊") {
      body = {
        ...base,
        companion: companion.trim() || null,
        dest_cities: destCities.trim() || null,
        stay_locations: stayLocations,
        meals_skip: mealsSkip,
      };
    } else {
      // 帰国：飞机时刻跟日期合成带东京时区的完整时间（与 iOS formatISOWithTokyo 一致）
      if (!departAirport.trim() || !arriveAirport.trim()) {
        setMsg({ type: "err", text: "出発・到着空港を入力してください" });
        return;
      }
      const depAt = leaveDate + "T" + hms(departFlightTime) + "+09:00";
      const arrAt = returnDate + "T" + hms(arriveFlightTime) + "+09:00";
      // 到着必须晚于出发（后端 KikokuCreateIn 也校验，前端先拦给友好提示）
      if (arrAt <= depAt) {
        setMsg({
          type: "err",
          text: "到着時刻は出発時刻より後にしてください",
        });
        return;
      }
      body = {
        ...base,
        companion: companion.trim() || null,
        dest_cities: destCities.trim() || null,
        stay_locations: stayLocations,
        meals_skip: mealsSkip,
        flight_dep_air: departAirport.trim(),
        flight_dep_at: depAt,
        flight_arr_air: arriveAirport.trim(),
        flight_arr_at: arrAt,
      };
    }

    setSubmitting(true);
    setMsg(null);
    try {
      await api.createByTeacher(picked.id, body, authToken);
      setMsg({
        type: "ok",
        text: picked.name + " さんの" + kind + "届を代録しました（承認待ち）",
      });
      // 重置申請内容（保留已选学生，方便连续代録）— 含飞机 / 食事日期 / 出租车时刻
      setReason("");
      setCompanion("");
      setDestCities("");
      setStayText("");
      setSkipEnabled(false);
      setMealNote("");
      setSkipStartDate(todayStr);
      setSkipEndDate(todayStr);
      setDepartFlightTime("10:00");
      setArriveFlightTime("12:00");
      setTaxiResvTime("17:00");
    } catch (e) {
      // client.js 的 request 把后端 {detail:{code,message}} 铺平到错误对象
      // 顶层 → e.code / e.message / e.status（不是 e.body.detail.code）
      const err = e as { code?: string; message?: string; status?: number };
      const code = err && err.code;
      const text =
        code === "FORBIDDEN_DORM"
          ? "担当外の寮の学生です"
          : code === "FORBIDDEN_ROLE"
            ? "代録権限がありません"
            : code === "LEAVE_DATE_PAST"
              ? "出寮日は本日以降を指定してください"
              : (err && err.message) ||
                "提出に失敗しました (" +
                  ((err && err.status) || "network") +
                  ")";
      setMsg({ type: "err", text });
    } finally {
      setSubmitting(false);
    }
  }

  // ── 通用样式 ──
  const labelStyle: React.CSSProperties = {
    fontSize: 11,
    color: T.ink2,
    fontWeight: 600,
    display: "block",
    marginBottom: 4,
  };
  const inputStyle: React.CSSProperties = {
    padding: "7px 10px",
    border: "1px solid " + T.lineStrong,
    borderRadius: 8,
    fontFamily: "inherit",
    fontSize: 13,
    width: "100%",
    boxSizing: "border-box",
  };
  const dateInputStyle: React.CSSProperties = {
    ...inputStyle,
    fontFamily: T.mono,
  };
  const cardStyle: React.CSSProperties = {
    background: T.surface,
    border: "1px solid " + T.line,
    borderRadius: 12,
    padding: 18,
    marginBottom: 16,
    boxShadow: T.shadow1,
  };
  const sectionTitle: React.CSSProperties = {
    fontSize: 13,
    fontWeight: 700,
    color: T.ink,
    marginBottom: 12,
    borderLeft: "3px solid " + T.cobalt,
    paddingLeft: 8,
  };

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      <h1
        style={{
          fontSize: 20,
          fontWeight: 700,
          color: T.ink,
          marginBottom: 4,
          letterSpacing: -0.3,
        }}
      >
        代録（出寮届）
      </h1>
      <p style={{ fontSize: 12, color: T.ink3, marginBottom: 18 }}>
        学生に代わって帰省・外泊・帰国届を提出します（当日も可）。提出後は通常の承認フローに乗ります。
      </p>

      {/* ① 学生选择 */}
      <div style={cardStyle}>
        <div style={sectionTitle}>① 対象の学生</div>
        {picked ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "10px 12px",
              background: T.cobaltSoft,
              border: "1px solid " + T.infoBorder,
              borderRadius: 8,
            }}
          >
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: T.ink }}>
                {picked.name}
                <span
                  style={{
                    marginLeft: 8,
                    fontSize: 11,
                    fontWeight: 600,
                    color: isOverseas ? T.warn : T.ink3,
                  }}
                >
                  {isOverseas ? "留学生" : "日本人寮生"}
                </span>
              </div>
              <div
                style={{
                  fontSize: 12,
                  color: T.ink3,
                  fontFamily: T.mono,
                }}
              >
                {picked.student_no} · {picked.dorm_unit}寮 · {picked.room_no}
              </div>
            </div>
            <button
              onClick={() => setPicked(null)}
              style={{
                padding: "5px 12px",
                background: "transparent",
                color: T.ink2,
                border: "1px solid " + T.lineStrong,
                borderRadius: 8,
                fontSize: 12,
                cursor: "pointer",
              }}
            >
              選び直す
            </button>
          </div>
        ) : (
          <div>
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="氏名 または 学籍番号で検索"
              style={inputStyle}
            />
            <div
              style={{
                marginTop: 8,
                maxHeight: 240,
                overflowY: "auto",
                border: "1px solid " + T.line,
                borderRadius: 8,
              }}
            >
              {loadingC ? (
                <div style={{ padding: 12, fontSize: 12, color: T.muted }}>
                  読み込み中…
                </div>
              ) : candErr ? (
                <div style={{ padding: 12, fontSize: 12, color: T.danger }}>
                  検索に失敗しました（ネットワークを確認してください）
                </div>
              ) : candidates.length === 0 ? (
                <div style={{ padding: 12, fontSize: 12, color: T.muted }}>
                  該当する学生がいません
                </div>
              ) : (
                candidates.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => {
                      // 选新学生时重置日期回今天，避免上一个学生的日期残留误提
                      setPicked(c);
                      setMsg(null);
                      setLeaveDate(todayStr);
                      setReturnDate(todayStr);
                    }}
                    style={{
                      padding: "9px 12px",
                      borderBottom: "1px solid " + T.line,
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span style={{ fontWeight: 600, color: T.ink }}>
                      {c.name}
                    </span>
                    <span
                      style={{
                        fontSize: 12,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {c.student_no} · {c.dorm_unit}寮
                    </span>
                  </div>
                ))
              )}
            </div>
            {candidates.length >= 100 ? (
              <div style={{ marginTop: 6, fontSize: 11, color: T.muted }}>
                ※ 最大100件まで表示。氏名・学籍番号で絞り込んでください
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* ② 申請种类 */}
      <div style={cardStyle}>
        <div style={sectionTitle}>② 届の種類</div>
        <div style={{ display: "flex", gap: 8 }}>
          {(["帰省", "外泊", "帰国"] as const).map((k) => (
            <button
              key={k}
              onClick={() => setKind(k)}
              style={{
                flex: 1,
                padding: "9px 0",
                background: kind === k ? T.cobalt : "transparent",
                color: kind === k ? "#fff" : T.ink2,
                border: "1px solid " + (kind === k ? T.cobalt : T.lineStrong),
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {k}届
            </button>
          ))}
        </div>
      </div>

      {/* ③ 日時・方法 */}
      <div style={cardStyle}>
        <div style={sectionTitle}>③ 日時・移動方法</div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: 12,
            marginBottom: 14,
          }}
        >
          <div>
            <label style={labelStyle}>出寮日</label>
            <input
              type="date"
              value={leaveDate}
              onChange={(e) => setLeaveDate(e.target.value)}
              style={dateInputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>出寮方法</label>
            <select
              value={leaveMethod}
              onChange={(e) => setLeaveMethod(e.target.value)}
              style={inputStyle}
            >
              {LEAVE_TRANSPORTS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={labelStyle}>出寮時刻</label>
            <input
              type="time"
              value={leaveTime}
              onChange={(e) => setLeaveTime(e.target.value)}
              style={dateInputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>帰寮日</label>
            <input
              type="date"
              value={returnDate}
              onChange={(e) => setReturnDate(e.target.value)}
              style={dateInputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>帰寮方法</label>
            <select
              value={returnMethod}
              onChange={(e) => setReturnMethod(e.target.value)}
              style={inputStyle}
            >
              {RETURN_TRANSPORTS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={labelStyle}>帰寮時刻</label>
            <input
              type="time"
              value={returnTime}
              onChange={(e) => setReturnTime(e.target.value)}
              style={dateInputStyle}
            />
          </div>
        </div>
        {leaveMethod === "タクシー" ? (
          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>
              タクシー希望時刻（出寮方法＝タクシー）
            </label>
            <input
              type="time"
              value={taxiResvTime}
              onChange={(e) => setTaxiResvTime(e.target.value)}
              style={{ ...dateInputStyle, maxWidth: 160 }}
            />
          </div>
        ) : null}
        <div>
          <label style={labelStyle}>本人連絡先（任意）</label>
          <input
            type="text"
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
            placeholder="携帯・WeChat 等"
            style={inputStyle}
          />
        </div>
      </div>

      {/* ④ 种类别字段 */}
      <div style={cardStyle}>
        <div style={sectionTitle}>④ {kind}の詳細</div>
        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>
            {kind === "帰省" ? "帰省理由" : "理由（任意）"}
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={kind === "帰省" ? "例：家庭の用事" : ""}
            style={inputStyle}
          />
        </div>

        {kind === "帰省" ? (
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 13,
              color: T.ink2,
              cursor: "pointer",
            }}
          >
            <input
              type="checkbox"
              checked={isLongVacation}
              onChange={(e) => setIsLongVacation(e.target.checked)}
            />
            長期休暇用（長期休暇中の帰省）
          </label>
        ) : null}

        {kind === "外泊" || kind === "帰国" ? (
          <div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 12,
                marginBottom: 14,
              }}
            >
              <div>
                <label style={labelStyle}>同行者（任意）</label>
                <input
                  type="text"
                  value={companion}
                  onChange={(e) => setCompanion(e.target.value)}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>行先（都市名・任意）</label>
                <input
                  type="text"
                  value={destCities}
                  onChange={(e) => setDestCities(e.target.value)}
                  style={inputStyle}
                />
              </div>
            </div>
            <div>
              <label style={labelStyle}>宿泊先（1行に1件・必須）</label>
              <textarea
                value={stayText}
                onChange={(e) => setStayText(e.target.value)}
                rows={3}
                placeholder={"例：◯◯ホテル 086-xxx-xxxx\n親戚宅 岡山市…"}
                style={{ ...inputStyle, resize: "vertical" }}
              />
            </div>
          </div>
        ) : null}

        {kind === "帰国" ? (
          <div
            style={{
              marginTop: 14,
              paddingTop: 14,
              borderTop: "1px dashed " + T.line,
            }}
          >
            <div
              style={{
                fontSize: 12,
                fontWeight: 700,
                color: T.ink2,
                marginBottom: 10,
              }}
            >
              帰国便情報
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "2fr 1fr",
                gap: 12,
                marginBottom: 12,
              }}
            >
              <div>
                <label style={labelStyle}>出発空港（必須）</label>
                <input
                  type="text"
                  value={departAirport}
                  onChange={(e) => setDepartAirport(e.target.value)}
                  placeholder="例：岡山空港"
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>出発時刻</label>
                <input
                  type="time"
                  value={departFlightTime}
                  onChange={(e) => setDepartFlightTime(e.target.value)}
                  style={dateInputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>到着空港（必須）</label>
                <input
                  type="text"
                  value={arriveAirport}
                  onChange={(e) => setArriveAirport(e.target.value)}
                  placeholder="例：上海浦東"
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>到着時刻</label>
                <input
                  type="time"
                  value={arriveFlightTime}
                  onChange={(e) => setArriveFlightTime(e.target.value)}
                  style={dateInputStyle}
                />
              </div>
            </div>
            <div style={{ fontSize: 11, color: T.muted }}>
              ※ 出発は出寮日、到着は帰寮日と組み合わせて記録します
            </div>
          </div>
        ) : null}
      </div>

      {/* ⑤ 食事 */}
      <div style={cardStyle}>
        <div style={sectionTitle}>⑤ 寮食堂の食事</div>
        {isOverseas ? (
          <div>
            <div style={{ marginBottom: 14 }}>
              <label style={labelStyle}>食事メモ（任意）</label>
              <input
                type="text"
                value={mealNote}
                onChange={(e) => setMealNote(e.target.value)}
                placeholder="例：8月10日朝食まで必要、8月20日夕食から必要"
                style={inputStyle}
              />
            </div>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                fontSize: 13,
                color: T.ink2,
                cursor: "pointer",
                marginBottom: skipEnabled ? 14 : 0,
              }}
            >
              <input
                type="checkbox"
                checked={skipEnabled}
                onChange={(e) => setSkipEnabled(e.target.checked)}
              />
              食事不要期間を申請する
            </label>
            {skipEnabled ? (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 12,
                }}
              >
                <div>
                  <label style={labelStyle}>不要 開始日</label>
                  <input
                    type="date"
                    value={skipStartDate}
                    onChange={(e) => setSkipStartDate(e.target.value)}
                    style={dateInputStyle}
                  />
                </div>
                <div>
                  <label style={labelStyle}>開始の食事</label>
                  <select
                    value={skipStartMeal}
                    onChange={(e) => setSkipStartMeal(e.target.value)}
                    style={inputStyle}
                  >
                    {MEALS.map((m) => (
                      <option key={m} value={m}>
                        {m}から不要
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>不要 終了日</label>
                  <input
                    type="date"
                    value={skipEndDate}
                    onChange={(e) => setSkipEndDate(e.target.value)}
                    style={dateInputStyle}
                  />
                </div>
                <div>
                  <label style={labelStyle}>終了の食事</label>
                  <select
                    value={skipEndMeal}
                    onChange={(e) => setSkipEndMeal(e.target.value)}
                    style={inputStyle}
                  >
                    {MEALS.map((m) => (
                      <option key={m} value={m}>
                        {m}まで不要
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ) : null}
          </div>
        ) : (
          <div style={{ fontSize: 12, color: T.ink3, lineHeight: 1.6 }}>
            ※
            日本人寮生は「食事入力表（スプレッドシート）」にご自身で×を入れてください。
            システムでは食数を収集しません。
          </div>
        )}
      </div>

      {/* 提交 */}
      {msg ? (
        <div
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            marginBottom: 12,
            fontSize: 13,
            fontWeight: 600,
            background: msg.type === "ok" ? T.okSoft : T.dangerSoft,
            color: msg.type === "ok" ? T.ok : T.danger,
            border:
              "1px solid " + (msg.type === "ok" ? T.okBorder : T.dangerBorder),
          }}
        >
          {msg.text}
        </div>
      ) : null}
      <button
        onClick={submit}
        disabled={submitting || !picked}
        style={{
          width: "100%",
          padding: "12px 0",
          background: submitting || !picked ? T.graySoft : T.cobalt,
          color: submitting || !picked ? T.muted : "#fff",
          border: "none",
          borderRadius: 10,
          fontFamily: "inherit",
          fontSize: 15,
          fontWeight: 700,
          cursor: submitting || !picked ? "default" : "pointer",
          marginBottom: 40,
        }}
      >
        {submitting ? "提出中…" : kind + "届を代録する"}
      </button>
    </div>
  );
}
