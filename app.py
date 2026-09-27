import streamlit as st
#import json
#from search import search_pages, highlight_match
#from datetime import date
from crawler import crawl_url,crawl_recursive, crawl_recursive_gen
#from search_fulltext import search_fulltext
from database import init_db, insert_page, get_all_pages, log_search
from ranking import get_engine, rebuild_index
import re

init_db()

#@st.cache_data
# この関数を同じfilepathの引数で2回目以降呼び出すと、Streamlitはファイルを再読み込みせず、キャッシュ済みの結果を返してくれます。

# def load_pages():
#     with open("pages_w2.json", "r", encoding="utf-8") as f:
#         return json.load(f)

# def save_pages(pages):
#     with open("pages_w2.json", "w", encoding="utf-8") as f:
#         json.dump(pages, f, ensure_ascii=False, indent=2)

# def add_page(pages, page):
#     page["id"] = len(pages) +1
#     page.setdefault("author", "クローラー")
#     page.setdefault("category", "クロール")
#     page.setdefault("created_at", str(date.today()))
#     pages.append(page)
#     save_pages(pages)

st.set_page_config(page_title="Tech0 Search w3")
st.title("Tech0 Search w4")

@st.cache_resource
def load_and_index():
    pages = get_all_pages()
    if pages:
        rebuild_index(pages)
    return pages

pages = load_and_index()
engine = get_engine()

st.title("Tech0 Search v1.0")

with st.sidebar:
    st.header("DBの状態")
    st.metric("登録ページ数", f"{len(pages)}件")
    if st.button("インデックスを更新"):
        st.cache_resource.clear()
        st.rerun()

tab_search, tab_crawl, tab_list = st.tabs(
    ["検索","クロール","一覧"])
# pages = load_pages()

