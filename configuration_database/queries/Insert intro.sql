USE Configuration_database;
GO

INSERT INTO Sources (SourceName, Source_URL, Authentication)
VALUES 
(
    'USGS Earthquake Feed',
    'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson',
    NULL
),
(
    'CoinGecko Markets',
    'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100',
    NULL
),
(
    'REST Countries',
    'https://restcountries.com/v3.1/all?fields=name,population,area,gini,gdp',
    NULL
);
GO

-- Bekræft at de er indsat korrekt
SELECT * FROM Sources;
GO