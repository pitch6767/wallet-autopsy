import json, urllib.request
for i in range(2):
    print(json.dumps(json.loads(urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev/api/sondes",headers={"User-Agent":"x"}),timeout=90).read()), indent=1))
