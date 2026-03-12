import pandas as pd

df = pd.read_csv("airport-codes.csv")

# keep airports with IATA codes
df = df[df["iata_code"].notna()]

# split coordinates
df[["latitude", "longitude"]] = df["coordinates"].str.split(",", expand=True)

df_clean = pd.DataFrame({
    "airport_code": df["iata_code"],
    "airport_name": df["name"],
    "city": df["municipality"],          # correct city
    "country": df["iso_country"],        # country code (AE)
    "country_code": df["iso_country"],   # same for now
    "latitude": df["latitude"],
    "longitude": df["longitude"],
    "timezone": df["continent"],
    "is_major_airport": False
})

df_clean.to_csv("airports_clean.csv", index=False)

print("Airports prepared:", len(df_clean))