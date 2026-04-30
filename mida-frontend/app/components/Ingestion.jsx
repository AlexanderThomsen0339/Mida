import { useState } from "react";

const BASE_URL = "http://localhost:8001";

export default function Ingestion() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

    async function triggerIngestion() {
        setLoading(true);
        setStatus(null);
        try {
        const response = await fetch(`${BASE_URL}/trigger/all`, { 
            method: "POST",
            signal: AbortSignal.timeout(5000) // giv op efter 5 sek
        });
        if (response.ok) {
            setStatus({ besked: "Pipeline startet — tjek logs for status." });
        }
        } catch (e) {
        // Timeout er okay — pipeline kører stadig i baggrunden
        setStatus({ besked: "Pipeline kører i baggrunden." });
        } finally {
        setLoading(false);
        }
    }

  return (
    <div style={{ padding: "1rem" }}>
      <h1>Ingestion</h1>
      <button onClick={triggerIngestion} disabled={loading}>
        {loading ? "Kører..." : "Kør alle pipelines"}
      </button>

      {status && (
        <pre style={{ marginTop: "1rem", background: "#f4f4f4", padding: "1rem" }}>
          {JSON.stringify(status, null, 2)}
        </pre>
      )}
    </div>
  );
}