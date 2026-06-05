"""
Wathiq — SSCO Job Title Mapper using Gemini AI.
Semantic mapping of unstructured job titles to official SSCO codes.
Blueprint Section 14, AI Integration 1.
"""
import json
import hashlib
from typing import Optional
from app.config import get_settings

settings = get_settings()

# In-memory cache for fast lookups (resets on restart — use DB in production)
_title_cache: dict[str, dict] = {}

# Known SSCO mappings for common Saudi job titles
KNOWN_TITLES = {
    "مدير المشتريات": {"code": "1321", "title_en": "Procurement Manager", "title_ar": "مدير المشتريات", "is_engineer": False},
    "procurement manager": {"code": "1321", "title_en": "Procurement Manager", "title_ar": "مدير المشتريات", "is_engineer": False},
    "مدير عقود": {"code": "1219", "title_en": "Contracts Manager", "title_ar": "مدير العقود", "is_engineer": False},
    "contracts manager": {"code": "1219", "title_en": "Contracts Manager", "title_ar": "مدير العقود", "is_engineer": False},
    "أخصائي مشتريات": {"code": "3323", "title_en": "Purchasing Specialist", "title_ar": "أخصائي مشتريات", "is_engineer": False},
    "purchasing specialist": {"code": "3323", "title_en": "Purchasing Specialist", "title_ar": "أخصائي مشتريات", "is_engineer": False},
    "مهندس مدني": {"code": "2142", "title_en": "Civil Engineer", "title_ar": "مهندس مدني", "is_engineer": True},
    "civil engineer": {"code": "2142", "title_en": "Civil Engineer", "title_ar": "مهندس مدني", "is_engineer": True},
    "مهندس برمجيات": {"code": "2512", "title_en": "Software Developer", "title_ar": "مهندس برمجيات", "is_engineer": False},
    "software engineer": {"code": "2512", "title_en": "Software Developer", "title_ar": "مهندس برمجيات", "is_engineer": False},
    "محاسب": {"code": "2411", "title_en": "Accountant", "title_ar": "محاسب", "is_engineer": False},
    "accountant": {"code": "2411", "title_en": "Accountant", "title_ar": "محاسب", "is_engineer": False},
    "مدير موارد بشرية": {"code": "1212", "title_en": "HR Manager", "title_ar": "مدير موارد بشرية", "is_engineer": False},
    "hr manager": {"code": "1212", "title_en": "HR Manager", "title_ar": "مدير موارد بشرية", "is_engineer": False},
    "سائق": {"code": "9333", "title_en": "Driver", "title_ar": "سائق", "is_engineer": False},
    "driver": {"code": "9333", "title_en": "Driver", "title_ar": "سائق", "is_engineer": False},
    "حارس أمن": {"code": "5414", "title_en": "Security Guard", "title_ar": "حارس أمن", "is_engineer": False},
    "security guard": {"code": "5414", "title_en": "Security Guard", "title_ar": "حارس أمن", "is_engineer": False},
    "مدير مبيعات": {"code": "1221", "title_en": "Sales Manager", "title_ar": "مدير مبيعات", "is_engineer": False},
    "sales manager": {"code": "1221", "title_en": "Sales Manager", "title_ar": "مدير مبيعات", "is_engineer": False},
    "lead ethical hacker": {"code": "251214", "title_en": "Penetration Tester", "title_ar": "مختبر اختراق الأنظمة والشبكات", "is_engineer": False},
    "penetration tester": {"code": "251214", "title_en": "Penetration Tester", "title_ar": "مختبر اختراق الأنظمة والشبكات", "is_engineer": False},
}


def _normalize_title(title: str) -> str:
    """Normalize a job title for cache lookup."""
    return title.strip().lower()


def _cache_key(title: str) -> str:
    return hashlib.md5(_normalize_title(title).encode()).hexdigest()


async def map_ssco_code(
    raw_title: str,
    use_gemini: bool = True,
) -> dict:
    """
    Map a raw job title to its official SSCO code.
    
    Priority:
    1. In-memory cache (fastest)
    2. Known titles dictionary
    3. Gemini AI (if available and use_gemini=True)
    
    Returns dict with: code, title_en, title_ar, confidence, is_engineering_code
    """
    normalized = _normalize_title(raw_title)
    cache_key_val = _cache_key(raw_title)
    
    # 1. Check in-memory cache
    cached = _title_cache.get(cache_key_val)
    if cached and cached.get("confidence", 0) >= 0.85:
        return cached
    
    # 2. Check known titles dictionary
    if normalized in KNOWN_TITLES:
        result = {**KNOWN_TITLES[normalized], "confidence": 0.95, "reason": "Matched known title"}
        _title_cache[cache_key_val] = result
        return result
    
    # 3. Try Gemini AI if key is configured
    if use_gemini and settings.gemini_api_key:
        try:
            return await _map_with_gemini(raw_title)
        except Exception:
            pass  # Fall through to fuzzy match
    
    # 4. Fuzzy match — find closest known title
    return _fuzzy_match(raw_title)


async def _map_with_gemini(raw_title: str) -> dict:
    """Use Gemini to map a job title to SSCO code."""
    import google.generativeai as genai
    
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""Map this job title to the official Saudi SSCO (Standard Classification of Occupations) code.
    
Job title: "{raw_title}"

Return a JSON object with:
- code: 6-digit SSCO code
- title_en: English title
- title_ar: Arabic title
- confidence: 0.0 to 1.0
- is_engineering_code: true if the code falls in 2141xx-2149xx range
- reason: brief bilingual justification

Return ONLY valid JSON. No markdown, no explanation."""
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0] if "```" in text else text
    
    result = json.loads(text)
    result["confidence"] = float(result.get("confidence", 0.7))
    
    cache_key_val = _cache_key(raw_title)
    _title_cache[cache_key_val] = result
    return result


def _fuzzy_match(raw_title: str) -> dict:
    """Fuzzy match a title against known titles."""
    normalized = _normalize_title(raw_title)
    
    # Check each word
    for known, mapping in KNOWN_TITLES.items():
        known_words = set(known.split())
        title_words = set(normalized.split())
        overlap = len(known_words & title_words)
        if overlap >= 2 or (overlap > 0 and len(known_words) <= 2):
            result = {**mapping, "confidence": 0.75, "reason": f"Fuzzy matched to '{known}'"}
            return result
    
    # Default fallback
    return {
        "code": "999999",
        "title_en": "Unclassified",
        "title_ar": "غير مصنف",
        "confidence": 0.3,
        "is_engineering_code": False,
        "reason": "No match found — manual classification required",
    }