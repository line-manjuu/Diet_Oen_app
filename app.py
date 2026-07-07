
import os
import datetime
import math


import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="ダイエット応援アプリ v3",  # ブラウザのタブに表示されるタイトル
    page_icon="🎈",  # タブのファビコン（絵文字やパスを指定可能）
    layout="wide",  # "centered"（デフォルト）か "wide"（横幅いっぱい）
    initial_sidebar_state="expanded",  # サイドバーの初期状態："auto", "expanded", "collapsed"
)

st.title("🎈 ダイエット応援アプリ v3")

st.write(
    "ダイエット応援アプリへようこそ！"
    "あなたがダイエットに成功するまで伴走します。"
    "今日も楽しんで、ダイエットしましょう！"
)

DB_FILE = "database.csv"





def _load_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str)

        for c in ["type", "key", "value"]:
            if c not in df.columns:
                df[c] = None

        return df[["type", "key", "value"]]
    return pd.DataFrame(columns=["type", "key", "value"])


def load_settings():
    df = _load_db()
    rows = df[df["type"] == "setting"]
    return {row["key"]: row["value"] for _, row in rows.iterrows()}


def save_setting(key, value):
    df = _load_db()

    keep = ~((df["type"] == "setting") & (df["key"] == str(key)))
    df = df[keep]

    new_row = pd.DataFrame(
        {"type": ["setting"], "key": [str(key)], "value": [str(value)]}
    )

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)


def load_log():
    df = _load_db()
    rows = df[df["type"] == "log"].copy()

    if rows.empty:
        return pd.DataFrame(columns=["date", "weight"])

    out = pd.DataFrame(
        {"date": rows["key"].astype(str), "weight": rows["value"].astype(float)}
    )

    return out.sort_values("date").reset_index(drop=True)


def save_record(date_str, weight):
    df = _load_db()

    keep = ~((df["type"] == "log") & (df["key"] == str(date_str)))
    df = df[keep]

    new_row = pd.DataFrame(
        {"type": ["log"], "key": [str(date_str)], "value": [str(weight)]}
    )

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)


