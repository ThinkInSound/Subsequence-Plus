from subsequence import Composition

composition = Composition(key="C", bpm=120)

# ── 16 silent pattern slots ───────────────────────────────────────────────────
# Each one is on its own MIDI channel and makes no sound until you redefine it.
# From the REPL, redefine any slot like this:
#
#   @composition.pattern(channel=1, length=4)
#   def ch1(p):
#       p.seq("60 _ 62 _ 64 _ 65 _", velocity=80)
#
# Change the name (ch1, ch2 etc) and channel number to match the slot you want.
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

@composition.pattern(channel=9,  length=4)
def ch9(p):  pass

@composition.pattern(channel=9, length=4)
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
composition.play()     # always last
