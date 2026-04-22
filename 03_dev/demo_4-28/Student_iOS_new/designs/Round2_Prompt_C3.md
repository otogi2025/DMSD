# Round 2 補丁 Prompt · C3 申し込み Tab 重構

> **用途**: itsuki 把本文件**整段**贴给 Round 1 的同一个 Claude Design conversation（**不新开 project**），让它针对**申し込み tab 一个模块**做重构。
> **触发**: Phase B 产出后 QA 发现 `APPLY_TYPES` 不匹配 Round 1 Prompt §5.1 的 7 种规格。
> **产物**: 新 standalone HTML `Tomoshibi_iOS_PhaseB_v3.html`（**不影响其他 tab**）
> **额度节约策略**: 尽量在 1 次 reply 内解决。只修改申し込み tab，其他组件不动。

---

## 要贴给 Claude Design 的内容（从下面开始）

---

こんにちは Claude Design さん。Round 1 で出してもらった Phase B の standalone HTML を QA しました。**申し込み tab だけ**に 1 つ critical な不一致があり、その修正を Round 2 補丁としてお願いします。

**他の全 tab（Splash / Onboarding / Register / Login / Lockout / PwReset / Home / 子ページ群 / マイページ）はそのまま保持してください**。変更するのは `100ba570-8c9d-46fb-b4cc-9dcf0d30205a.js`（申し込み tab モジュール）+ 必要なら `c281cafa-0a67-4ff3-8653-8811600aa3e9.js` の `SEED.applies` 部分 のみ。

---

## 現状（Phase B 実装）

現在の `APPLY_TYPES` 配列 8 種：

```js
const APPLY_TYPES = [
  { k:'outing',  name:'外出',     desc:'当日帰寮の外出' },
  { k:'stay',    name:'外泊',     desc:'寮外での宿泊' },
  { k:'holiday', name:'帰省',     desc:'実家帰省・長期休暇' },
  { k:'return',  name:'早帰',     desc:'門限前の早帰・遅帰' },
  { k:'repair',  name:'修繕',     desc:'部屋・設備の修繕依頼' },
  { k:'parcel',  name:'代理受取', desc:'不在時の荷物代理受取' },
  { k:'guest',   name:'来訪者',   desc:'家族・友人の来訪' },
  { k:'other',   name:'その他',   desc:'上記以外のご依頼' },
];
```

この 8 種は Claude Design が自由発揮したもの。Round 1 Prompt §5.1 の仕様とは**ズレ**があります。

---

## 目標（Round 1 Prompt §5.1 に準拠した新 7 種）

```js
const APPLY_TYPES = [
  { k:'stay',        name:'外泊申請',       icon:Ic.home,      desc:'寮外での 1 日以上の宿泊' },
  { k:'returnhome',  name:'帰国申請',       icon:Ic.plane,     desc:'長期休暇・緊急の帰国' },
  { k:'holiday',     name:'帰省申請',       icon:Ic.train,     desc:'実家帰省（同国内）· 毎週水曜 18:00 締切' },
  { k:'taxi',        name:'タクシー予約',   icon:Ic.car,       desc:'タクシー利用の事前予約' },
  { k:'clean',       name:'掃除提出',       icon:Ic.camera,    desc:'掃除完了の写真提出 → 先生審査' },
  { k:'absence',     name:'欠席届（今回）', icon:Ic.note,      desc:'単発の点呼欠席申請' },
  { k:'exempt',      name:'免点呼期間 閲覧', icon:Ic.eye,       desc:'先生が設定した免点呼期間を確認（閲覧のみ）' },
];
```

**icon が未定義なら、近い既存 icon で代替 OK**（Ic.plane / Ic.train / Ic.car / Ic.note / Ic.eye などを適宜新規定義して `theme.jsx` に追加、または既存の近いもので代替）。

---

## 各 kind の form 仕様

### 1. stay (外泊申請) · 既存 `StayForm` を保持

Round 1 Prompt §2.2 の「§ 申請者本人」「§ 同行者」「§ 外泊日時」「§ 移動手段」「§ 宿泊先」「§ 食事」「§ 外泊の理由」「§ 備考」「§ 保護者許可」を含む既存フォームを**そのまま**（現在の実装 OK）。

### 2. returnhome (帰国申請) · 新規 form

