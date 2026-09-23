import { useEffect, useState } from "react";

import { fetchHealth } from "./services/api";

type BackendStatus = "checking" | "online" | "offline";

export default function App() {
  const [status, setStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    fetchHealth()
      .then(() => setStatus("online"))
      .catch(() => setStatus("offline"));
  }, []);

  const statusColor: Record<BackendStatus, string> = {
    checking: "bg-nexus-warning",
    online: "bg-nexus-success",
    offline: "bg-nexus-danger",
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 px-6 text-center">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">NEXUS</h1>
        <p className="text-gray-400 max-w-xl">
          Enterprise Multi-Agent Incident Resolution &amp; AI Operations Platform
        </p>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-nexus-border bg-nexus-panel px-4 py-2">
        <span className={`h-2.5 w-2.5 rounded-full ${statusColor[status]}`} />
        <span className="text-sm text-gray-300">
          Backend API:{" "}
          {status === "checking" && "checking connectivity..."}
          {status === "online" && "online"}
          {status === "offline" && "offline"}
        </span>
      </div>

      <p className="text-xs text-gray-500 max-w-md">
        Phase 1 scaffold — incident dashboard, agent traces, and RAG evidence
        views are implemented in later phases.
      </p>
    </div>
  );
}