with tab_search:
    st.subheader("キーワードで検索")

    col_search, col_options = st.columns([3, 1])
    with col_search:
        query = st.text_input("キーワードを入力")
    with col_options:
        top_n = st.selectbox("表示件数", [10, 20, 50], index=0)
    if query:
        results = engine.search(query, top_n=top_n)
        log_search(query, len(results))
        
        st.markdown(f"***検索結果：{len(results)}件**")
        st.divider()

        if results:
            for i, page in enumerate(results,1):
                with st.container():
                    col_rank, col_title, col_score = st.columns([0.5, 4, 1])
                    with col_rank:
                        medal = ["金", "銀", "銅"][i - 1] if i <= 3 else str(i)
                        st.markdown(f"###{medal}")
                    with col_title:
                        st.markdown(f"###{page['title']}")
                    with col_score:
                        st.metric("スコア", f"{page['relevance_score']}",
                                  delta=f"基準：{page['base_score']}")

                    desc = page.get("description", "")
                    if desc:
                        st.markdown(f"*{desc[:200]}{'...'if len(desc) > 200 else ''}*")

                    kw = page.get("keywords", "") or ""
                    if kw:
                        kw_list = [k.strip() for k in kw.split(",")] if isinstance(kw, str) else list(kw)
                        tags = " ".join([f"'{k}" for k in kw_list[:5] if k])
                        st.markdown(f"タグ{tags}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.caption(f"{page.get('author', '不明')or '不明'}")
                    with col2: st.caption(f"{page.get('word_count', 0)}語")
                    with col3: st.caption(f"{page.get('category', '未分類') or '未分類'}")
                    with col4: st.caption(f"{(page.get('crawled_at', '') or '')[:10]}")

                    st.markdown(f"[{page['url']}]({page['url']})")
                    st.divider()
        else:
            st.info("該当ページ無し")

if "crawl_results" not in st.session_state:
            st.session_state.crawl_results = []

with tab_crawl:
    st.subheader("自動クローラー")

    if st.session_state.get("registered_count"):
        st.success(f"{st.session_state['registered_count']}件　登録完了")
        st.session_state["registered_count"] = 0
    st.caption("URLをクロールし、インデックスに登録")

    crawl_url_input = st.text_area(
        "クロール対象URL",
        placeholder="URLを改行またはスペース区切りで入力してください",
        height =150
    )

    if st.button("クロール実行", type="primary"):
        if crawl_url_input:
            raw_parts = re.split(r'[\s]+', crawl_url_input.strip())
            urls = [p for p in raw_parts if p.startswith(("http://", "https://"))]

            if not urls:
                st.error("有効なURLが見つかりませんでした")
            else:
                st.write(f"{len(urls)}件のURLを処理します")
                st.session_state.crawl_results = []

                for url in urls:
                    with st.spinner(f"クロール中: {url}"):
                        result = crawl_url(url)

                    if result and result.get('crawl_status') == 'success':
                        st.success(f"成功：{url}")
                        col1, col2 = st.columns(2)
                        with col1:
                            title = result.get('title', '')
                            st.metric("タイトル", (title[:30] + "...") if len(title) > 30 else title)
                        with col2:
                            st.metric("文字数", f"{result.get('word_count', 0)}語")
                        st.session_state.crawl_results.append(result)
                    else:
                        st.error(f"失敗：{url}")

    if st.session_state.crawl_results:
        st.info(f"{len(st.session_state.crawl_results)}件のクロール結果を登録できます")

        if st.button("すべてインデックスに登録"):
            total = len(st.session_state.crawl_results)
            progress_text = st.empty()
            progress_bar = st.progress(0)

            for i, r in enumerate(st.session_state.crawl_results, start=1):
                progress_text.write(f"{i} / {total}件登録中...")
                insert_page(r)
                progress_bar.progress(i / total)

            st.session_state["registered_count"] = total
            st.session_state.crawl_results = []
            st.cache_resource.clear()
            st.rerun()

with tab_list:
    st.subheader(f"登録済みページ一覧({len(pages)})件")
    if not pages:
        st.info("登録ページがありません。ページ追加して")
    else:
        for page in pages:
            with st.expander(f"{page['title']}"):
                st.markdown(f"**URL:**{page['url']}")
                st.markdown(f"**説明:**{page.get('description', '(なし)') or '（なし）'}")
                col1, col2, col3 = st.columns(3)
                with col1: st.caption(f"語数{page.get('word_count', 0)}")
                with col2: st.caption(f"作成者{page.get('author', '不明') or '不明'}")
                with col3: st.caption(f"カテゴリ{page.get('category', '未分類') or '未分類'}")

st.divider()
st.caption("@ PROJECT ZERO Tech0 Search v1 Powered by TF-IDF")





            # st.markdown(f"### [{r['title']}]({r['url']})")
            #     st.markdown(f"マッチ数：**{r['match_count']}**回")
            #     if r.get("preview"):
            #         st.caption(r["preview"])
            #     st.divider()

        # for page in results:
        #     st.markdown(f"###[{page['title']}]({page['url']})")
        #     st.markdown(highlight_match(page['description'],query))
        #     tags = " , ".join([f"`{kw}`" for kw in page["keywords"]])
        #     st.markdown(f"{tags}")
        #     col1, col2 = st.columns(2)
        #     col1.caption(f"{page['author']}")
        #     col2.caption(f"{page['created_at']}")
        #     st.caption(f"{page['url']}")
        #     st.divider()

# with tab2:
#     st.subheader("クロールDB登録")    
#     url_input = st.text_input("クロールしたいURL")
#     if st.button("クロール実行"):
#         if url_input:
#             with st.spinner(f"クロール中{url_input}"):
#                 result = crawl_url(url_input)
#             if result.get("crawl_status") == "success":
#                 insert_page(result)
#                 st.success(f"DB登録{result['title']}({result['word_count']}語)")
#             else:
#                 st.error(f"取得失敗{result.get('error')}")


#             #     st.success(f"取得成功：{result['title']}")
#             #     st.caption(f"{result['word_count']}語　リンク{len(result['links'])}件")
#             #     add_page(pages, result)
#             #     st.cache_data.clear()
#             #     st.info("登録完了")
#             # else:
#             #     st.error(f"習得失敗{result.get('error')}")

#     st.divider()

#     st.markdown("一括クロール、URLを改行区切りで入力")
#     urls_text = st.text_area("URLリスト", height=120)
#     if st.button("一括クロール実行"):
#         urls = [u.strip() for u in urls_text.splitlines() if u.strip().startswith("http")]
#         if not urls:
#             st.error("有効なURLが見つかりませんでした")
#         else:
#             ok = 0
#             for u in urls:
#                 with st.spinner(f"クロール中：{u}"):
#                     result = crawl_url(u)
#                 if result.get("crawl_status") == "success":
#                     insert_page(result)
#                     ok += 1
#                     st.success(f"{result['title']}")
#                 else:
#                     st.error(f"失敗{u}")
#             st.cache_data.clear()
#             st.info(f"{ok} / {len(urls)}件を登録しました")
#     st.divider()
#     st.markdown("連続クロール")
#     st.caption("自動巡回")

#     col1, col2 = st.columns([3,1])
#     with col1:
#         rec_url = st.text_input("起点となるURL", placeholder="https:・・・・")
#     with col2:
#         max_pages = st.number_input("上限ページ数", min_value=1, max_value=50, value=5)

    # if st.button("リンク巡回クロール開始"):
    #     if not rec_url or not rec_url.strip().startswith("http"):
    #         st.error("有効なURLを入力して")
    #     else:
    #         status_box = st.empty()
    #         progress_bar = st.progress(0.0)

    #         ok = 0

    #         for result, current_count in crawl_recursive_gen(rec_url.strip(),max_pages=max_pages):
    #             progress = current_count / max_pages
    #             progress_bar.progress(progress)

    #             if result.get("crawl_status") == "success":
    #                 add_page(pages, result)
    #                 ok += 1
    #                 st.write(f"〇({current_count}/{max_pages}){result.get('title','No Title')} - '{result.get('url')}'")
    #             else:
    #                 st.write(f"×({current_count} / {max_pages})失敗：'{result.get('url')}'")

    #         st.cache_data.clear()
    #         status_box.success(f"巡回完了：{ok} / {max_pages}県の登録に成功")



# with tab3:
#     st.subheader("ページを登録")
#     if st.session_state.get("registered"):
#         st.success("登録完了")
#         st.session_state["registered"] = False

#     with st.form('register_form'):
#         url = st.text_input("URL")
#         title = st.text_input("タイトル")
#         description = st.text_area("説明")
#         keywords = st.text_input("キーワードはカンマ区切りで")
#         author = st.text_input("作成者")
#         category = st.selectbox("カテゴリ",["事例", "企画", "業務マニュアル", "研修", "共有"])
#         submitted = st.form_submit_button('登録する')
#     if submitted:
#         if not url or not title:
#             st.error("URLとタイトルは必須")
#         else:
#             new_page = {
#                 "id":len(pages) +1,
#                 "title":title,
#                 "url":url,
#                 "description":description,
#                 "keywords":[k.strip() for k in keywords.split(",") if k.strip()],
#                 "author":author,
#                 "created_at":str(date.today()),
#                 "category":category,
#             }

#             pages.append(new_page)
#             save_pages(pages)
#             st.cache_data.clear()
#             st.session_state['registered'] = True
#             st.rerun()

# with tab3:
#     pages = get_all_pages()
#     st.subheader(f"登録ずみページ一覧({len(pages)}件)")
#     for page in pages:
#         with st.expander(f"{page['title']}"):
#             st.markdown(page.get('description',"") or "(説明なし)")
#             # tags = " , ".join([f"`{kw}`" for kw in page["keywords"]])
#             # st.markdown(f"{tags}")
#             st.caption(f"{page.get('author') or '不明'} {page.get('word_count',0)}語")
#             st.caption(f"{page['url']}")



