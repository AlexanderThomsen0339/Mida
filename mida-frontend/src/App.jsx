import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "../app/components/Header";
import DataTables from "../app/components/DataTables";
import Ingestion from "../app/components/Ingestion";

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/data" element={<DataTables />} />
        <Route path="/ingestion" element={<Ingestion />} />
        <Route path="/" element={<DataTables />} />
      </Routes>
    </BrowserRouter>
  );
}