import json, urllib.request, time
for i in range(3):
    print(json.dumps(json.loads(urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev/api/v1debug",headers={"User-Agent":"x"}),timeout=30).read()), indent=1)[:4000]); time.sleep(20)
