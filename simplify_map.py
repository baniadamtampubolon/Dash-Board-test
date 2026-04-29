import geopandas as gpd
import time
import os

input_file = "Database/indonesia-kota-kabupaten.json"
output_file = "Database/indonesia-kabkot-simplified.geojson"

print(f"Loading {input_file} (This might take a moment)...")
start_time = time.time()

# Load the large GeoJSON
gdf = gpd.read_file(input_file)
print(f"Loaded {len(gdf)} features in {time.time() - start_time:.2f} seconds.")

# Simplify the geometry
# 0.005 degrees is roughly 500 meters. This will drastically reduce file size
# while maintaining the shape of the regencies.
print("Simplifying geometry (tolerance=0.005)...")
start_time = time.time()
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.005, preserve_topology=True)
print(f"Simplification done in {time.time() - start_time:.2f} seconds.")

# Save the simplified GeoJSON
print(f"Saving to {output_file}...")
start_time = time.time()
gdf.to_file(output_file, driver='GeoJSON')
print(f"Saved successfully in {time.time() - start_time:.2f} seconds.")

# Compare file sizes
in_size = os.path.getsize(input_file) / (1024 * 1024)
out_size = os.path.getsize(output_file) / (1024 * 1024)
print(f"\nSize Reduction:")
print(f"Original: {in_size:.2f} MB")
print(f"Simplified: {out_size:.2f} MB")
print(f"Reduced by: {(1 - out_size/in_size)*100:.2f}%")
