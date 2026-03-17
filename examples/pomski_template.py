import subsequence
import subsequence.constants.instruments.gm_drums as gm_drums
from live_bridge import LiveBridge
from api_feeds import DataFeeds

composition = subsequence.Composition(key="C", bpm=120)
composition.harmony(style="functional_major", cycle_beats=4, gravity=0.8)

# ── Ableton Live bridge ───────────────────────────────────────────────────────
# Requires AbletonOSC remote script installed in Live.
# Live Preferences → Link/Tempo/MIDI → Control Surface → AbletonOSC
#
# From patterns, read Live state via composition.data:
#   vol = composition.data.get("live_track_0_volume", 0.8)
#
# From the REPL or patterns, control Live directly:
#   live.clip_play(track=0, clip=0)       # fire a clip
#   live.scene_play(2)                    # fire a scene
#   live.track_volume(0, 0.9)             # set track volume (0.0–1.0)
#   live.track_mute(1, True)              # mute a track
#   live.device_param(0, 0, 3, 0.7)      # track, device, param, value (0–1)
#   live.set_tempo(128.0)                 # set Live's tempo
#   live.watch("track/0/volume")          # push to composition.data["live_track_0_volume"]
#   live.tracks                           # list of track names
#   live.scenes                           # list of scene names
# ─────────────────────────────────────────────────────────────────────────────

live = LiveBridge(composition)
composition._live_bridge = live   # exposes Live state to web UI

# ── 16 silent pattern slots ───────────────────────────────────────────────────
# Each one is on its own MIDI channel and makes no sound until you redefine it.
# From the REPL, redefine any slot like this:
#
#   @composition.pattern(channel=0, length=4)
#   def ch1(p):
#       p.seq("60 _ 62 _ 64 _ 65 _", velocity=80)
#
# Use composition.data.get("live_...") inside patterns to react to Live state.
# ─────────────────────────────────────────────────────────────────────────────

@composition.pattern(channel=0,  length=4)
def ch1(p):  pass

@composition.pattern(channel=1,  length=4)
def ch2(p):  pass

@composition.pattern(channel=2,  length=4)
def ch3(p):  pass

@composition.pattern(channel=3,  length=4)
def ch4(p):  pass

@composition.pattern(channel=4,  length=4)
def ch5(p):  pass

@composition.pattern(channel=5,  length=4)
def ch6(p):  pass

@composition.pattern(channel=6,  length=4)
def ch7(p):  pass

@composition.pattern(channel=7,  length=4)
def ch8(p):  pass

@composition.pattern(channel=8,  length=4)
def ch9(p):  pass

@composition.pattern(channel=9, length=4, drum_note_map=gm_drums.GM_DRUM_MAP)
def ch10(p): pass

@composition.pattern(channel=10, length=4)
def ch11(p): pass

@composition.pattern(channel=11, length=4)
def ch12(p): pass

@composition.pattern(channel=12, length=4)
def ch13(p): pass

@composition.pattern(channel=13, length=4)
def ch14(p): pass

@composition.pattern(channel=14, length=4)
def ch15(p): pass

@composition.pattern(channel=15, length=4)
def ch16(p): pass

# ── Start ─────────────────────────────────────────────────────────────────────

composition.web_ui()   # http://localhost:8080
composition.live()     # REPL on port 5555

# ── API feeds ─────────────────────────────────────────────────────────────────
# `feeds` is available in the REPL and browser command box.
#
#   feeds.add("btc", "https://api.coinbase.com/v2/prices/BTC-USD/spot",
#             interval=10, extract=lambda r: float(r["data"]["amount"]))
#   feeds.stop("btc")
#   feeds          # show active feeds and current values
#
# Read values in patterns:
#   price = composition.data.get("feed_btc", 0)
# ─────────────────────────────────────────────────────────────────────────────
feeds = DataFeeds(composition)
_orig_build = composition._live_server._build_namespace
composition._live_server._build_namespace = lambda: {**_orig_build(), "feeds": feeds}

composition.play()     # always last
