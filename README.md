# Related Messages RSA Lab

A small, reproducible Python demonstration of the Franklin–Reiter related-message attack described in [the walkthrough](https://medium.com/@jishnujishnus025/picoctf-2026-related-messages-medium-walkthrough-f03066d2f8bc). It uses generated toy RSA values and a harmless numeric message; it does not include the challenge ciphertexts, modulus, plaintexts, or flag.

## Objectives

- Explain how reusing textbook RSA with a known additive plaintext relationship can expose a message.
- Reproduce the polynomial-GCD recovery on controlled, synthetic inputs.
- Keep CTF artifacts private and avoid publishing recovered flags.

## Prerequisites

- Python 3.11 or newer
- Docker (optional)

The implementation uses only the Python standard library.

## Reproduce

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[test]'
python -m related_messages demo --output data/demo.json
python -m related_messages solve data/demo.json
```

The demo uses fixed, tiny primes and a numeric toy plaintext so results are repeatable. The solver prints only a success marker, recovered byte count, and SHA-256 digest; it does not print plaintext bytes.

## Input format and usage

Input is JSON with decimal strings for large integers:

```json
{
  "n": "1000036000099",
  "e": 17,
  "c1": "<ciphertext for m2 + delta>",
  "c2": "<ciphertext for m2>",
  "delta": -3
}
```

Use your own authorized, synthetic or competition-provided values:

```sh
python -m related_messages solve path/to/input.json
```

Here `c1 = (m2 + delta)^e mod n` and `c2 = m2^e mod n`. Inputs must satisfy `0 <= m2, m2 + delta < n`; the polynomial algorithm also requires invertible leading coefficients during Euclidean reduction. A non-invertible coefficient is reported as an unsupported/non-coprime case rather than silently guessed.

## Approach

Over integers modulo `n`, form `f(x) = (x + delta)^e - c1` and `g(x) = x^e - c2`. Their common root is `m2`; the polynomial Euclidean algorithm recovers a linear factor when its divisions are valid. This is an educational implementation for the challenge's relationship, not a general-purpose RSA toolkit.

## Safe disclosure

Do not commit raw flags, recovered plaintexts, private keys, challenge outputs, screenshots containing secrets, or unredacted terminal logs. Keep real challenge artifacts outside the repository. Use synthetic examples for issues and pull requests, and follow the event's disclosure rules. This repository intentionally ships only harmless toy inputs.

## Development

```sh
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## License

MIT. See [LICENSE](LICENSE).
