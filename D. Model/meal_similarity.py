"""
Helper similarity/diversity untuk kandidat makanan.

File ini bukan algoritma optimasi.
Fungsinya hanya menyediakan skor similarity sederhana yang bisa dipakai
oleh Greedy/Genetic manual nanti.
"""

from typing import Dict, Iterable, List, Set


PROTEIN_SOURCE_HINTS = {
    "ikan", "fish", "salmon", "tuna", "sarden", "ayam", "chicken", "beef",
    "daging", "meat", "telur", "egg", "tofu", "tempe", "udang", "shrimp"
}


def normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def extract_name_tokens(food_name: str) -> Set[str]:
    """Ambil token nama makanan untuk cek kemiripan kasar."""
    text = normalize_name(food_name)
    separators = [",", "(", ")", "/", "-", "_"]
    for sep in separators:
        text = text.replace(sep, " ")
    tokens = [token for token in text.split() if token]
    return set(tokens)


def get_food_signature(food_row: Dict) -> Dict[str, object]:
    """
    Bentuk signature sederhana makanan untuk similarity check.

    Returns:
        {
            'name_tokens': set,
            'food_group': str,
            'cuisine': str,
            'consumption_label': str,
            'protein_hint': str or None
        }
    """
    food_name = food_row.get("food_name") or food_row.get("name") or ""
    text = normalize_name(food_name)

    protein_hint = None
    for hint in PROTEIN_SOURCE_HINTS:
        if hint in text:
            protein_hint = hint
            break

    return {
        "name_tokens": extract_name_tokens(food_name),
        "food_group": normalize_name(food_row.get("food_group")),
        "cuisine": normalize_name(food_row.get("cuisine") or food_row.get("cuisine_label")),
        "consumption_label": normalize_name(food_row.get("consumption_label")),
        "protein_hint": protein_hint,
    }


def similarity_score(food_a: Dict, food_b: Dict) -> float:
    """
    Skor similarity kasar antara 0 dan 1.

    Semakin tinggi berarti semakin mirip.
    """
    sig_a = get_food_signature(food_a)
    sig_b = get_food_signature(food_b)

    score = 0.0

    if sig_a["protein_hint"] and sig_a["protein_hint"] == sig_b["protein_hint"]:
        score += 0.45

    if sig_a["food_group"] and sig_a["food_group"] == sig_b["food_group"]:
        score += 0.20

    if sig_a["cuisine"] and sig_a["cuisine"] == sig_b["cuisine"]:
        score += 0.10

    if sig_a["consumption_label"] and sig_a["consumption_label"] == sig_b["consumption_label"]:
        score += 0.10

    tokens_a = sig_a["name_tokens"]
    tokens_b = sig_b["name_tokens"]
    if tokens_a and tokens_b:
        overlap = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        if union > 0:
            score += 0.15 * (overlap / union)

    return min(1.0, round(score, 4))


def diversity_penalty(candidate: Dict, selected_items: Iterable[Dict]) -> float:
    """
    Hitung penalti diversity untuk kandidat terhadap daftar item terpilih.

    Semakin besar penalti berarti kandidat terlalu mirip.
    """
    penalty = 0.0
    for item in selected_items:
        penalty = max(penalty, similarity_score(candidate, item))
    return penalty


def is_too_similar(candidate: Dict, selected_items: List[Dict], threshold: float = 0.60) -> bool:
    """True jika kandidat terlalu mirip dengan item yang sudah dipilih."""
    return diversity_penalty(candidate, selected_items) >= threshold