フィールド:
- 出発予定日 (date)
- 帰着予定日 (date)
- 航空券番号 (text input, 例: `JL123 / CA456`)
- 行先国 (select: 中国 / 韓国 / その他 text)
- 家族連絡先 (name + phone 2 field)
- 滞在先住所 (textarea)
- 証明書アップロード (画像 picker, 複数 OK)
- 帰国理由 (textarea, 必須)

### 3. holiday (帰省申請) · 既存 `StayForm` を再利用、+ 毎週水曜 18:00 締切 の amber reminder banner

帰省は外泊の特殊ケース（実家帰省）なので `StayForm` の「行先都市 = 実家」「外泊理由 = 帰省」として再利用可。form 上部に追加:

```jsx
<div style={{ padding:'10px 14px', background:T.warnBg, borderRadius:10, fontSize:12, color:T.warnDeep, marginBottom:14 }}>
  ⏰ 帰省申請は毎週水曜日 18:00 が締切です
</div>
```

### 4. taxi (タクシー予約) · 新規 form

フィールド:
- 日時 (date + time picker)
- 乗車地 (text input, 例: `寮ロビー`)
- 目的地 (text input)
- 同乗者数 (number stepper, 1-4)
- 利用理由 (textarea)

### 5. clean (掃除提出) · 新規 form

フィールド:
- 日付 (date picker, default 今日)
- 掃除範囲 (select: `部屋 / 廊下 / 共用エリア / 浴場 / その他`)
- **写真アップロード** (画像 picker, 複数選択 OK, max 5 枚, サムネイル grid 表示)
- 備考 (textarea, optional)

### 6. absence (欠席届今回) · 既存 AbsenceSheet と共通

既に HomePage の顶部 feedback sheet で `AbsenceSheet` がある (「今回欠席の申請」)。申し込み tab からも同じ form に入れるようにする。**state 共有**: AbsenceSheet 既存のロジックを再利用。

### 7. exempt (免点呼期間 閲覧) · 読み取り専用 list

フィールドはなし。**一覧ページ**として実装:

```jsx
function ExemptListPage() {
  const exempts = [
    { from:'2026-04-20', to:'2026-04-27', reason:'インフルエンザ隔離', setBy:'田中先生' },
    { from:'2026-04-15', to:'2026-04-16', reason:'修学旅行事前打ち合わせ', setBy:'佐藤先生' },
  ];
  return (
    <Page hideBottomNav>
      <PageHeader title="免点呼期間" level={2}/>
      <div style={{ padding:'0 20px', fontSize:12, color:T.inkSub, marginBottom:14 }}>
        先生が設定した免点呼期間です。学生側では申請・変更できません。
      </div>
      {exempts.map((e,i)=>(
        <Card key={i} pad={14} style={{ margin:'0 20px 10px' }}>
          <div style={{ fontFamily:T.mono, fontSize:13, color:T.ink, fontWeight:700, marginBottom:6 }}>
            {e.from} 〜 {e.to}
          </div>
          <div style={{ fontSize:13, color:T.ink, marginBottom:3 }}>{e.reason}</div>
          <div style={{ fontSize:11, color:T.inkMute }}>設定者: {e.setBy}</div>
        </Card>
      ))}
    </Page>
  );
}
```

---

## SEED.applies 更新

`c281cafa` の `SEED.applies` を以下に更新（新 kind に合わせる）:

```js
applications: [
  { id:'a1', type:'stay',       status:'pending',  date:'2026-04-22', summary:'東京・友人宅 2 泊 3 日' },
  { id:'a2', type:'clean',      status:'approved', date:'2026-04-19', summary:'部屋掃除 · 評点 5' },
  { id:'a3', type:'returnhome', status:'pending',  date:'2026-04-25', summary:'中国・上海 · GW 帰国' },
  { id:'a4', type:'taxi',       status:'approved', date:'2026-04-18', summary:'駅前 → 寮 · 19:00' },
  { id:'a5', type:'holiday',    status:'pending',  date:'2026-04-24', summary:'茨城・実家 · 帰省' },
],
```

---

## 変更するファイル

