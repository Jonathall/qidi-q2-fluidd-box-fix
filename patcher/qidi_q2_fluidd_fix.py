#!/usr/bin/env python3
# QIDI Q2 Fluidd Box panel fix - patcher (V1.0.0)
# Verifies the EXACT stock bundle of the QIDI Q2 firmware 01.01.03.01+
# (Fluidd v1.30.5, index-DlFvHGAh.js - the same bundle file the Plus 5
# ships) by SHA-256, applies anchored edits, writes the patched bundle.
# Refuses any other input, including an already-patched bundle.
# GPL-3.0. See docs/changes.md for the per-change documentation.
import hashlib, json, sys

STOCK_SHA256 = "178b2e076d3a75716819ee13f9ea1f0c92e536546c8b2adafde8632f6723710c"
STAMP = 'window.__qidiQ2Fix="1.0.0";'
DB_LINK = ".qidi_filaments"

FALLBACK_DB = {"QIDI": ["PLA Basic", "PLA Matte Basic", "PLA Rapido", "PLA Rapido Matte", "PLA Rapido Metal", "PLA Silk", "WOOD Rapido", "PLA-CF", "ASA", "ASA-Aero", "ABS-GF", "ASA-CF20 Core", "ABS Odorless", "ABS Rapido", "ABS Rapido Metal", "PC/ABS-FR", "PETG Basic", "PETG Rapido", "PETG Tough", "PETG Translucent", "PETG-CF", "PETG-GF", "PAHT-CF", "PA6-CF", "PA12-CF", "PAHT-GF", "UltraPA", "UltraPA-CF25", "PPS-CF", "PPS-GF", "Support For PET/PA", "Support For PAHT", "PET-CF", "PET-GF", "TPU-Aero", "TPU 95A-HF", "TPU-GF", "PEBA 95A"], "Generic": ["ABS", "PC", "PETG", "PLA", "PLA Silk", "PLA+", "TPU 95A"], "Bambu": ["ABS", "PETG", "PLA"], "HATCHBOX": ["ABS", "PETG", "PLA"], "Overture": ["ABS", "PLA"], "Polymaker": ["ABS", "PLA", "PLA-HT"]}
FILA_MAP = {"QIDI|pla rapido": 1, "QIDI|pla rapido metal": 3, "QIDI|pla silk": 4, "QIDI|pla-cf": 5, "QIDI|wood rapido": 6, "QIDI|pla basic": 7, "QIDI|pla matte basic": 8, "Generic|pla+": 9, "QIDI|abs rapido": 11, "QIDI|abs-gf": 12, "QIDI|abs rapido metal": 13, "QIDI|abs odorless": 14, "QIDI|asa": 18, "QIDI|asa-aero": 19, "QIDI|asa-cf20 core": 20, "Generic|pc": 23, "QIDI|ultrapa": 24, "QIDI|pa6-cf": 25, "QIDI|ultrapa-cf25": 26, "QIDI|pa12-cf": 27, "QIDI|paht-cf": 30, "QIDI|paht-gf": 31, "QIDI|support for paht": 32, "QIDI|support for pet/pa": 33, "QIDI|pc/abs-fr": 34, "QIDI|peba 95a": 36, "QIDI|pet-cf": 37, "QIDI|pet-gf": 38, "QIDI|petg basic": 39, "QIDI|petg tough": 40, "QIDI|petg rapido": 41, "QIDI|petg-cf": 42, "QIDI|petg-gf": 43, "QIDI|pps-cf": 44, "QIDI|petg translucent": 45, "QIDI|pps-gf": 46, "QIDI|tpu-aero": 49, "QIDI|tpu 95a-hf": 50, "QIDI|pla rapido matte": 51, "QIDI|tpu-gf": 52, "Generic|abs": 53, "Generic|petg": 54, "Generic|pla": 55, "Generic|pla silk": 56, "Generic|tpu 95a": 57, "Bambu|abs": 58, "Bambu|petg": 59, "Bambu|pla": 60, "HATCHBOX|abs": 61, "HATCHBOX|petg": 62, "HATCHBOX|pla": 63, "Overture|abs": 64, "Overture|pla": 65, "Polymaker|abs": 66, "Polymaker|pla": 67, "Polymaker|pla-ht": 68}

