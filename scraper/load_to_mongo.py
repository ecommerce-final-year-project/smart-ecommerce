import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne

load_dotenv()
VERI_KLASORU = Path(os.environ["VERI_KLASORU"])
SADECE = os.getenv("SADECE_KATEGORI") or None

client = MongoClient(os.environ["MONGO_URI"])
koleksiyon = client["catalog_db"]["products"]

ORTAK = {"ad", "marka", "en_dusuk_fiyat_tl", "epey_puani",
         "kullanici_puani", "url", "gorsel"}


def sayi(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def anahtar(k):
    # Mongo anahtarlarında nokta ve $ sorun çıkarır
    return k.strip().replace(".", " ").replace("$", "")


def belge_yap(satir, kategori, simdi):
    url = satir.get("url")
    if not isinstance(url, str) or not url.strip():
        return None
    url = url.strip()
    yol = urlparse(url).path.strip("/").removesuffix(".html")
    belge = {
        "_id": f"epey:{yol}",
        "source": "epey",
        "kategori": kategori,
        "url": url,
        "loaded_at": simdi,
    }
    for alan in ("ad", "marka", "gorsel"):
        v = satir.get(alan)
        if isinstance(v, str) and v.strip():
            belge[alan] = v.strip()
    for alan in ("en_dusuk_fiyat_tl", "epey_puani", "kullanici_puani"):
        n = sayi(satir.get(alan))
        if n is not None and n == n:  # NaN değilse
            belge[alan] = n
    specs = {
        anahtar(k): v.strip()
        for k, v in satir.items()
        if k not in ORTAK and k != "Unnamed: 0"
        and isinstance(v, str) and v.strip()
    }
    if specs:
        belge["specs"] = specs
    return belge


def main():
    simdi = datetime.now(timezone.utc)
    dosyalar = sorted(VERI_KLASORU.glob("*.csv"))
    if SADECE:
        dosyalar = [d for d in dosyalar if d.stem == SADECE]
    print("İşlenecek dosya sayısı:", len(dosyalar))

    for yol in dosyalar:
        df = pd.read_csv(yol, sep=";", dtype=str, encoding="utf-8-sig")
        islemler, atlanan = [], 0
        for satir in df.to_dict("records"):
            belge = belge_yap(satir, yol.stem, simdi)
            if belge is None:
                atlanan += 1
                continue
            islemler.append(ReplaceOne({"_id": belge["_id"]}, belge, upsert=True))
        if islemler:
            sonuc = koleksiyon.bulk_write(islemler, ordered=False)
            print(f"{yol.stem}: {len(df)} satır | yeni {sonuc.upserted_count}, "
                  f"güncellenen {sonuc.modified_count} | url'siz atlanan {atlanan}")

    koleksiyon.create_index("kategori")
    koleksiyon.create_index("marka")
    print("Toplam belge:", koleksiyon.count_documents({}))


if __name__ == "__main__":
    main()