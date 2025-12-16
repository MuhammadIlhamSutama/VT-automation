import vt
import pandas as pd
import time
import os
import json
import random
from itertools import cycle
from urllib.parse import urlparse
from tqdm import tqdm
from dotenv import load_dotenv

# ==============================================================================
# ⚙️ KONFIGURASI
# ==============================================================================
load_dotenv()
API_KEYS = [
    os.getenv("VT_APIKEY1"),
    os.getenv("VT_APIKEY2"),
]

INPUT_FILE = "input.xlsx"
OUTPUT_FILE = "output_vt_scan.xlsx"
DOMAIN_COLUMN = "Domain"
CACHE_FILE = "vt_cache.json"
MAX_RETRIES = 3

# --- PENGATURAN SPEED & SAFETY ---
VALID_KEYS = [k for k in API_KEYS if k.strip()]
TOTAL_KEYS = len(VALID_KEYS)

if TOTAL_KEYS == 0:
    print("❌ Error: Tidak ada API Key yang valid!")
    exit()

DELAY_BETWEEN_REQUESTS = (60 / (4 * TOTAL_KEYS)) + 0.5

# ==============================================================================
# 🧠 FUNGSI & LOGIKA
# ==============================================================================

cache_skor = {}
key_cycle = cycle(VALID_KEYS)

def extract_domain(value):
    if pd.isna(value): return None
    value = str(value).strip()
    if '@' in value: return value.split('@')[-1]
    try:
        parsed = urlparse(value if '://' in value else 'http://' + value)
        return parsed.netloc or parsed.path
    except: return None

def load_cache():
    global cache_skor
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try: cache_skor = json.load(f)
            except: cache_skor = {}

def save_cache():
    with open(CACHE_FILE, 'w') as f: json.dump(cache_skor, f)

def get_vt_score(domain, api_key):
    """Engine Scan: Anti-Ban & Smart Quota"""
    for attempt in range(MAX_RETRIES):
        try:
            with vt.Client(api_key) as client:
                obj = client.get_object(f"/domains/{domain}")
                stats = obj.last_analysis_stats
                malicious = stats['malicious']
                total = sum(stats.values())
                return f"={malicious}/{total}"
        except Exception as e:
            err_msg = str(e)
            if "NotAllowedError" in err_msg or "banned" in err_msg.lower():
                tqdm.write(f"⛔ Key Bermasalah ({api_key[:5]}...).")
                return "Error: Banned"
            if "QuotaExceededError" in err_msg:
                tqdm.write(f"⚠️ Quota Habis. Tidur 60 detik...")
                time.sleep(61)
                continue
            if attempt < MAX_RETRIES - 1:
                sleep_time = (2 ** attempt) + random.uniform(1.0, 3.0)
                time.sleep(sleep_time)
            else:
                return f"Error: {err_msg}"
    return "Error: Timeout"

# ==============================================================================
# 🚀 MAIN PROGRAM
# ==============================================================================

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f" VT Automation")
    print("="*60)
    
    # --- [BAGIAN 1: INPUT PASTE] ---
    print("1. Silakan PASTE domain di bawah ini.")
    print("2. Tekan ENTER 2x (dua kali) setelah selesai paste untuk mulai.")
    print("3. (Biarkan kosong & Enter jika ingin pakai file lama)")
    print("-" * 60)

    lines = []
    while True:
        try:
            line = input()
            if not line: break 
            lines.append(line.strip())
        except EOFError: break

    if lines:
        cleaned_domains = []
        for l in lines:
            parts = l.replace(',', ' ').split()
            for p in parts:
                if p.strip(): cleaned_domains.append(p.strip())
        
        df_new = pd.DataFrame({DOMAIN_COLUMN: cleaned_domains})
        df_new.to_excel(INPUT_FILE, index=False)
        print(f"\n💾 Input disimpan: {len(cleaned_domains)} domain.")
    else:
        print("\n⏩ Menggunakan file input yang sudah ada...")
    
    print("-" * 60 + "\n")

    # --- [BAGIAN 2: SCANNING] ---
    if not os.path.exists(INPUT_FILE):
        print(f"❌ File {INPUT_FILE} tidak ditemukan.")
        exit()

    load_cache()
    df = pd.read_excel(INPUT_FILE)

    if 'VT_Score' not in df.columns: df['VT_Score'] = ""
    else: df['VT_Score'] = df['VT_Score'].astype(str)

    df['__domain'] = df[DOMAIN_COLUMN].apply(extract_domain)
    df['__index'] = df.index
    df_need_scan = df[df['__domain'].notna()][['__index', '__domain']]

    if not df_need_scan.empty:
        print(f"🔍 Mulai Scanning {len(df_need_scan)} baris...")
        for _, row in tqdm(df_need_scan.iterrows(), total=len(df_need_scan)):
            idx = row['__index']
            domain = row['__domain']

            if domain in cache_skor:
                skor = cache_skor[domain]
            else:
                api_key = next(key_cycle)
                skor = get_vt_score(domain, api_key)
                if "Error" not in skor:
                    cache_skor[domain] = skor
                    save_cache()
                time.sleep(DELAY_BETWEEN_REQUESTS)

            df.at[idx, 'VT_Score'] = skor

        df.drop(columns=["__domain", "__index"], inplace=True)
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"\n✅ Scan Selesai! Disimpan di: {OUTPUT_FILE}")
    
    # --- [BAGIAN 3: MENU COPY PASTE] ---
    while True:
        print("\n" + "="*60)
        print("PILIHAN OUTPUT:")
        print("1. Copy SEMUA (Domain + Score) -> Untuk tabel baru")
        print("2. Copy HANYA SCORE          -> Untuk paste ke kolom sebelah domain")
        print("3. Selesai (Keluar)")
        print("="*60)
        
        pilihan = input("Pilih (1/2/3): ")

        try:
            if pilihan == '1':
                # Copy Domain dan Score (tanpa header)
                df[[DOMAIN_COLUMN, 'VT_Score']].to_clipboard(index=False, header=False)
                print("📋 SUKSES: Domain dan Score tersalin ke clipboard!")
                print("   (Tinggal CTRL+V di Excel/Laporan)")
            
            elif pilihan == '2':
                # Copy Score saja (tanpa header)
                df['VT_Score'].to_clipboard(index=False, header=False)
                print("📋 SUKSES: Hanya Score tersalin ke clipboard!")
                print("   (Cocok untuk mengisi kolom kosong di samping domain)")
            
            elif pilihan == '3':
                print("(ノಠ益ಠノ)彡 oɐ1ɔ")
                break
            
            else:
                print("❌ Pilihan tidak valid.")
        
        except Exception as e:
            print(f"❌ Gagal melakukan copy: {e}")
            print("💡 Tips: Pastikan modul 'pyperclip' terinstall (pip install pyperclip)")