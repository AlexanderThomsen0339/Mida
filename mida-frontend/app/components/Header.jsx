// app/components/Header.jsx
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header style={{ padding: "1rem", borderBottom: "1px solid #ccc", display: "flex", gap: "2rem" }}>
      <span style={{ fontWeight: "bold", fontSize: "1.2rem" }}>MIDA</span>
      <nav style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <Link to="/data">Data</Link>
        <Link to="/ingestion">Ingestion</Link>
      </nav>
    </header>
  );
}