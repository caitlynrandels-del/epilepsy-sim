"""Counter-based random numbers (copied in spirit from the v4 metastasis testbed, oro_cascade.U).
A uniform depends only on (seed, id, day, stream), never on how the system is partitioned, so independent parts can be
processed separately and recombined exactly (delta reconciliation). Speculative modeling only."""
import numpy as np
M64 = (1 << 64) - 1
def _u64(x): return np.uint64(x & M64)
def U(seed, ids, day, stream):
    base = _u64(seed * 0xD1B54A32D192ED03 + day * 0x8CB92BA72F3D8DD7 + stream * 0xFF51AFD7ED558CCD)
    with np.errstate(over="ignore"):
        x = ids.astype(np.uint64) * _u64(0x9E3779B97F4A7C15) + base
        x ^= x >> np.uint64(30); x *= _u64(0xBF58476D1CE4E5B9)
        x ^= x >> np.uint64(27); x *= _u64(0x94D049BB133111EB)
        x ^= x >> np.uint64(31)
    return (x >> np.uint64(11)).astype(np.float64) * (1.0 / (1 << 53))

def poisson_inv(u, lam, kmax=200):
    """vectorised Poisson inversion (deterministic given u)."""
    k = np.zeros(u.shape, dtype=np.int64)
    p = np.exp(-lam); c = p.copy(); m = u > c
    j = 0
    while m.any() and j < kmax:
        j += 1; idx = np.nonzero(m)[0]
        p[idx] = p[idx] * lam[idx] / j; c[idx] += p[idx]; k[idx] = j
        m[idx] = u[idx] > c[idx]
    return k

def binom_inv(u, n, p):
    """vectorised Binomial(n, p) inversion; n int array, p float array or scalar."""
    n = np.asarray(n, dtype=np.int64); p = np.broadcast_to(np.asarray(p, dtype=np.float64), n.shape).copy()
    out = np.zeros(n.shape, dtype=np.int64)
    idx = np.nonzero((n > 0) & (p > 0))[0]
    if idx.size == 0: return out
    nn = n[idx]; pp = np.clip(p[idx], 0, 1); uu = u[idx]
    full = pp >= 1.0
    q = 1 - pp
    with np.errstate(divide="ignore", invalid="ignore"):
        pk = np.where(full, 0.0, q ** nn); c = pk.copy(); k = np.zeros(idx.size, dtype=np.int64)
        m = (uu > c) & ~full
        while m.any():
            j = np.nonzero(m)[0]
            pk[j] = pk[j] * (nn[j] - k[j]) / (k[j] + 1) * pp[j] / q[j]; k[j] += 1; c[j] += pk[j]
            m[j] = (uu[j] > c[j]) & (k[j] < nn[j])
    k[full] = nn[full]
    out[idx] = k
    return out
