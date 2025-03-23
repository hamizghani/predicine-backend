from datetime import timedelta


def estimate_stockout(row):
    # Faktor permintaan dengan bobot
    demand_factor = (
        (row["disease_score_1"] * 0.45) + 
        (row["disease_score_2"] * 0.30) + 
        (row["disease_score_3"] * 0.25)
    )
    
    # Pastikan demand_factor tidak nol
    demand_factor = max(demand_factor, 0.1)
    
    # Perhitungan estimasi hari sebelum stok habis
    estimated_days = (
        row["stock"] / (demand_factor * row["avg_visitor_weekly"] * 0.05)
    ) * (1 + row["supplier_reliability"] * 0.5)

    # Pastikan nilai tidak negatif atau terlalu kecil
    estimated_days = max(estimated_days, 7)  # Minimal 7 hari agar tidak terlalu kecil

    return row["record_timestamp"] + timedelta(days=int(estimated_days))
