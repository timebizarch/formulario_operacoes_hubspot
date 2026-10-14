"""Gera products.json com os Produtos (unidades) do HubSpot usados no seletor do formulário.

Uso: HUBSPOT_TOKEN=pat-... python3 scripts/update_products.py
Precisa do escopo crm.objects.custom.read no Private App.
"""
import json, os, sys, urllib.request

OBJECT = "2-59303198"  # Produtos
STATUS_OK = {"Operando", "Operação pausada", "Novo"}
IGNORAR = {"lixeira erros admin"}

def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        sys.exit("Defina HUBSPOT_TOKEN")
    props = "nome_do_produto,id_do_produto,status_operacional"
    url = f"https://api.hubapi.com/crm/v3/objects/{OBJECT}?limit=100&properties={props}"
    rows = []
    while url:
        d = get(url, token)
        for it in d["results"]:
            p = it["properties"]
            nome = (p.get("nome_do_produto") or "").strip()
            if not nome or nome.lower() in IGNORAR or p.get("status_operacional") not in STATUS_OK:
                continue
            rows.append([it["id"], nome, p.get("id_do_produto") or ""])
        nxt = d.get("paging", {}).get("next", {}).get("after")
        url = f"https://api.hubapi.com/crm/v3/objects/{OBJECT}?limit=100&properties={props}&after={nxt}" if nxt else None
    rows.sort(key=lambda r: r[1].lower())
    out = os.path.join(os.path.dirname(__file__), "..", "products.json")
    with open(out, "w", encoding="utf-8") as f:
        # formato compacto: [id HubSpot, nome do produto, id do produto no Admin]
        json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(rows)} produtos gravados em products.json")

if __name__ == "__main__":
    main()
