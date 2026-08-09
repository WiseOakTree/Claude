"""Audit: was steht wirklich im Code? Keine Selbstauskunft, nur grep."""
import re,os,glob
K={
 "Holdout":      r"SPLIT|holdout|HOLDOUT|Holdout|oos|OOS",
 "Kosten":       r"COST|cost=|fee|Gebuehr|gebuehr|slippage|Slippage",
 "Slippage":     r"slippage|Slippage|half_spread|spread_pct",
 "Funding":      r"funding|Funding",
 "n_eff":        r"n_eff|neff|Einzigartigkeit|uniq",
 "Bonferroni":   r"[Bb]onferroni|holm|Holm|fdr|FDR",
 "Zufallskontr": r"default_rng|np\.random|shuffle|np\.roll|permut",
 "mehr_Assets":  r"for sym in|SYMS|MAERKTE|for s in \(",
 "exec_close":   r'mode="close"|execution.*close|shift\(1\)',
}
rows=[]
for f in sorted(glob.glob("research/*.py")):
    src=open(f,encoding="utf-8",errors="ignore").read()
    rows.append((os.path.basename(f), len(src.splitlines()),
                 {k:bool(re.search(v,src)) for k,v in K.items()}))
print(f"{'Skript':<26}{'Zeilen':>7}"+"".join(f"{k[:9]:>11}" for k in K))
for n,z,d in rows:
    print(f"{n:<26}{z:>7}"+"".join(f"{'ja' if d[k] else '-':>11}" for k in K))
print()
print("ANTEIL DER SKRIPTE MIT DEM JEWEILIGEN MERKMAL")
for k in K:
    a=sum(1 for _,_,d in rows if d[k])
    print(f"  {k:<16}{a:>4} von {len(rows)}  ({a/len(rows)*100:>5.1f} %)")