1. `100ba570-*.js`（申し込み tab モジュール）— 以下を更新:
   - `APPLY_TYPES` 配列を 新 7 種に置換
   - `ApplyFormPage` dispatch に新 kind を追加:
     ```js
     function ApplyFormPage({ kind }) {
       if (kind === 'stay' || kind === 'holiday') return <StayForm kind={kind}/>;
       if (kind === 'returnhome') return <ReturnHomeForm/>;
       if (kind === 'taxi') return <TaxiForm/>;
       if (kind === 'clean') return <CleanForm/>;
       if (kind === 'absence') return <AbsenceSheet asPage/>;  // 既存 sheet を page mode で呼ぶ
       if (kind === 'exempt') return <ExemptListPage/>;
       return <Empty/>;
     }
     ```
   - `StayForm` 内部で `holiday` kind なら reminder banner を表示:
     ```js
     {kind === 'holiday' && (
       <div style={{ padding:'10px 14px', background:T.warnBg, ... }}>
         ⏰ 帰省申請は毎週水曜日 18:00 が締切です
       </div>
     )}
     ```
   - 旧 `GenericApplyForm` / 旧 repair/parcel/guest/return 用コードを削除

2. `c281cafa-*.js`（SEED）— `applications` 配列を上記 5 件に置換

3. （必要なら）`c13988a3-*.js` の `theme.jsx` 部分で Ic.plane / Ic.train / Ic.car / Ic.note / Ic.eye を新規追加:
   ```js
   plane: (s=22)=>(<svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M17.5 19 21 12l-3.5-7v3.5L13 11h-3L5.5 4H3v2.5L7 12l-4 5.5V20h2.5L10 13h3l4.5 4v2Z"/></svg>),
   train: (s=22)=>(<svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="3" width="14" height="15" rx="2"/><path d="M8 18l-2 3"/><path d="M16 18l2 3"/><circle cx="9" cy="13" r="1"/><circle cx="15" cy="13" r="1"/><path d="M5 9h14"/></svg>),
   car: (s=22)=>(<svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M5 17h14l-1.5-5.5A2 2 0 0 0 15.6 10H8.4a2 2 0 0 0-1.9 1.5L5 17Z"/><circle cx="8" cy="17" r="1.5"/><circle cx="16" cy="17" r="1.5"/></svg>),
   note: (s=22)=>(<svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="4" width="14" height="16" rx="2"/><path d="M9 9h6"/><path d="M9 13h6"/><path d="M9 17h4"/></svg>),
   eye:  (s=22)=>(<svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>),
   ```

---

## 不要な変更

- Home tab / マイページ tab / Auth flow / 顶部 bar / 中央 ⭐ 点呼 sheet / 通知系 — **全て現状維持**
- 申し込み tab の **画面レイアウト**（グリッド 2 列 × n 行、Card デザイン）— **現状維持**
- デザイン言語（Ryō tokens / Liquid Glass / アニメーション）— **現状維持**

---

## 交付

「Save as standalone HTML: Tomoshibi iOS Phase B v3.html」でエクスポートしてください。これを受け取ったら申し込み tab の各 kind form を QA して代码 agent に引き渡します。

以上、よろしくお願いします！

— リュウ イヒ（itsuki）

---

## （itsuki 向け · Claude Design に送る前に）

**この Round 2 補丁は必須ではない**。代替策:

| 方案 | 成本 | 代価 |
|---|---|---|
| **(i) Round 2 補丁を送る** | Claude Design 額度 +1 次対話 | 申し込み tab pixel-perfect 一致 |
| **(ii) 代码 agent にランタイム JS inject で差し替え** | 0 額度 | WebView 加载时 `APPLY_TYPES` 配列書き換え、form 内容は元のままで name/desc だけ変わる → **form 内容とラベルが不一致** ❌ |
| **(iii) C3 を受け入れる**（Claude Design の 8 種を採用） | 0 | demo 当日、管理員には「台本」で説明する |

**(iii) の AC 面試話術** もし採用する場合:
> 「Claude Design が 8 種の申請類型を生成したのを見て、これは私が書いた仕様の 7 種とは違うと気づきました。AI が『日本の寮では修繕・荷物受取・来訪者申請の方が一般的』と product thinking レベルで判断して自由発揮したんです。最初は prompt 通りに直そうとしましたが、よく考えたら AI の提案の方が実際の運用に近いかも。それで一度『AI の提案を真に受ける』という実験として採用してみました。— AI が人間の仕様を無条件に従うべきか、それとも AI の product judgement を受け入れる余地を残すべきか、これは AI 時代の協業における面白い問いだと思いました。」

**itsuki が (i) か (iii) を選んで CC にフィードバックしてください**。(ii) は非推奨（表裏不一致）。

---

**END**
