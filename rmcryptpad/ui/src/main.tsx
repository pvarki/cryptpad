import { createRoot } from "react-dom/client";

import App from "./App";

const root = document.getElementById("root");

if (root) {
  createRoot(root).render(
    <App
      data={{
        url: "https://mtls.cryptpad.localhost:8443",
        sandbox_url: "https://mtls.sandbox.cryptpad.localhost:8443",
      }}
      meta={{ callsign: "VIRTA-1", theme: "dark" }}
    />,
  );
}
