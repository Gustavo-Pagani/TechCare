import json
import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "historico_pop_apg_oficial" / "historico_pop_apg"
OUTPUT = ROOT / "apg.geojson"


def utm23s_to_lonlat(easting, northing):
    # EPSG:31983 - SIRGAS 2000 / UTM zone 23S. SIRGAS 2000 is effectively WGS84 for this web prototype.
    a = 6378137.0
    inv_f = 298.257222101
    f = 1 / inv_f
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    k0 = 0.9996
    lon0 = math.radians(-45)

    x = easting - 500000.0
    y = northing - 10000000.0
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2**3 / 256))

    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    j1 = 3 * e1 / 2 - 27 * e1**3 / 32
    j2 = 21 * e1 * e1 / 16 - 55 * e1**4 / 32
    j3 = 151 * e1**3 / 96
    j4 = 1097 * e1**4 / 512
    fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)

    sin_fp = math.sin(fp)
    cos_fp = math.cos(fp)
    tan_fp = math.tan(fp)
    c1 = ep2 * cos_fp * cos_fp
    t1 = tan_fp * tan_fp
    n1 = a / math.sqrt(1 - e2 * sin_fp * sin_fp)
    r1 = a * (1 - e2) / (1 - e2 * sin_fp * sin_fp) ** 1.5
    d = x / (n1 * k0)

    lat = fp - (n1 * tan_fp / r1) * (
        d * d / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1 * c1 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 * t1 - 252 * ep2 - 3 * c1 * c1) * d**6 / 720
    )
    lon = lon0 + (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1 * c1 + 8 * ep2 + 24 * t1 * t1) * d**5 / 120
    ) / cos_fp
    return [round(math.degrees(lon), 7), round(math.degrees(lat), 7)]


def read_dbf(path):
    data = path.read_bytes()
    record_count = struct.unpack("<I", data[4:8])[0]
    header_len = struct.unpack("<H", data[8:10])[0]
    record_len = struct.unpack("<H", data[10:12])[0]

    fields = []
    offset = 32
    while data[offset] != 0x0D:
        raw_name = data[offset : offset + 11].split(b"\x00", 1)[0]
        fields.append(
            {
                "name": raw_name.decode("utf-8", errors="replace").strip(),
                "type": chr(data[offset + 11]),
                "size": data[offset + 16],
                "decimal": data[offset + 17],
            }
        )
        offset += 32

    rows = []
    for i in range(record_count):
        start = header_len + i * record_len
        record = data[start : start + record_len]
        if not record or record[0:1] == b"*":
            continue
        cursor = 1
        row = {}
        for field in fields:
            raw = record[cursor : cursor + field["size"]]
            cursor += field["size"]
            text = raw.decode("utf-8", errors="replace").strip()
            if field["type"] in {"N", "F"} and text:
                try:
                    number = float(text) if field["decimal"] else int(text)
                    row[field["name"]] = number
                except ValueError:
                    row[field["name"]] = text
            else:
                row[field["name"]] = text
        rows.append(row)
    return fields, rows


def signed_area(ring):
    total = 0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        total += x1 * y2 - x2 * y1
    return total / 2


def read_shp(path):
    data = path.read_bytes()
    records = []
    offset = 100
    while offset < len(data):
        _, content_words = struct.unpack(">2i", data[offset : offset + 8])
        offset += 8
        content = data[offset : offset + content_words * 2]
        offset += content_words * 2

        shape_type = struct.unpack("<i", content[:4])[0]
        if shape_type not in {5, 15, 25}:
            raise ValueError(f"Unsupported shape type: {shape_type}")

        num_parts, num_points = struct.unpack("<2i", content[36:44])
        parts = list(struct.unpack(f"<{num_parts}i", content[44 : 44 + 4 * num_parts]))
        points_start = 44 + 4 * num_parts
        points = [
            struct.unpack("<2d", content[points_start + i * 16 : points_start + (i + 1) * 16])
            for i in range(num_points)
        ]

        rings = []
        for idx, part_start in enumerate(parts):
            part_end = parts[idx + 1] if idx + 1 < len(parts) else len(points)
            ring = [utm23s_to_lonlat(x, y) for x, y in points[part_start:part_end]]
            if ring and ring[0] != ring[-1]:
                ring.append(ring[0])
            rings.append(ring)

        outers = []
        holes = []
        for ring in rings:
            if signed_area(ring) < 0:
                outers.append([ring])
            else:
                holes.append(ring)

        if not outers:
            outers = [[ring] for ring in rings]
            holes = []
        for hole in holes:
            outers[0].append(hole)
        records.append(outers)
    return records


def normalize_properties(row, index):
    lower = {key.lower(): value for key, value in row.items()}
    nome = lower.get("apg") or lower.get("nome_compl") or f"APG {index + 1}"
    apg_code = lower.get("id") or lower.get("apg_cod") or lower.get("cod_apg") or index + 1
    return {
        "id": str(nome).lower().replace(" ", "-"),
        "nome": nome,
        "apg": apg_code,
        "fonte_limite": "Prefeitura Municipal de Campinas - Portal de Metadados Geoespaciais, camada Historico de Populacao por APG",
        "precisao": "Geometria oficial baixada em SHP e convertida para GeoJSON para uso no prototipo web",
        **row,
    }


def main():
    fields, rows = read_dbf(SOURCE.with_suffix(".dbf"))
    geometries = read_shp(SOURCE.with_suffix(".shp"))
    if len(rows) != len(geometries):
        raise ValueError(f"DBF rows ({len(rows)}) and SHP geometries ({len(geometries)}) differ")

    features = []
    for index, (row, polygons) in enumerate(zip(rows, geometries)):
        geometry = {"type": "Polygon", "coordinates": polygons[0]} if len(polygons) == 1 else {"type": "MultiPolygon", "coordinates": polygons}
        features.append(
            {
                "type": "Feature",
                "properties": normalize_properties(row, index),
                "geometry": geometry,
            }
        )

    collection = {
        "type": "FeatureCollection",
        "name": "historico_pop_apg_oficial_campinas",
        "metadata": {
            "source": "https://zoneamento.campinas.sp.gov.br/novo_zoneamento/exporta_shp.php?id=171",
            "source_name": "Historico de Populacao por APG",
            "source_owner": "Prefeitura Municipal de Campinas - CDDSE / DEPLAN / SMPDU",
            "source_crs": "EPSG:31983 - SIRGAS 2000 / UTM zone 23S",
            "target_crs": "EPSG:4326-compatible lon/lat for Leaflet",
        },
        "features": features,
    }
    OUTPUT.write_text(json.dumps(collection, ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(features)} APG features")
    print("Fields:", ", ".join(field["name"] for field in fields))


if __name__ == "__main__":
    main()
