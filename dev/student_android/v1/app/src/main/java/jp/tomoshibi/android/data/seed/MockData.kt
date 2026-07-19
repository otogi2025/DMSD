package jp.tomoshibi.android.data.seed

import jp.tomoshibi.android.data.model.*

// Mock seed 数据 — 对应 React tokens.jsx DATA + app-shell.jsx DEFAULT_STATE 默认值
// + iOS SEED.swift 的 060218 リュウイヒ 真值
// v1.0 demo 用，P6 接 backend 时换成真实 Repository

object MockData {
    val DEFAULT_USER =
        User(
            name = "リュウ イヒ",
            kana = "りゅう いひ",
            email = "demo@example.com",
            dorm = "男寮",
            room = "A5",
            avatar = "リ",
            studentNo = "060218",
            gradeClass = "高3 B組 18番",
            category = "一般寮生",
            phone = "090-0000-0000",
            birthDate = "2006-10-14",
            gender = "男",
            isStudyTarget = false,
        )

    val DEFAULT_APPLICATIONS =
        listOf(
            Application(
                id = "A-2401",
                kind = "外泊",
                dest = "実家（神戸）",
                from = "2025-04-12",
                to = "2025-04-14",
                status = ApplicationStatus.APPROVED,
                reason = "家族行事のため",
                createdAt = "2025-04-08",
            ),
            Application(
                id = "A-2402",
                kind = "外出",
                dest = "梅田 紀伊國屋書店",
                from = "2025-04-19",
                to = "2025-04-19",
                status = ApplicationStatus.PENDING,
                reason = "研究資料の購入",
                createdAt = "2025-04-18",
            ),
            Application(
                id = "A-2403",
                kind = "その他",
                dest = "共用エリア掃除",
                from = "2025-04-05",
                to = "2025-04-05",
                status = ApplicationStatus.RETURNED,
                reason = "掃除当番交代依頼",
                createdAt = "2025-04-04",
            ),
        )