PANEL_MEMBERS = r"""
get items(){const t=this.q2RawItems.slice();for(let m=0;m<16&&m<this.boxCount*4;m++){const r=this.q2Info(m);if(r&&t[m]&&this.variables.slot[m]!==0)t[m]=Object.assign({},t[m],{color:r.color,filament:r.filament,vendor:r.vendor})}const r16=this.q2Info(16);if(r16&&t[16])t[16]=Object.assign({},t[16],{color:r16.color,filament:r16.filament,vendor:r16.vendor});return t}q2Info(i){const p=this.$store.state.printer.printer;let fi=null;if(i===16){fi=(((p.multi_color_controller||{}).extra)||{}).filament_info}else{const bx=(p.box_extras||{}).boxes||[];fi=((bx[Math.floor(i/4)]||{}).filament_info||[])[i%4]}if(!fi||!fi.filament_str)return null;const c=String((fi.color_rgb_str||[])[0]||"").replace("#","");return{filament:fi.filament_str,vendor:fi.vendor_str||"",color:c?"#"+c.toUpperCase():"#00000000"}}q2NewFw(){const bx=(this.$store.state.printer.printer.box_extras||{}).boxes;return!!(bx&&bx[0]&&bx[0].filament_info)}q2Canon(v){const k=String(v||"").toLowerCase().replace(/[^a-z0-9]/g,"");return{bambulab:"Bambu",bambu:"Bambu",qidi:"QIDI",generic:"Generic",hatchbox:"HATCHBOX",overture:"Overture",polymaker:"Polymaker"}[k]||v}q2Db(){return this.q2NewFw()?(this.$store.state.printer.q2FilaDB||__Q2_FALLBACK__):null}q2LoadDb(){const st=this.$store.state,pr=st.printer;if(pr.q2FilaDB||window.__q2DbLoading)return;window.__q2DbLoading=1;let nz="0.4";try{const d=parseFloat(pr.printer.configfile.settings.extruder.nozzle_diameter);[0.2,0.4,0.6,0.8].forEach(x=>{Math.abs(d-x)<.01&&(nz=x.toFixed(1))})}catch(e){}const base=(st.config&&st.config.apiUrl)||"";fetch(base+"/server/files/config/__Q2_LINK__/filament-"+nz+".json",{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject("HTTP "+r.status)).then(j=>{const db={};for(const k in j){const e=j[k]||{},v=this.q2Canon(e.filament_vendor||k.split(" ")[0]),n=k.indexOf((e.filament_vendor||"")+" ")===0?k.slice((e.filament_vendor||"").length+1):(k.indexOf(v+" ")===0?k.slice(v.length+1):k);(db[v]=db[v]||[]).push(n)}Object.keys(db).length&&this.$set(pr,"q2FilaDB",db)}).catch(e=>console.warn("[q2fix] firmware filament database unavailable, using fallback catalogue:",e)).finally(()=>{window.__q2DbLoading=0})}q2Protected(){const r=this.q2Info(this.selectIndex);if(!r)return!1;const db=this.q2Db();if(!db)return!1;const list=db[this.q2Canon(r.vendor)];return!(list&&list.indexOf(r.filament)>=0)}q2Edit(o){const i=this.selectIndex;if(!this.q2NewFw())return!1;if(i>16)return!0;const r=this.q2Info(i);if(!r)return!1;if(this.q2Protected())return!0;const db=this.q2Db();let v=o.vendor!=null?o.vendor:r.vendor,f=o.filament!=null?o.filament:r.filament;const cv=this.q2Canon(v);if(o.vendor!=null&&db&&db[cv]&&db[cv].indexOf(f)<0){const base=String(f).split(/[ -]/)[0];f=db[cv].find(n=>n.split(/[ -]/)[0]===base)||db[cv][0]}let c=String(o.color!=null?o.color:r.color||"").replace("#","").toUpperCase().slice(0,6);/^[0-9A-F]{6}$/.test(c)||(c=String(r.color||"").replace("#","").toUpperCase().slice(0,6));/^[0-9A-F]{6}$/.test(c)||(c="FAFAFA");I.printerGcodeScript(`UPDATE_FILAMENT_INFORMATION SLOT=${i} COLOR='${c}' VENDOR='${cv}' FILAMENT='${f}'`);return!0}
"""

