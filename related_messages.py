"""Safe educational Franklin–Reiter related-message RSA demonstration."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Sequence

Poly = list[int]


def trim(poly: Poly) -> Poly:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_sub(a: Poly, b: Poly, n: int) -> Poly:
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % n
                 for i in range(max(len(a), len(b)))])


def poly_mul(a: Poly, b: Poly, n: int) -> Poly:
    out = [0] * (len(a) + len(b) - 1)
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            out[i + j] = (out[i + j] + av * bv) % n
    return trim(out)


def poly_pow(base: Poly, exponent: int, n: int) -> Poly:
    if exponent < 0:
        raise ValueError("polynomial exponent must be nonnegative")
    result, factor, power = [1], base, exponent
    while power:
        if power & 1:
            result = poly_mul(result, factor, n)
        factor = poly_mul(factor, factor, n)
        power >>= 1
    return result


def poly_divmod(a: Poly, b: Poly, n: int) -> tuple[Poly, Poly]:
    a, b = trim(a[:]), trim(b[:])
    if b == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if a == [0] or len(a) < len(b):
        return [0], a
    try:
        inverse = pow(b[-1], -1, n)
    except ValueError as exc:
        raise ValueError("non-invertible polynomial leading coefficient") from exc
    quotient = [0] * (len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        degree = len(a) - len(b)
        factor = (a[-1] * inverse) % n
        quotient[degree] = factor
        for i, coefficient in enumerate(b):
            a[degree + i] = (a[degree + i] - factor * coefficient) % n
        trim(a)
    return trim(quotient), trim(a)


def polynomial_gcd(a: Poly, b: Poly, n: int) -> Poly:
    while b != [0]:
        _, remainder = poly_divmod(a, b, n)
        a, b = b, remainder
    if a == [0]:
        return a
    try:
        inverse = pow(a[-1], -1, n)
    except ValueError as exc:
        raise ValueError("GCD has a non-invertible leading coefficient") from exc
    return [(coefficient * inverse) % n for coefficient in a]


def recover_related_message(n: int, e: int, c1: int, c2: int, delta: int) -> int:
    """Recover m2 from c1=(m2+delta)^e mod n and c2=m2^e mod n."""
    if n <= 1 or e < 2:
        raise ValueError("n must exceed 1 and e must be at least 2")
    if not (0 <= c1 < n and 0 <= c2 < n):
        raise ValueError("ciphertexts must be canonical residues in [0, n)")
    x = [0, 1]
    shifted = [delta % n, 1]
    f = poly_sub(poly_pow(shifted, e, n), [c1], n)
    g = poly_sub(poly_pow(x, e, n), [c2], n)
    common = polynomial_gcd(f, g, n)
    if len(common) != 2 or common[1] != 1:
        raise ValueError("expected a linear common factor; inputs may not be related")
    return (-common[0]) % n


def load_input(path: Path) -> dict[str, int]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = {"n", "e", "c1", "c2", "delta"}
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("JSON must contain exactly n, e, c1, c2, and delta")
    return {key: int(value) for key, value in raw.items()}


def demo_values() -> dict[str, int]:
    """Create deterministic toy RSA ciphertexts for harmless integer 12345."""
    p, q, e = 1_000_003, 1_000_033, 17
    n, phi = p * q, (p - 1) * (q - 1)
    if math.gcd(e, phi) != 1:
        raise RuntimeError("demo parameters do not define an RSA exponent")
    m2, delta = 12_345, -3
    return {"n": n, "e": e, "c1": pow(m2 + delta, e, n), "c2": pow(m2, e, n), "delta": delta}


def run_solve(path: Path) -> int:
    values = load_input(path)
    recovered = recover_related_message(**values)
    encoded = recovered.to_bytes(max(1, (recovered.bit_length() + 7) // 8), "big")
    digest = hashlib.sha256(encoded).hexdigest()
    print(f"recovery=success bytes={len(encoded)} sha256={digest}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="write harmless deterministic sample input")
    demo.add_argument("--output", type=Path, default=Path("data/demo.json"))
    solve = subparsers.add_parser("solve", help="recover from an authorized JSON input")
    solve.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    if args.command == "demo":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({k: str(v) if k not in {"e", "delta"} else v
                                          for k, v in demo_values().items()}, indent=2) + "\n", encoding="utf-8")
        print(f"wrote synthetic demo input: {args.output}")
        return 0
    return run_solve(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