def show_result(message, with_balloons=False, color="#d6336c"):
    balloons = ""
    if with_balloons:
        st.balloons()  # 組み込みの風船をひと吹き
        colors = ["#ff5a5f", "#ffb400", "#4ecdc4", "#5a9bff", "#b06bff", "#ff7ac1"]
        for i in range(18):  # ★風船の数（増やすと派手）
            c = colors[i % len(colors)]
            left = (i * 5 + 3) % 100
            delay = (i % 6) * 0.25
            duration = 4 + (i % 4)
            balloons += (
                f'<div class="balloon" style="left:{left}%;background:{c};'
                f'animation-delay:{delay}s;animation-duration:{duration}s;"></div>'
            )
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, encoding="utf-8") as f:
        css = " ".join(line.strip() for line in f if line.strip())
    html = (
        f"<style>{css}</style>"
        f'<div class="celebrate">{balloons}</div>'
        f'<div class="result-msg" style="color:{color}">{message}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def make_weekly_plan(start_weight, goal, start_date, deadline):
    plan = []
    total_days = (deadline - start_date).days

    weeks = max(1, math.ceil(total_days / 7))

    for k in range(1, weeks + 1):

        target = start_weight - (start_weight - goal) * k / weeks

        w_start = start_date + datetime.timedelta(days=(k - 1) * 7)  # その週の開始日
        w_end = start_date + datetime.timedelta(days=k * 7 - 1)  # その週の終了日
        if w_end > deadline:
            w_end = deadline  # 期限を越えたら期限で止める

        plan.append(
            {
                "週": k,
                "開始日": w_start.isoformat(),
                "終了日": w_end.isoformat(),
                "目安体重": round(target, 1),
            }
        )

    weeks = max(1, len(plan))  # ← 上の for を書いたら、weeks は len(plan) でOK
    return weeks, plan


def current_week_index(start_date, today, weeks):


    elapsed = (today - start_date).days
    idx = elapsed // 7 + 1
    return max(
        1, min(idx, weeks)
    )  # 1週目以降の経過週数を計算して今がダイエット開始から何週目にあたるのかを計算



if st.sidebar.button("データをリセット"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.rerun()


settings = load_settings()
default_start = float(settings["start_weight"]) if "start_weight" in settings else 60.0
default_goal = float(settings["goal"]) if "goal" in settings else 60.0
default_deadline = (
    datetime.date.fromisoformat(settings["deadline"])
    if "deadline" in settings
    else datetime.date.today() + datetime.timedelta(days=56)
)

st.header("①目標を設定しましょう")

col1, col2, col3 = st.columns(3)

with col1:
    start_weight_input = st.number_input(
        "開始体重（kg）", min_value=20.0, max_value=200.0, value=default_start, step=0.1
    )

with col2:
    goal_input = st.number_input(
        "目標体重（kg）", min_value=20.0, max_value=200.0, value=default_goal, step=0.1
    )

with col3:
    deadline_input = st.date_input("達成期限", value=default_deadline)



if st.button("目標プランを保存"):
    save_setting(
        "start_weight", start_weight_input
    )  # だーあさパートで作成された変数を受取
    save_setting("goal", goal_input)  # だーあさパートで作成された変数を受取
    save_setting(
        "deadline", deadline_input.isoformat()
    )  # だーあさパートで作成された変数を受取
    save_setting("start_date", datetime.date.today().isoformat())  #  ← プランを立てた日
    st.success("...")
    st.rerun()



st.header("② 今週の目安と週次プラン")
this_week_target = None
settings = load_settings()

needed = ["start_weight", "goal", "deadline", "start_date"]
if all(k in settings for k in needed):

    start_weight = float(settings["start_weight"])
    goal = float(settings["goal"])
    deadline = datetime.date.fromisoformat(settings["deadline"])
    start_date = datetime.date.fromisoformat(settings["start_date"])

    today = datetime.date.today()

    weeks, plan = make_weekly_plan(start_weight, goal, start_date, deadline)

    week_idx = current_week_index(start_date, today, weeks)

    this_week_target = plan[week_idx - 1]["目安体重"]

    deadline_passed = today > deadline


if this_week_target is not None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("今週の目安体重", f"{this_week_target} kg")

    with col2:
        st.metric("現在の週", f"{week_idx} 週目")

    with col3:
        st.metric("全体の期間", f"{weeks} 週間")

    st.subheader("週次プラン")
    st.dataframe(pd.DataFrame(plan), use_container_width=True, hide_index=True)

    if deadline_passed:
        deadline_log = load_log()
        latest_weight = (
            float(deadline_log["weight"].iloc[-1]) if not deadline_log.empty else None
        )

        if latest_weight is not None and latest_weight <= goal:
            st.success(
                f"🎉 達成期限（{deadline.isoformat()}）を迎え、目標体重 {goal}kg を達成しました！"
                "おめでとうございます。①で新しい目標と期限を設定して、次のステップに挑戦しましょう。"
            )
        else:
            st.warning(
                f"⏰ 達成期限（{deadline.isoformat()}）を過ぎました。ここまで続けてきたこと自体が成果です。"
                "①で開始体重・目標・新しい期限を設定し直して、引き続きチャレンジしましょう！"
            )

else:
    st.info("まず①で目標プランを保存してください。")



st.header("③ 体重を記録する")

selected_date = st.date_input("記録する日付", key="record_date")
date_str = selected_date.isoformat()

if "deadline" in settings and selected_date > datetime.date.fromisoformat(
    settings["deadline"]
):
    st.warning("①で目標を設定してください。")

today_weight_input = st.number_input(
    "その日の体重（kg）", min_value=20.0, max_value=200.0, value=66.0, step=0.1
)




@st.dialog("確認ダイアログ")
def confirm_overwrite_dialog(date_str, weight):
    st.write(f"{date_str}の記録を上書きしていいですか？")
    col_1, col_2, col_3, col_4 = st.columns(4)
    with col_2:
        if st.button("戻る", type="secondary"):
            st.rerun()
    with col_3:
        if st.button("上書きする", type="primary"):
            save_record(date_str, weight)  # ここで保存処理
            st.session_state.flash_message = (
                f"{date_str} の体重を記録しました！よくがんばりました👏"
            )
            st.session_state.show_result_for = date_str
            st.rerun()


log = load_log()

existing = log[log["date"] == date_str]

if st.button("この日の体重を記録"):
    if not existing.empty:
        confirm_overwrite_dialog(date_str, today_weight_input)
    else:
        save_record(date_str, today_weight_input)
        st.session_state.flash_message = (
            f"{date_str} の体重を記録しました！よくがんばりました👏"
        )
        st.session_state.show_result_for = date_str
        st.rerun()


if "flash_message" in st.session_state:
    st.success(st.session_state.flash_message)
    del st.session_state.flash_message


st.header("④ これまでの記録")

log = load_log()

if log.empty:
    st.info("まだ記録がありません。③から記録してみましょう。")
else:



    st.subheader("これまでの記録")

    display_log = log.copy()
    display_log["weight"] = display_log["weight"].map(lambda x: f"{x:.1f}kg")

    st.dataframe(display_log, use_container_width=True, hide_index=True)

    st.subheader("体重の推移")
    chart_df = log.copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"])
    chart_df = chart_df.set_index("date")
    chart_df = chart_df.rename(columns={"weight": "体重"})

    if "goal" in settings:
        chart_df["最終目標"] = float(settings["goal"])

    if this_week_target is not None:
        chart_df["今週の目安"] = [
            plan[current_week_index(start_date, d.date(), weeks) - 1]["目安体重"]
            for d in chart_df.index
        ]

    chart_long = chart_df.reset_index().melt("date", var_name="項目", value_name="値")
    y_min = chart_long["値"].min()
    y_max = chart_long["値"].max()
    padding = max((y_max - y_min) * 0.1, 0.5)

    weight_chart = (
        alt.Chart(chart_long)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "date:T",
                title="日付",
                axis=alt.Axis(format="%Y/%m/%d", tickCount="day"),
            ),
            y=alt.Y(
                "値:Q",
                title="体重（kg）",
                scale=alt.Scale(domain=[y_min - padding, y_max + padding]),
            ),
            color=alt.Color("項目:N", title=""),
        )
    )
    st.altair_chart(weight_chart, width="stretch")



