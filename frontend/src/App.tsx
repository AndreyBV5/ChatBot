import ChatWidget from "./components/chatWidget";

export default function App() {
  return (
    <>
      {/* Aquí puedes dejar tu página normal */}
      <h1 style={{ textAlign: "center", marginTop: "40px" }}>Bienvenido a mi demo</h1>

      {/* El chat flotante aparece siempre abajo a la derecha */}
      <ChatWidget />
    </>
  );
}
