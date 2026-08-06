"""Minimaler PDF-Textextraktor -- reines Python, nur zlib.
Umgeht die kaputte cryptography-Installation."""
import re, zlib, sys

data=open(sys.argv[1],"rb").read()
# Alle Streams finden und dekomprimieren
out=[]
for m in re.finditer(rb"stream\r?\n", data):
    start=m.end()
    e=data.find(b"endstream", start)
    if e<0: continue
    raw=data[start:e]
    try: txt=zlib.decompress(raw)
    except Exception:
        try: txt=zlib.decompressobj().decompress(raw)
        except Exception: continue
    out.append(txt)

def unescape(s):
    s=s.replace(rb"\(",b"(").replace(rb"\)",b")").replace(rb"\\",b"\\")
    return s

pages=[]
for blob in out:
    chunks=[]
    # Tj / TJ Operatoren
    for m in re.finditer(rb"\((?:[^()\\]|\\.)*\)", blob):
        chunks.append(unescape(m.group(0)[1:-1]))
    if not chunks: continue
    t=b" ".join(chunks).decode("latin-1", errors="replace")
    t=re.sub(r"\s+"," ",t).strip()
    if len(t)>40: pages.append(t)

print(f"### {len(pages)} Textbloecke aus {len(out)} Streams\n")
for i,p in enumerate(pages,1):
    print(f"--- Block {i} ---")
    print(p[:4000])
    print()
