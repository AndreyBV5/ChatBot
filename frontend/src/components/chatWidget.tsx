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
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEDElEQVR4nO2YS0wbVxSG79hjO05EwqowosusUJNscdTCCoWQTZelipKodgx+8hiwhVhFbVXRFrWsKPamTaJEIV00gEgAA4bwCMEGv6QkRGoYk1RdtpA2SgI90R3XHs/DFiMPOCP5lz5pdOfozv+fa3vuNUIllVRSSZKiQ+eIztBzgg5tInr1LFKbSEdwk3QGIcVMEqlNevPwpsEyAhi9ZUR9AQ5/fvOs8eJtMF4cgsPnbzQgNUrTvgwYpFZp3fOAQWoV6ZgBDFKr9C3joG+ZeD8CHO9fN1D+DTflZx5QPuYl5U+CovjwnHjupAs/S1HzHw4kqyp9TERx035pKv3MGn6mIuZxNw7SPJUVQpGVSH1sDtY8xeEsPICPWS5eAGZJgRVgtosYYFuBAIJJfQyUfbsO2p4EIG9MEbQ9CSjrfcrOLXye4gHKep8A8kT2hbLe9QIDeOOnkDd6HXljL5Anuou7I5yQ7I4A0bnK0f4ACGcwBb7OvidFnnqyOyIOgFcp5QV7uoY6YyelzXetWVFX5K2wK8IJCTrE0bYIVF8IGp68gjOPX0Hl96kxXo3MekoYQLxSb5Bn7TLfPB2uJejwrlTHhBOmd5gstknWyKd/AMuZR/+yY7wamfWUsGFSq0iHd1FH6OOMf6Lj4biGXgEphBNq25Y4mu9mzKTBY7wamfWUsGE5fBH0yt1MAE3b8laurokCtM5zWEfFhqyj/BqZ9VS+Fc+mbXkrE0DburSVq2uiL7FrjsMyLDKEx3g1MuupfCueTeviX9wKuO7fSx8+hIgCZA7qQSDNd8SGzHf4NTLrKWGAHL407vmxTADSGfyEdM7uSnVNOKHOPsXxxW/Q8OifjBl8jcd4NTLrqXwrzrFDumZP836IdI4ZC+mYfpM+RaURBbBNcjSPQdXXs6wRTNVXs+wYr0ZmPSUMIPCDPeqc02bJV4HOMXmCtAd+Ie1Tz3X2qR2pjhxyTYO+eZzj8ijoL/2aAl9n35MiT/0h93SOFQ/8R9oCm6R96mddy8xHBW0lyq+EQW8d2xfKvxS/d440XWWRZTpfALzhwiGMjgkwWEYVweiYgPIrIcnNnPHCLRZ1bqcHk1sG8wgYzMN/q/JAUznwe0JnCwBpC8QLCJB0FSvAsW8Sc9rWBdC6F/oKO9T7mbWDNl8xyDzWdIVfE12rO4herUYF/62y1xCDz6CiPw4VP0T49MfZe3s1r+1J/Jk6C8R+REqoeiihx/8S4IN2vi82Nlr7WTM0NjbyqG1qSYXIZdy38fKDnzbiR797Okd4o6//Nz+JrCEdOmjV19eDFHs+J3tib9nOF8M8Vl1dHUiR33R0G3liceSN9qHuRGGf+UJlMpnum0wmyKampmauqKZKKqmkktB+6B3pu5wct5mfIwAAAABJRU5ErkJggg==" alt="chatbot--v1" />
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