show_for = st.session_state.get("show_result_for")
st.session_state.show_result_for = None

log = load_log()

if show_for is not None and this_week_target is not None:
    date_str = show_for
    today_rows = log[log["date"] == date_str]

    if not today_rows.empty:
        today_weight = float(today_rows["weight"].iloc[0])
        record_date = datetime.date.fromisoformat(date_str)
        skip_show_result = False

        show_next_goal_toast = False

        if record_date == deadline:
            if today_weight <= goal:
                message = f"🏆 達成期限を迎え、最終目標 {goal}kg を達成しました！お疲れ様でした！"
                color = "#2b8a3e"
                with_balloons = True
            else:
                message = f"⏰ 達成期限を迎えました。最終目標 {goal}kg には届きませんでしたが、ここまでの頑張りは本物です！"
                color = "#e8590c"
                with_balloons = False

            show_next_goal_toast = True

        elif record_date > deadline:
            skip_show_result = True

        else:
            record_week_idx = current_week_index(start_date, record_date, weeks)
            record_target = plan[record_week_idx - 1]["目安体重"]

            past = log[log["date"] < date_str]
            achieved_before = (
                (past["weight"] <= record_target).any() if not past.empty else False
            )
            prev_weight = float(past["weight"].iloc[-1]) if not past.empty else None

            if today_weight <= record_target and achieved_before == False:
                message = f"🎊 初クリア！今週の目安 {record_target}kg を達成しました！素晴らしいです！"
                color = "#e8590c"
                with_balloons = True

            elif today_weight <= record_target and achieved_before == True:
                message = f"🎉 今週の目安 {record_target}kg をクリア！この調子で続けましょう！"
                color = "#2b8a3e"
                with_balloons = True

            elif (
                today_weight > record_target
                and prev_weight is not None
                and today_weight < prev_weight
            ):
                message = f"💪 目安まではあと少し！でも前回より減っています。順調です！"
                color = "#1c7ed6"
                with_balloons = False

            else:
                message = f"⚠️ 今週の目安 {record_target}kg までもう少し。焦らず立て直しましょう！"
                color = "#e8590c"
                with_balloons = False

        if not skip_show_result:
            show_result(message, with_balloons=with_balloons, color=color)

        if show_next_goal_toast:
            st.toast(
                "**🎯 次の目標を①で設定して、引き続きチャレンジしましょう！**",
                icon="🎯",
                duration="infinite",
            )
