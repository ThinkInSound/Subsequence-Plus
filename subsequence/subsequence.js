/**
 * subsequence.js — Max for Live node.script
 *
 * Connects to the subsequence WebSocket (ws://localhost:8765),
 * reports connection state and live BPM back to the Max patch.
 *
 * Messages OUT to Max (via Max.outlet):
 *   connected 1 / connected 0   — connection state
 *   bpm <value>                  — live BPM as float
 *
 * Browser opening is handled natively by Max via the
 * "; max launchbrowser" message box in the patch.
 */

const Max = require("max-api");

const WS_URL       = "ws://localhost:8765";
const RECONNECT_MS = 3000;

let ws             = null;
let reconnectTimer = null;

function clearReconnect() {
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
}

function scheduleReconnect() {
    clearReconnect();
    reconnectTimer = setTimeout(connect, RECONNECT_MS);
}

function connect() {
    clearReconnect();
    if (ws) { try { ws.terminate(); } catch (_) {} ws = null; }

    let WS;
    try {
        WS = require("ws");
    } catch (e) {
        Max.post("ws not found — send [script npm install ws] to the node.script object", Max.POST_LEVELS.ERROR);
        scheduleReconnect();
        return;
    }

    ws = new WS(WS_URL);

    ws.on("open", () => {
        Max.outlet("connected", 1);
        Max.post("Connected to subsequence");
    });

    ws.on("message", data => {
        try {
            const msg = JSON.parse(data);
            if (msg.bpm !== undefined) {
                Max.outlet("bpm", parseFloat(msg.bpm));
            }
        } catch (_) {}
    });

    ws.on("close", () => {
        Max.outlet("connected", 0);
        scheduleReconnect();
    });

    ws.on("error", () => {
        Max.outlet("connected", 0);
        try { ws.terminate(); } catch (_) {}
        ws = null;
        scheduleReconnect();
    });
}

connect();