    // 7 条 = 4.5 点（0.5×5 + 1.0×2）— iOS 截图 21.55.04 真值。
    // tier 处罚档：月累计 <8 = 0（无）/ ≥8 = 8（禁足）。（原 4=罚扫随清扫功能 6-10 删）
    // 本月累计最高 4.5，未达 8，所以 7 条 tier 全 = 0。
    val DEFAULT_DEDUCTIONS =
        listOf(
            Deduction("D-101", "2026-04-05", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-102", "2026-04-07", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-103", "2026-04-12", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-104", "2026-04-15", 1.0, "晩点呼・欠席", 0),
            Deduction("D-105", "2026-04-18", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-106", "2026-04-20", 1.0, "晩点呼・欠席", 0),
            Deduction("D-107", "2026-04-21", 0.5, "朝点呼・遅刻", 0),
        )

    val DEFAULT_NOTIFICATIONS =
        listOf(
            Notification("N1", "宅配", "Amazon 荷物到着", "寮管理員室で受取り", "今日 14:20", false),
            Notification("N2", "申請", "外泊申請が承認されました", "田中先生が承認しました", "昨日 16:30", false),
            Notification("N3", "減点", "遅刻警告", "今月の遅刻が 5 回に到達", "昨日 9:00", false),
            Notification("N4", "活動", "明日 18:00 新入生歓迎会", "食堂集合", "昨日", false),
            Notification("N5", "リクエスト曲", "あなたの投稿曲が採用されました", "Lemon / 米津玄師", "2 日前", true),
        )

    val DEFAULT_MUSIC =
        listOf(
            MusicRequest("M1", "春の歌", "中島みゆき", 12),
            MusicRequest("M2", "プラネタリウム", "大塚愛", 8),
            MusicRequest("M3", "Lemon", "米津玄師", 22),
        )

    // 失物 — Home omnibus 3 色块 grid（对应 iOS / React DATA.lostFound）
    val DEFAULT_LOST_FOUND =
        listOf(
            LostItem("L1", "青いおりたたみ傘", "FFA9C8E8", place = "玄関", date = "2026-04-25"),
            LostItem("L2", "黒の鍵", "FF9DA3A4", place = "廊下", date = "2026-04-23"),
            LostItem("L3", "赤のペンケース", "FFEC9FAA", place = "食堂", date = "2026-04-21"),
        )

    // 宅配 — 4 条（1 待領 + 3 領済），对齐 iOS SEED.packages
    val DEFAULT_PACKAGES =
        listOf(
            PackageItem(1, "本日", "Amazon", "待領", "JP1234567890"),
            PackageItem(2, "04-22", "佐川急便", "領済"),
            PackageItem(3, "04-18", "ヤマト運輸", "領済", "460-1234-5678"),
            PackageItem(4, "04-10", "郵便局", "領済"),
        )

    // 点呼履历 — 2026-04-05 ~ 04-21 每天朝/晩两条（对齐 iOS SEED.rollcall）
    // 遅刻日（朝）= 5/7/12/18/21；欠席日（晩）= 15/20；其余時間内
    val DEFAULT_ROLLCALL: List<RollcallEntry> =
        buildList {
            val lateMorning = setOf(5, 7, 12, 18, 21)
            val absentEvening = setOf(15, 20)
            for (d in 5..21) {
                val dd = "%02d".format(d)
                val date = "2026-04-$dd"
                val mStatus = if (d in lateMorning) "遅刻" else "時間内"
                add(RollcallEntry("RC-04$dd-AM", date, "朝点呼", mStatus, "NFC"))
                val eStatus = if (d in absentEvening) "欠席" else "時間内"
                add(RollcallEntry("RC-04$dd-PM", date, "晩点呼", eStatus, if (eStatus == "欠席") "―" else "NFC"))
            }
        }

    // 体调报告履历 — 2 条（对齐 iOS SEED.health）
    val DEFAULT_HEALTH =
        listOf(
            HealthRecord("H1", "2026-04-14", "頭痛", 37.2, "午後ずっと頭が重い"),
            HealthRecord("H2", "2026-04-03", "腹痛"),
        )

    // 特別運行便假数据 — 5 个日别（对应 iOS SEED.busSchedule，含通学便/特別便/空港便）
    val DEFAULT_BUS_ROUTES =
        listOf(
            SpecialBusRoute("B1", "2026-04-29", "水", "08:30", "寮 → 高校棟", "通学便"),
            SpecialBusRoute("B2", "2026-04-29", "水", "18:00", "高校棟 → 寮", "通学便"),
            SpecialBusRoute("B3", "2026-05-06", "水", "07:00", "寮 → 関西空港", "特別便", isAirport = true, seats = "残り 8 席"),
            SpecialBusRoute("B4", "2026-05-06", "水", "09:20", "高校棟 → 金川駅", "通学便"),
            SpecialBusRoute("B5", "2026-05-16", "土", "10:00", "寮 → 伊丹空港", "特別便", isAirport = true, seats = "残り 3 席"),
            SpecialBusRoute("B6", "2026-05-23", "土", "08:00", "寮 → 高校棟", "通学便"),
            SpecialBusRoute("B7", "2026-05-31", "日", "13:00", "寮 → 関西空港", "特別便", isAirport = true, seats = "満席"),
        )

    // 老师公告列表假数据（对应 iOS announcement list）
    val DEFAULT_ANNOUNCEMENTS =
        listOf(
            AnnouncementBrief(
                "AN1",
                "ゴールデンウィークの帰省について",
                "GW 期間中の帰省届は 4/25 までに提出してください。バスの増便もあります。",
                "田中先生",
                "2 時間前",
                isRead = false,
                replyCount = 2,
            ),
            AnnouncementBrief(
                "AN2",
                "防災訓練のお知らせ",
                "5 月 16 日（土）10:00 より避難訓練を実施します。全寮生参加必須です。",
                "佐藤先生",
                "昨日",
                isRead = true,
                replyCount = 0,
            ),
        )

    // 公告详情假数据（按 id 取，含回复链）
    val DEFAULT_ANNOUNCEMENT_DETAILS =
        listOf(
            AnnouncementDetail(
                "AN1",
                "ゴールデンウィークの帰省について",
                "GW 期間中（4/29〜5/6）の帰省を希望する寮生は、帰省届を 4/25（金）までに寮務室へ提出してください。\n\n空港送迎便の増便も予定しています。詳細は「特別運行便」のページをご確認ください。",
                "田中先生",
                "2026/04/20 14:30",
                listOf(
                    AnnouncementReply("リュウ イヒ", "student", "2026/04/20 15:10", "バスの時刻表はどこで確認できますか？"),
                    AnnouncementReply("田中先生", "teacher", "2026/04/20 16:00", "アプリの「特別運行便」から確認できます。"),
                ),
            ),
            AnnouncementDetail(
                "AN2",
                "防災訓練のお知らせ",
                "5 月 16 日（土）10:00 より避難訓練を実施します。全寮生の参加が必須です。\n\n当日は寮玄関前に集合してください。",
                "佐藤先生",
                "2026/05/15 09:00",
                emptyList(),
            ),
        )

    // 点歌假数据 — 8 条（对应 iOS SEED.songs）
    val DEFAULT_SONGS =
        listOf(
            SongItem(8, "ミックスナッツ", "Official髭男dism", "07号"),
            SongItem(7, "群青", "YOASOBI", "06号"),
            SongItem(6, "マリーゴールド", "あいみょん", "05号"),
            SongItem(5, "紅蓮華", "LiSA", "04号"),
            SongItem(4, "炎", "LiSA", "03号"),
            SongItem(3, "Pretender", "Official髭男dism", "02号"),
            SongItem(2, "夜に駆ける", "YOASOBI", "01号"),
            SongItem(1, "Lemon", "米津玄師", "00号"),
        )

    // 行事予定假数据 — 12 条（对应 iOS SEED.events，ISO 日期 + 场所 + 描述，给月历 + 活動詳細 用）
    val DEFAULT_EVENTS =
        listOf(
            EventItem("2026-04-05", "留 4 アクティビティ", "08:30", id = 1, place = "多目的ホール", desc = "新年度最初の寮生交流イベントです。"),
            EventItem("2026-04-07", "帰寮日", "15:33", id = 2, place = "寮玄関", desc = "春休み明けの帰寮日です。"),
            EventItem("2026-04-12", "茶道部体験", "14:00", id = 3, place = "和室", desc = "茶道部による体験会を開催します。"),
            EventItem("2026-04-19", "避難訓練", "10:00", id = 4, place = "寮玄関前集合", desc = "防災のための避難訓練を実施します。"),
            EventItem("2026-04-23", "新入生歓迎会", "18:00", id = 5, place = "食堂", desc = "新入生を歓迎する食事会です。"),
            EventItem("2026-04-29", "GW 特別便運行", "07:00", id = 6, place = "寮玄関", desc = "ゴールデンウィークの空港送迎便を運行します。"),
            EventItem("2026-05-06", "帰寮日", "17:00", id = 7, place = "寮玄関", desc = "ゴールデンウィーク明けの帰寮日です。"),
            EventItem("2026-05-10", "保護者面談", "13:00", id = 8, place = "応接室", desc = "保護者との面談を行います。"),
            EventItem("2026-05-16", "防災訓練", "10:00", id = 9, place = "寮玄関前集合", desc = "全寮生参加必須の防災訓練です。"),
            EventItem("2026-05-23", "球技大会", "13:00", id = 10, place = "体育館", desc = "寮対抗の球技大会を開催します。"),
            EventItem("2026-05-28", "進路ガイダンス", "16:00", id = 11, place = "多目的ホール", desc = "進学・進路についてのガイダンスです。"),
            EventItem("2026-05-31", "誕生日会", "19:00", id = 12, place = "カフェテリア", desc = "今月誕生日の寮生をお祝いします。"),
        )

    // 今週の活動 14 件 + 2 行 preview（iOS Home 「行事」section）
    const val EVENTS_THIS_WEEK = 14
    val EVENTS_PREVIEW =
        listOf(
            EventItem("04-05", "留 4 アクティビティ", "08:30"),
            EventItem("04-07", "帰寮日", "15:33"),
        )

    // 申请类型选项 — 对应 React tokens.jsx applyKinds
    data class ApplyKind(
        val kind: String,
        val iconName: String,
        val sub: String,
    )

    val APPLY_KINDS =
        listOf(
            ApplyKind("外出", "cal", "当日帰寮の外出"),
            ApplyKind("外泊", "home", "寮外での宿泊"),
            ApplyKind("帰省", "house", "実家帰省・長期休暇"),
            ApplyKind("帰国", "plane", "一時帰国（航空機利用）"),
            ApplyKind("早帰", "cal-clock", "門限前の早帰・遅帰"),
            ApplyKind("修繕", "wrench", "部屋・設備の修繕依頼"),
            ApplyKind("代理受取", "box", "不在時の荷物代理受取"),
            ApplyKind("来訪者", "people", "家族・友人の来訪"),
            ApplyKind("その他", "chat", "その他の申請"),
            ApplyKind("学習", "book", "自習室・学習関連"),
        )

    // Bus 数据 — 对应 React tokens.jsx DATA.bus
    data class BusInfo(
        val time: String,
        val date: String,
        val route: String,
    )

    val DEFAULT_BUS = BusInfo("09:20", "05/06(水)", "高校棟 → 金川駅")

    // Delivery
    data class DeliveryInfo(
        val count: Int,
        val source: String,
        val note: String,
    )

    val DEFAULT_DELIVERY = DeliveryInfo(1, "Amazon", "本日到着")

    // ───────── 申請履歴 family 假数据（对应 iOS StayListMock）─────────
    // 用户「リュウ イヒ」= 留学生 → 外泊承認链 5 役职：「担任」「国際交流部長」「寮務課長」「寮務部長」「管理係」
    private val OVERSEAS_STAY_ROLES =
        listOf("担任", "国際交流部長", "寮務課長", "寮務部長", "管理係")

    // 全员同决定的承認链（用于「全 pending」「全 approved」两种简单态）
    private fun chainAll(
        decision: StayDecision,
        decidedAt: String? = null,
    ): List<StayApprovalStep> =
        OVERSEAS_STAY_ROLES.map {
            StayApprovalStep(
                role = it,
                decision = decision.name,
                decidedAt = if (decision == StayDecision.PENDING) null else decidedAt,
            )
        }

    val DEFAULT_STAY_APPLICATIONS: List<StayApplication> =
        listOf(
            // 1) 外泊 審査中 — 链全 pending
            StayApplication(
                id = "s1",
                kind = StayKind.STAY.label,
                status = StayStatus.PENDING.name,
                leaveDate = "2026-05-03",
                returnDate = "2026-05-05",
                summary = "実家へ外泊",
                destination = "東京都世田谷区",
                leaveMethod = "JR",
                returnMethod = "JR",
                chain = chainAll(StayDecision.PENDING),
                submittedAt = "2026-05-01 10:24",
                auditLog =
                    listOf(
                        StayAuditEntry(at = "2026-05-01 10:24", action = "提出", actor = "リュウ イヒ"),
                    ),
            ),
            // 2) 帰省 承認済 — 链全 approved
            StayApplication(
                id = "s2",
                kind = StayKind.HOLIDAY.label,
                status = StayStatus.APPROVED.name,
                leaveDate = "2026-04-20",
                returnDate = "2026-04-23",
                summary = "GW 帰省",
                destination = "大阪府",
                leaveMethod = "新幹線",
                returnMethod = "新幹線",
                chain = chainAll(StayDecision.APPROVED, decidedAt = "2026-04-19 16:00"),
                submittedAt = "2026-04-18 09:10",
                auditLog =
                    listOf(
                        StayAuditEntry(at = "2026-04-19 16:00", action = "承認", actor = "管理係：田中"),
                        StayAuditEntry(at = "2026-04-18 09:10", action = "提出", actor = "リュウ イヒ"),
                    ),
            ),
            // 3) 外泊 要修正（差戻）— 担任承認、国際交流部長差戻、其余 pending
            StayApplication(
                id = "s3",
                kind = StayKind.STAY.label,
                status = StayStatus.RETURNED.name,
                leaveDate = "2026-05-10",
                returnDate = "2026-05-11",
                summary = "友人宅に外泊",
                destination = "神奈川県横浜市",
                leaveMethod = "バス",
                returnMethod = "バス",
                chain =
                    listOf(
                        StayApprovalStep("担任", "佐藤", StayDecision.APPROVED.name, "2026-05-08 11:02"),
                        StayApprovalStep("国際交流部長", "鈴木", StayDecision.REJECTED.name, "2026-05-08 14:30", comment = "外泊先の連絡先を明記してください"),
                        StayApprovalStep("寮務課長", decision = StayDecision.PENDING.name),
                        StayApprovalStep("寮務部長", decision = StayDecision.PENDING.name),
                        StayApprovalStep("管理係", decision = StayDecision.PENDING.name),
                    ),
                submittedAt = "2026-05-07 19:40",
                auditLog =
                    listOf(
                        StayAuditEntry(at = "2026-05-08 14:30", action = "差し戻し", actor = "国際交流部長：鈴木", detail = "外泊先の連絡先を明記してください"),
                        StayAuditEntry(at = "2026-05-08 11:02", action = "承認", actor = "担任：佐藤"),
                        StayAuditEntry(at = "2026-05-07 19:40", action = "提出", actor = "リュウ イヒ"),
                    ),
            ),
        )

    // 行事企画 一覧 假数据
    val DEFAULT_DORM_EVENTS: List<DormEventProposal> =
        listOf(
            DormEventProposal(
                id = "ev1",
                teamName = "3 階有志",
                title = "春の交流会",
                heldAt = "2026-05-18 18:00",
                place = "1 階ラウンジ",
                expectedCount = 30,
                target = "全寮生",
                purpose = "新入寮生との親睦",
                content = "軽食を囲んでの交流会",
                riskSolution = "食物アレルギー確認・21 時までに解散",
                expectedCost = "5,000 円",
                status = "pending",
            ),
        )

    // 在线学习申請 一覧 假数据
    val DEFAULT_STUDY_ONLINE: List<StudyOnlineRequest> =
        listOf(
            StudyOnlineRequest(
                id = "so1",
                reason = "オンライン英会話の受講",
                periodFrom = "2026-05-01",
                periodTo = "2026-07-31",
                contractFileName = "契約書.pdf",
                status = "approved",
            ),
        )

    // 冷蔵庫購入 申請 一覧 假数据
    val DEFAULT_FRIDGE: List<FridgePurchaseRequest> =
        listOf(
            FridgePurchaseRequest(
                id = "fr1",
                product = "A",
                contactPhone = "090-1234-5678",
                submittedAt = "2026-04-25 13:20",
                status = "ordered",
            ),
        )

    // 物品所持 申請 一覧 假数据
    val DEFAULT_ITEMS: List<ItemPossessionRequest> =
        listOf(
            ItemPossessionRequest(
                id = "it1",
                roomNo = "A5",
                item = "電気ケトル",
                reason = "お茶を淹れるため",
                guardianName = "リュウ ジェンミン",
                submittedAt = "2026-04-22 20:05",
                status = "pending",
            ),
        )

    // 夜学习出席打卡履历假数据（対象学生用，对齐 iOS studyHistory）
    // 3 天：05-10 齐全時間内 / 05-09 齐全但遅刻 / 05-08 只 1 次未完
    val DEFAULT_STUDY_HISTORY: List<StudyHistoryEntry> =
        listOf(
            StudyHistoryEntry("sh1", "2026-05-10", StudyTap.START.name, "19:38"),
            StudyHistoryEntry("sh2", "2026-05-10", StudyTap.END.name, "21:42"),
            StudyHistoryEntry("sh3", "2026-05-09", StudyTap.START.name, "19:52", note = "遅刻"),
            StudyHistoryEntry("sh4", "2026-05-09", StudyTap.END.name, "21:43"),
            StudyHistoryEntry("sh5", "2026-05-08", StudyTap.START.name, "19:39"),
        )

    // 当月夜学习欠席届 累计次数（>3 显示超過警告，对齐 iOS studyLeaveCountThisMonth）
    const val STUDY_LEAVE_COUNT = 2

    // 完整初始 AppState — fresh state（走完整 Onboarding → Account → Welcome → Login → Home）
    // Account 注册各 step 默认预填 demo seed，itsuki 一路点「次へ」走完，不用手动填
    val INITIAL_STATE =
        AppState(
            authed = false,
            onboarded = false,
            user = DEFAULT_USER,
            themeMode = ThemeMode.LIGHT,
            rollState = RollState.IDLE,
            applications = DEFAULT_APPLICATIONS,
            deductions = DEFAULT_DEDUCTIONS,
            notifications = DEFAULT_NOTIFICATIONS,
            musicRequests = DEFAULT_MUSIC,
        )
}
