package jp.tomoshibi.android.data.network

// ApiErrorPresenter.kt
// data/network — 把 ApiError 转成日语用户提示的统一 helper
//
// 对齐 iOS Foundation/Network/APIErrorPresenter.swift。
// 用途：各屏 catch 分支需要给用户看日语提示时调用，避免每处手写 when、文案散乱。

object ApiErrorPresenter {
    // 把任意 Throwable 转成日语用户提示。
    //   - api: catch 拿到的异常（非 ApiError 也接受，走 fallback）
    //   - fallback: 非 ApiError 或 Unknown 时显示的文案（每个调用点按场景写）
    fun userMessage(
        error: Throwable,
        fallback: String,
    ): String {
        val api = error as? ApiError ?: return fallback
        return when (api) {
            is ApiError.Unauthorized -> {
                "ログインが必要です。再度ログインしてください。"
            }

            is ApiError.Network -> {
                "通信エラーが発生しました。電波を確認してください。"
            }

            is ApiError.Server -> {
                when (api.code) {
                    // 423 锁定 / 403 停用：后端日语文案是真值，原样显示（对齐 iOS AuthStubs）
                    423 -> {
                        api.msg.ifEmpty {
                            "アカウントロック中です。しばらくしてからお試しください"
                        }
                    }

                    403 -> {
                        api.msg.ifEmpty {
                            "このアカウントは現在ご利用いただけません。寮監に申し出てください"
                        }
                    }

                    else -> {
                        "サーバーエラー（コード ${api.code}）。時間をおいて再度お試しください。"
                    }
                }
            }

            is ApiError.Unprocessable -> {
                api.msg
            }

            // 后端 422 日语提示原样显示
            is ApiError.Decode -> {
                "データの読み込みに失敗しました。"
            }

            is ApiError.Unknown -> {
                fallback
            }
        }
    }
}
