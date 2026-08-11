"""
Base62 encoding for turning a DB auto-increment ID into a short code.

Why base62 (not base64)? Base64 includes '+' and '/', which aren't
URL-safe without escaping. Base62 (0-9, a-z, A-Z) is alphanumeric only,
so every code is safe to drop straight into a URL path with no encoding.

Why encode the DB id at all, instead of a random string?
- Deterministic: no collision checks needed, ever (id is unique by
  construction from the DB).
- Short: a 32-bit id space fully fits in 6 base62 characters
  (62^6 ≈ 56.8 billion).
Tradeoff: codes are sequential/guessable (id=1 -> code, id=2 -> next
code), which leaks how many URLs you've shortened and lets someone
enumerate them. A production system might XOR/shuffle the id first,
or salt it, to break that predictability. Worth mentioning this
tradeoff explicitly in an interview — it shows you thought about it
rather than stumbling into it.
"""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]

    digits = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        digits.append(ALPHABET[remainder])

    return "".join(reversed(digits))


def decode(short_code: str) -> int:
    num = 0
    for char in short_code:
        num = num * BASE + ALPHABET.index(char)
    return num
