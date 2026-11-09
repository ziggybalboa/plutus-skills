"""Read-only live checks. Mutable data is discovered, not hardcoded."""
import importlib.util
import pathlib
import uuid

path = pathlib.Path(__file__).resolve().parents[1] / "skills/funder-research/scripts/funders.py"
spec = importlib.util.spec_from_file_location("funders", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
passed = []

def check(name, condition):
    assert condition, name
    passed.append(name)
    print("PASS", name)

tools = m.call("list", {})["tools"]
check("two read-only tools", {x["name"] for x in tools} == {"search_funders", "get_funder"} and all(x["annotations"]["readOnlyHint"] for x in tools))
schemas = {x["name"]: x["inputSchema"] for x in tools}
check("schema bounds", schemas["search_funders"]["properties"]["limit"]["maximum"] == 50 and schemas["get_funder"]["required"] == ["id"])
a = m.call("search_funders", {"limit": 2, "offset": 0})
check("discovery returns bounded page", 0 < len(a["funders"]) <= 2)
check("continuation available", isinstance(a["next_offset"], int))
b = m.call("search_funders", {"limit": 2, "offset": a["next_offset"]})
ids = [f["id"] for f in a["funders"] + b["funders"]]
check("consecutive pagination without duplicates", b["offset"] == a["next_offset"] and len(ids) == len(set(ids)))
f = a["funders"][0]
name_result = m.call("search_funders", {"q": f["name"], "limit": 50})
check("named company lookup", f["id"] in [x["id"] for x in name_result["funders"]])
detail = m.call("get_funder", {"id": f["id"]})["funder"]
check("detail ID consistent", detail["id"] == f["id"])
check("citation and provenance present", detail["url"].startswith("https://plutusai.net/funders/") and isinstance(detail["sources"], list) and "quality" in detail and "freshness" in detail)
product = m.call("search_funders", {"product": "MCA", "limit": 3})
check("product-filtered discovery", bool(product["funders"]) and len(product["funders"]) <= 3)
empty = m.call("search_funders", {"q": "zzzznonexistentcompany" + uuid.uuid4().hex, "limit": 1})
check("no results distinct from error", empty["funders"] == [] and empty["total"] == 0 and empty["next_offset"] is None)
missing = m.call("get_funder", {"id": str(uuid.uuid4())})
check("unavailable profile is null", missing["funder"] is None)
for args in [{"id": "not-a-uuid"}, {"id": f["id"], "private_contacts": True}]:
    try:
        m.call("get_funder", args)
    except ValueError:
        rejected = True
    else:
        rejected = False
    check("invalid arguments rejected: " + ("UUID" if len(args) == 1 else "extra field"), rejected)
try:
    m.call("search_funders", {"limit": 51})
except ValueError:
    rejected = True
else:
    rejected = False
check("over-limit rejected", rejected)
# Verify real unknown numeric fields survive the client unchanged.
unknowns = [(f, section, key) for f in a["funders"] + b["funders"] for section in ("amounts", "terms", "eligibility") for key, value in f.get(section, {}).items() if value is None]
check("live unknown numeric field observed", bool(unknowns))
f, section, key = unknowns[0]
d = m.call("get_funder", {"id": f["id"]})["funder"]
check("live unknown remains null in detail", d[section][key] is None)
print(f"{len(passed)} live checks passed; reviewed {len(ids)} unique paginated profiles. Not agent-behavior tests.")
