# Character counter for the series.
# WeChat "visible chars": whole file; drop image lines ![..](..), drop URLs (incl. markdown link targets),
#   drop table separator rows, drop markdown syntax chars (# * > ` |), count non-whitespace chars.
#   Also reports a stricter count that keeps spaces inside lines.
# XHS: same stripping, count all non-whitespace chars.
import re,sys
def clean(t):
    t=re.sub(r'^!\[[^\]]*\]\([^)]*\)\s*$','',t,flags=re.M)
    t=re.sub(r'\]\([^)]*\)',']',t)              # markdown link target
    t=re.sub(r'https?://\S+','',t)
    t=re.sub(r'^\s*\|?\s*:?-{3,}.*$','',t,flags=re.M)  # table separator rows
    t=re.sub(r'[#*>`|]','',t)
    t=t.replace('[','').replace(']','')
    return t
def counts(path):
    t=clean(open(path,encoding='utf-8').read())
    nonws=len(re.sub(r'\s','',t))
    withsp=len(re.sub(r'[\n\r\t]','',re.sub(r' {2,}',' ',t)))
    return nonws,withsp
if __name__=='__main__':
    for p in sys.argv[1:]:
        print(p,*counts(p))
