import { useEffect, useRef, useState, type JSX } from "react";
import { ask } from "../api";
import "../styles.css";

type Msg = { who: "you" | "bot"; text: string; rich?: JSX.Element };

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    { who: "bot", text: "¡Hola! Pregúntame sobre contraseñas, facturas, precios o ventas." }
  ]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [msgs, open]);

  async function send() {
    const text = q.trim();
    if (!text || loading) return;
    setMsgs(m => [...m, { who: "you", text }]);
    setQ("");
    setLoading(true);
    try {
      const r = await ask(text);
      const content = (
        <div>
          <div>{r.answer}</div>
          {r.suggestions?.length > 0 && (
            <div className="cb-sug">
              {r.intent === "fallback" ? "Sugerencias: " : "¿Te referías a: "}
              {r.suggestions.map((s, i) => (
                <a key={i} onClick={() => setQ(s)}>{s}</a>
              ))}
            </div>
          )}
        </div>
      );
      setMsgs(m => [...m, { who: "bot", text: r.answer, rich: content }]);
    } catch {
      setMsgs(m => [...m, { who: "bot", text: "Ups, ocurrió un error llamando a la API." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Botón flotante */}
      <button
        className="cb-fab"
        aria-label={open ? "Cerrar chat" : "Abrir chat"}
        onClick={() => setOpen(v => !v)}
      >
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path d="M12 2a1 1 0 0 1 1 1v1.06a8.003 8.003 0 0 1 7 7.94v3a4 4 0 0 1-4 4h-1.28A3.5 3.5 0 0 1 12 22a3.5 3.5 0 0 1-2.72-1H8a4 4 0 0 1-4-4v-3a8.003 8.003 0 0 1 7-7.94V3a1 1 0 0 1 1-1Zm-4 8.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Zm8 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 14h8a1 1 0 1 1 0 2H8a1 1 0 0 1 0-2Z" />
        </svg>
      </button>

      {/* Panel del chat */}
      <div className={`cb-panel ${open ? "open" : ""}`} role="dialog" aria-modal="false">
        <div className="cb-card">
          <div className="cb-head">
            <div className="cb-title">Asistente</div>
            <button className="cb-close" onClick={() => setOpen(false)} aria-label="Cerrar">×</button>
          </div>

          <div className="cb-chat" ref={chatRef}>
            {msgs.map((m, i) => (
              <div key={i} className={`cb-msg ${m.who === "you" ? "you" : "bot"}`}>
                {m.rich ?? m.text}
              </div>
            ))}
          </div>

          {/* >>> ESTA ES LA FILA DEL INPUT <<< */}
          <div className="cb-row">
            <input
              ref={inputRef}
              value={q}
              placeholder="Escribe tu pregunta…"
              onChange={e => setQ(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") send(); }}
            />
            <button onClick={send} disabled={loading}>{loading ? "…" : "Enviar"}</button>
          </div>
        </div>
      </div>
    </>
  );
}
