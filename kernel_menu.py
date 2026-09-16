#!/usr/bin/env python3
import sys, re, time, os, platform, hashlib, signal

# --- TRAP ---
def bye(*a):
    print("\nExiting....")
    sys.exit(0)
signal.signal(signal.SIGINT, bye)

FILE = ".config"
MD5 = "d5a1a6423a2928c1c6290ea44eaf599a"
SHA1 = "696f7e6fdc585e2260e618f47fc79dd3c2fd6501"
SHA256 = "d2e8aa3174545290fe9ca0164220630812495cb60e7891198ca5f72749d3c86d"

if not os.path.exists(FILE):
    print(f"[-] {FILE} gak ada"); sys.exit(1)
data = open(FILE, 'rb').read()
if hashlib.md5(data).hexdigest()!= MD5: print("[-] MD5 mismatch"); sys.exit(1)
if hashlib.sha1(data).hexdigest()!= SHA1: print("[-] SHA1 mismatch"); sys.exit(1)
if hashlib.sha256(data).hexdigest()!= SHA256: print("[-] SHA256 mismatch"); sys.exit(1)
print(f"[+] OK: {FILE} valid")

CONFIG_FILE = sys.argv[1] if len(sys.argv) > 1 else ".config"
OUTPUT_FILE = "saved.config"
SHOW_MODE = 25
TYPE_SPEED = 0.004
ENABLE_TYPING = True

B='\033[1m'; C='\033[96m'; G='\033[92m'; Y='\033[93m'; R='\033[91m'; W='\033[0m'
SKULL = f"{R}{B}\n██╗ ██╗███████╗███████╗ ██████╗ \n╚██╗██╔╝██╔════╝██╔════╝██╔════╝ \n ╚███╔╝ █████╗ ███████╗██║ ███╗\n ██╔██╗ ██╔══╝ ╚════██║██║ ██║\n██╔╝ ██╗███████╗███████║╚██████╔╝\n╚═╝ ╚═╝╚══════╝╚══════╝ ╚═════╝ \n{W}"

def tprint(text, delay=TYPE_SPEED):
    if ENABLE_TYPING and delay>0:
        for ch in text: print(ch,end='',flush=True); time.sleep(delay)
        print()
    else: print(text)
def clear(): os.system('cls' if os.name=='nt' else 'clear')
def get_sysinfo(): return time.strftime("%Y-%m-%d %H:%M:%S"), platform.machine(), platform.release()
def parse_config(lines):
    entries=[]
    for idx,line in enumerate(lines):
        l=line.rstrip('\n')
        m=re.match(r'^(CONFIG_[A-Z0-9_]+)=(.*)$',l)
        if m: entries.append({"line":idx,"type":"set","name":m.group(1),"val":m.group(2)}); continue
        m=re.match(r'^#\s*(CONFIG_[A-Z0-9_]+)\s+is\s+not\s+set$',l)
        if m: entries.append({"line":idx,"type":"unset","name":m.group(1),"val":"n"}); continue
        entries.append({"line":idx,"type":"other","raw":line.rstrip('\n')})
    return entries
def print_batch(entries,ptr,end):
    tprint(f"{Y}⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻{W}")
    tprint(f"\n{B}{C}=== Line {ptr+1} - {end} / {len(entries)} ==={W}")
    disp_map={}; n=1
    for e in entries[ptr:end]:
        if e["type"]=="other": print(f" {W}| {e.get('raw','')}")
        else:
            col=G if e['val'] in ['y','m'] else R if e['val']=='n' else Y
            print(f"{B}[{n:2d}]{W} | {B}{e['name']}{W} = {col}{e['val']}{W}")
            disp_map[n]=e; n+=1
    return disp_map
def save_now(lines):
    with open(OUTPUT_FILE,'w') as f: f.writelines(lines)
    tprint(f"\n{G}[+] Saved to {OUTPUT_FILE} | {len(lines)} lines{W}")

def main():
    clear()
    date,arch,kernel=get_sysinfo()
    print(SKULL)
    tprint(f"{B}{R}I Don't Need Ncurses{W}")
    tprint(f"{B}{G}KBUILD SAHRUL GUNAWAN ID v3.2{W}")
    tprint(f"{Y}----------------------------------------{W}")
    tprint(f"{B}{C}Date{W}: {date} | {arch} | {kernel}")
    tprint(f"{Y}----------------------------------------{W}\n")

    try: lines=open(CONFIG_FILE,'r').readlines()
    except EOFError: bye()
    entries=parse_config(lines); ptr=0; total=len(entries)
    tprint(f"{C}Loaded {total} lines. SHOW_MODE={SHOW_MODE}{W}")
    tprint(f"{Y}Aturan: 1 3 4 -> set 1 value | q=quit | s=save{W}\n")

    while ptr < total:
        end=min(ptr+SHOW_MODE,total)
        disp_map=print_batch(entries,ptr,end)
        tprint(f"{Y}⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻{W}")
        try: sel=input(f"\n{B}{C}root@kbuild~# {W}").strip().lower()
        except EOFError: bye()

        if sel=='q': print(f"{R}Quit tanpa save.{W}"); break
        if sel=='s': save_now(lines); continue
        if sel=='w': save_now(lines); break

        if sel!='':
            try:
                nums=list(set([int(x) for x in sel.split()]))
                nums=[x for x in nums if x in disp_map]
            except: tprint(f"{R}Input salah{W}"); nums=[]
            if nums:
                try: common_val=input(f"{B}{Y}Set value [y/n/m/value] --> {W}").strip()
                except EOFError: bye()
                if common_val!="":
                    for num in nums:
                        e=disp_map[num]
                        if common_val=="n": lines[e["line"]]=f"# {e['name']} is not set\n"
                        else: lines[e["line"]]=f"{e['name']}={common_val}\n"
                        tprint(f" -> Set {e['name']}={common_val}",0.001)
                    entries=parse_config(lines)
        try: nxt=input(f"\n{B}{C}next y/n (s=save q=quit)? {W}").strip().lower()
        except EOFError: bye()
        if nxt=='q': break
        if nxt=='s': save_now(lines); continue
        if nxt=='n': continue
        else: ptr=end
    else:
        save_now(lines)

    tprint(f"{B}{G}Done! cp {OUTPUT_FILE}.config && make olddefconfig{W}")

if __name__=="__main__":
    main()