DIALOG_MEMBERS = r"""
q2Info(i){const p=this.$store.state.printer.printer;let fi=null;if(i===16){fi=(((p.multi_color_controller||{}).extra)||{}).filament_info}else{const bx=(p.box_extras||{}).boxes||[];fi=((bx[Math.floor(i/4)]||{}).filament_info||[])[i%4]}if(!fi||!fi.filament_str)return null;const c=String((fi.color_rgb_str||[])[0]||"").replace("#","");return{filament:fi.filament_str,vendor:fi.vendor_str||"",color:c?"#"+c.toUpperCase():"#00000000"}}q2Canon(v){const k=String(v||"").toLowerCase().replace(/[^a-z0-9]/g,"");return{bambulab:"Bambu",bambu:"Bambu",qidi:"QIDI",generic:"Generic",hatchbox:"HATCHBOX",overture:"Overture",polymaker:"Polymaker"}[k]||v}q2FilaIndex(r){const m=__Q2_FILAMAP__;const v=this.q2Canon(r.vendor),n=String(r.filament||"").toLowerCase();if(m[v+"|"+n])return m[v+"|"+n];const s=n.indexOf(" ")>0?n.slice(n.indexOf(" ")+1):n;return m[v+"|"+s]||0}
"""

_B = "this.$store.state.printer.printer.box_extras.b_endstop_state"
_MCC_B = "((this.$store.state.printer.printer.multi_color_controller||{}).box||{}).b_endstop_state"
_B_FB = f"({_B}!==void 0?{_B}:{_MCC_B})"
_E = "this.$store.state.printer.printer.box_extras.e_endstop_state"
_MCC_E = "((this.$store.state.printer.printer.multi_color_controller||{}).box||{}).e_endstop_state"
_E_FB = f"({_E}!==void 0?{_E}:{_MCC_E})"

