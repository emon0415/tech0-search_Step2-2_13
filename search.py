# search.py — W1 検索ロジック（虫食い版）
# ------------------------------------------------------------------
# ノートブック W1 Step 4 で学んだ2つの関数を、____ を埋めて完成させよう。
# 詰まったら search_answer.py（答え）と見比べること。
# 完成したら app.py から  from search import search_pages, highlight_match  で使える。
# ------------------------------------------------------------------
import re


def search_pages(query: str, pages: list) -> list:
    """キーワードでページを絞り込む（部分一致）"""

    # ① キーワードが空欄ならすぐ終了（空リストを返す）
    if not query.strip():
        return []          # TODO: 空のリストを返す

    results = []
    query_lower = query.lower()   # TODO: 大文字小文字を無視するため小文字に統一するメソッド

    for page in pages:           # ページを1件ずつ取り出してループ

        # title + description + keywords を1つの文字列に結合して検索対象にする
        search_text = " ".join([
            page["title"],
            page["description"],
            " ".join(page["keywords"]),
        ])

        # キーワードが search_text に含まれていたら results に追加
        if query_lower in search_text.lower():
            results.append(page)   # TODO: リストに要素を追加するメソッド

    return results


def highlight_match(text: str, query: str) -> str:
    """説明文の中のキーワードを **太字** にする"""

    if not query:                # キーワードが空なら何もしない
        return text

    pattern = re.compile(
        re.escape(query),        # 特殊文字が含まれても壊れない安全策
        re.IGNORECASE                  # TODO: 大文字・小文字を区別しないフラグ
    )

    # マッチした部分を **キーワード** に置換する（Markdownの太字）
    return pattern.sub(f"**{query}**", text)




