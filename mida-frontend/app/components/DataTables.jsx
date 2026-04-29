import { useState } from "react";
import { getData, login, setToken } from "../utilities/api";

function EarthquakeTable({ data }) {
  return (
    <table border="1" cellPadding="6">
      <thead>
        <tr>
          <th>Titel</th>
          <th>Magnitude</th>
          <th>Sted</th>
          <th>Status</th>
          <th>Tsunami</th>
          <th>Tidspunkt</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.code}>
            <td>{row.title}</td>
            <td>{row.mag}</td>
            <td>{row.place}</td>
            <td>{row.status}</td>
            <td>{row.tsunami === 1 ? "Ja" : "Nej"}</td>
            <td>{new Date(row.time).toLocaleString("da-DK")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function CoinTable({ data }) {
  return (
    <table border="1" cellPadding="6">
      <thead>
        <tr>
          <th>Navn</th>
          <th>Symbol</th>
          <th>Pris (USD)</th>
          <th>Market Cap</th>
          <th>24h %</th>
          <th>Sidst opdateret</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id}>
            <td>
              <img src={row.image} alt={row.name} width={20} />{" "}
              {row.name}
            </td>
            <td>{row.symbol.toUpperCase()}</td>
            <td>{row.current_price.toLocaleString()} $</td>
            <td>{row.market_cap.toLocaleString()} $</td>
            <td>{row.price_change_percentage_24h?.toFixed(2)}%</td>
            <td>{new Date(row.last_updated).toLocaleString("da-DK")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function CountriesTable({ data }) {
  return (
    <table border="1" cellPadding="6">
      <thead>
        <tr>
          <th>Land</th>
          <th>Officielt navn</th>
          <th>Areal (km²)</th>
          <th>Befolkning</th>
          <th>Gini</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            <td>{row["name.common"]}</td>
            <td>{row["name.official"]}</td>
            <td>{row.area?.toLocaleString()}</td>
            <td>{row.population?.toLocaleString()}</td>
            <td>{row["gini.2018"] ?? "N/A"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function DataTables() {
  const [earthquake, setEarthquake] = useState([]);
  const [coins, setCoins] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function hentData() {
    setLoading(true);
    setError(null);
    try {
      const auth = await login("admin", "admin123");
      setToken(auth.access_token);

      const [eq, coin, country] = await Promise.all([
        getData("usgs_earthquake_feed"),
        getData("coingecko_markets"),
        getData("rest_countries"),
      ]);
      setEarthquake(eq.data);
      setCoins(coin.data);
      setCountries(country.data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button onClick={hentData} disabled={loading}>
        {loading ? "Henter..." : "Hent data"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {earthquake.length > 0 && (
        <>
          <h2>Jordskælv</h2>
          <EarthquakeTable data={earthquake} />
        </>
      )}

      {coins.length > 0 && (
        <>
          <h2>Krypto</h2>
          <CoinTable data={coins} />
        </>
      )}

      {countries.length > 0 && (
        <>
          <h2>Lande</h2>
          <CountriesTable data={countries} />
        </>
      )}
    </div>
  );
}