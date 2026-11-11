#!/usr/bin/env python3
"""Refresh podcast.json from the Fly'n With Ryan Show YouTube feed."""
import json, re, urllib.request

CHANNEL_ID = "UCemhs_MtUP-3OePRSwAU8fw"
FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL_ID
OUT = "podcast.json"
KEEP = 8

def tag(block, name):
    m = re.search(r"<%s[^>]*>(.*?)</%s>" % (name, name), block, re.S)
    return m.group(1).strip() if m else ""

def unescape(s):
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&apos;", "'"), ("&amp;", "&")):
        s = s.replace(a, b)
    return s

req = urllib.request.Request(FEED, headers={"User-Agent": "ryav-site-feed/1.0"})
xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

episodes = []
for block in xml.split("<entry>")[1:]:
    vid, title, pub = tag(block, "yt:videoId"), tag(block, "title"), tag(block, "published")
    if vid and title:
        episodes.append({"id": vid, "title": unescape(title), "published": pub})
    if len(episodes) == KEEP:
        break

if not episodes:
    raise SystemExit("feed returned no episodes; leaving podcast.json untouched")

data = {
    "channel": "Fly'n With Ryan Show",
    "channelUrl": "https://www.youtube.com/@FlynWithRyanShow",
    "updated": tag(xml.split("<entry>")[0], "published") or "",
    "episodes": episodes,
}

try:
    if json.load(open(OUT))["episodes"] == episodes:
        print("no change")
        raise SystemExit(0)
except (OSError, ValueError, KeyError):
    pass

with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("wrote %d episodes" % len(episodes))
