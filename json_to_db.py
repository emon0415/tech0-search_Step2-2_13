# import json

# def migrate_from_json(json_path: str ="pages_w2.json") -> int:
#     with open(json_path, "r",encoding="utf-8") as f:
#         pages = json.load(f)

#     for p in pages:
#         insert_page(p)

#     return len(pages)

# n= migrate_from_json("pages_w2.json")
# print(f"{n}件をDBに移行しました")

# pages = get_all_pages()
# print(f"現在のDB登録件数：{len(pages)}件")
# print()
# for p in pages[:5]:
#     honbun ="本文アリ" if p.get("full_text") else "本文なし"
#     print(f" id={p['id']:>2}[(honbun)] {p['title'][:30]}")

