"""Background processors: Oroboro components from the user's repos acting as observers only (read copies of daily cohort summaries;
no RNG, no writes). Same set as the v4 metastasis testbed, inputs re-mapped to the epilepsy cohort.
  PrincipleAuditor   <- sky-ari-ai OroboroCorePrinciplesGate (InternalDiagnosticFirst census check, TransparentTransmission, AdaptOrDie stagnation)
  MemoryBlender      <- oroboro-os Memory + blender(): rolling digest of every daily snapshot
  MeshRerouteMonitor <- AegisMesh 'reroutes': share of seizures arising outside each brain's dominant focus
  CorrelationPipeline<- oroboro-os Epic_Universe_Correlation_Pipeline: corr(daily discharges, daily Levy)"""
import hashlib, numpy as np
class PrincipleAuditor:
    def __init__(self): self.diag_fail = 0; self.stagnant_max = 0; self._run = 0; self._last = None
    def step(self, s):
        self.diag_fail += int(min(s["census"]) < 0); n = s["seizures"]
        self._run = self._run + 1 if (n == self._last) else 0; self._last = n; self.stagnant_max = max(self.stagnant_max, self._run)
    def finish(self, res): res.update(bg_diag_fail=self.diag_fail, bg_stagnant_max=self.stagnant_max)
class MemoryBlender:
    def __init__(self): self.h = hashlib.sha1(); self.n = 0
    def step(self, s): self.h.update(repr((s["day"], s["census"], s["seizures"], round(s["levy_inc"], 6))).encode()); self.n += 1
    def finish(self, res): res.update(bg_memory_digest=self.h.hexdigest()[:12], bg_memory_grown=self.n)
class MeshRerouteMonitor:
    def __init__(self): self.off = 0; self.tot = 0
    def step(self, s): self.off += s["seizures_offdominant"]; self.tot += s["seizures"]
    def finish(self, res): res.update(bg_offdominant_seizure_share=self.off / self.tot if self.tot else float("nan"))
class CorrelationPipeline:
    def __init__(self): self.a = []; self.b = []
    def step(self, s): self.a.append(s["discharges"]); self.b.append(s["levy_inc"])
    def finish(self, res):
        a, b = np.array(self.a, float), np.array(self.b, float)
        res.update(bg_corr_discharge_levy=float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan"))
def all_background(): return [PrincipleAuditor(), MemoryBlender(), MeshRerouteMonitor(), CorrelationPipeline()]