EDITS = [
    # 1. Le getter items d'origine du panneau devient q2RawItems.
    ("get items(){var i,a,o,l,c,u,d,p,h;const t=[],s=new Array(16).fill(!1);",
     "get q2RawItems(){var i,a,o,l,c,u,d,p,h;const t=[],s=new Array(16).fill(!1);", 1),
    # 2. Membres du fix + chargement de la base firmware a la creation.
    ("created(){this.$store.state.printer.officiallFilasList?",
     "__PANEL_MEMBERS__created(){this.q2LoadDb();this.$store.state.printer.officiallFilasList?", 1),
    # 3. Liste des fournisseurs depuis la base (protege = fournisseur courant seul).
    ("get vendorItems(){",
     "get vendorItems(){const qd=this.q2Db();if(qd)return this.q2Protected()?[this.q2Info(this.selectIndex).vendor]:Object.keys(qd);", 1),
    # 4. Liste des filaments filtree par fournisseur (protege = filament courant seul).
    ("get filamentItems(){",
     "get filamentItems(){const qd=this.q2Db();if(qd){if(this.q2Protected())return[this.q2Info(this.selectIndex).filament];const cv=this.q2Canon((this.q2Info(this.selectIndex)||{}).vendor);return qd[cv]||qd.QIDI||[]}", 1),
    # 5-7. Les trois setters passent par q2Edit (ecriture unique, protegee).
    ("set selectedVendor(t){", "set selectedVendor(t){if(t&&this.q2Edit({vendor:t}))return;", 1),
    ("set selectedFilament(t){", "set selectedFilament(t){if(t&&this.q2Edit({filament:t}))return;", 1),
    ("set selectedColor(t){", "set selectedColor(t){if(t&&this.q2Edit({color:t}))return;", 1),
    # 8. Commandes d'action au dialecte actuel.
    ('const n=["E_BOX","E_LOAD","E_UNLOAD"];I.printerGcodeScript(`${n[t-1]} slot=${s}`)',
     'const n=["EJECT_FILAMENT_CONTROL","LOAD_FILAMENT_CONTROL","UNLOAD_FILAMENT_CONTROL"];I.printerGcodeScript(`${n[t-1]} SLOT=${s}`)', 1),
    # 9. RFID au dialecte actuel.
    ("RFID_READ SLOT=slot${t}", "READ_RFID SLOT=${t}", 1),
    # 10. buttonStatus : b_endstop avec repli multi_color_controller.box (x2).
    (f"{_B}===0&&this.variables.lastLoadSlot",
     f"{_B_FB}===0&&this.variables.lastLoadSlot", 2),
    # 11. isOperating : l'etat d'operation du MCC verrouille le panneau.
    ("get isOperating(){const t=this.$store.state.printer.printer.box_extras;return!(!t||!t.box_button_state)",
     "get isOperating(){const t=this.$store.state.printer.printer.box_extras,qm=(this.$store.state.printer.printer.multi_color_controller||{}).state;if(qm&&qm!==\"idle\")return!0;return!(!t||!t.box_button_state)", 1),
    # 12. Fusion des deltas partiels de multi_color_controller dans le store.
    ("t[s]!==e.payload[s]&&$.set(r.printer[e.key],s,e.payload[s])",
     "t[s]!==e.payload[s]&&$.set(r.printer[e.key],s,e.key===\"multi_color_controller\"&&t[s]!==null&&e.payload[s]!==null&&typeof t[s]===\"object\"&&typeof e.payload[s]===\"object\"&&!Array.isArray(t[s])&&!Array.isArray(e.payload[s])?Object.assign({},t[s],e.payload[s]):e.payload[s])", 1),
    # 13. Dialogue d'impression : helpers resolus avant isOkPrinter.
    ("get isOkPrinter(){", "__DIALOG_MEMBERS__get isOkPrinter(){", 1),
    # 14. Dialogue : endstops avec repli MCC.box (semantique stock conservee).
    (f"{_E}===1?{_B}===0?", f"{_E_FB}===1?{_B_FB}===0?", 1),
    # 15. Dialogue : items batis depuis les identites resolues.
    ("get items(){const t=[];return this.variables.slot.forEach((s,n)=>{var i;if(s!==0&&Math.floor(n/4)<this.boxCount){const a=Math.floor(n/4+1)+String.fromCharCode(n%4+65),o=(i=this.officialFilasListDictData)==null?void 0:i.colordict,l=o?o[this.variables.colorSlot[n]]:\"#000000\",c=\"fila\"+this.variables.filamentSlot[n];t[n]={label:a,color:l,filaIndex:c}}})",
     "get items(){const t=[];return this.variables.slot.forEach((s,n)=>{if(s!==0&&Math.floor(n/4)<this.boxCount){const a=Math.floor(n/4+1)+String.fromCharCode(n%4+65),r=this.q2Info(n),f=r?this.q2FilaIndex(r):0;t[n]={label:a,color:r?r.color:\"#000000\",filaIndex:\"fila\"+(f||this.variables.filamentSlot[n])}}})", 1),
]

def main():
    if len(sys.argv) != 3:
        print("usage: qidi_q2_fluidd_fix.py <stock index-DlFvHGAh.js> <output.js>"); return 2
    src = open(sys.argv[1], 'rb').read()
    digest = hashlib.sha256(src).hexdigest()
    if digest != STOCK_SHA256:
        print(f"REFUS: SHA-256 {digest} != stock attendu {STOCK_SHA256}")
        print("Ce patcheur ne s'applique qu'au bundle stock exact (Q2 01.01.03.01+, Fluidd v1.30.5).")
        return 1
    js = src.decode('utf-8')
    members = (PANEL_MEMBERS
               .replace("__Q2_FALLBACK__", json.dumps(FALLBACK_DB, separators=(",", ":"), ensure_ascii=False))
               .replace("__Q2_LINK__", DB_LINK))
    dialog = DIALOG_MEMBERS.replace("__Q2_FILAMAP__", json.dumps(FILA_MAP, separators=(",", ":"), ensure_ascii=False))
    for anchor, repl, expected in EDITS:
        found = js.count(anchor)
        if found != expected:
            print(f"REFUS: ancre trouvee {found}x (attendu {expected}) : {anchor[:70]!r}")
            return 1
        js = js.replace(anchor, repl.replace("__PANEL_MEMBERS__", members).replace("__DIALOG_MEMBERS__", dialog))
    js = STAMP + js
    open(sys.argv[2], 'w', encoding='utf-8').write(js)
    print(f"OK: bundle patche ecrit ({len(js)} octets, stamp __qidiQ2Fix 1.0.0)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
