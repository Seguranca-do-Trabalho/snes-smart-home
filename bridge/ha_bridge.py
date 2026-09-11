#!/usr/bin/env python3
from __future__ import annotations
import json, os, socket, struct, time, urllib.request
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread

HA_URL=os.getenv('HA_URL','http://127.0.0.1:8123').rstrip('/')
HA_TOKEN=os.getenv('HA_TOKEN','')
HTTP_PORT=int(os.getenv('BRIDGE_HTTP_PORT','8790'))
TCP_PORT=int(os.getenv('BRIDGE_TCP_PORT','8791'))
POLL_SECONDS=float(os.getenv('POLL_SECONDS','2'))
SUPPORTED={'light':1,'switch':2,'cover':3,'lock':4,'fan':5,'climate':6,'sensor':7,'binary_sensor':8,'media_player':9}
@dataclass
class Entity:
    domain:int; state_code:int; features:int; entity_id:str; name:str; state:str; value:str; numeric_value_x100:int|None
class Store:
    def __init__(self): self.lock=Lock(); self.entities=[]; self.last_error=''; self.last_update=0.0
    def replace(self,e):
        with self.lock:self.entities=e[:24];self.last_update=time.time();self.last_error=''
    def error(self,m):
        with self.lock:self.last_error=m
    def snapshot(self):
        with self.lock:return list(self.entities)
    def meta(self):
        with self.lock:return {'count':len(self.entities),'last_update':self.last_update,'error':self.last_error}
store=Store()

SERVICE_MAP={
    "light": {"on":"turn_on", "off":"turn_off"},
    "switch": {"on":"turn_on", "off":"turn_off"},
    "fan": {"on":"turn_on", "off":"turn_off"},
    "cover": {"open":"open_cover", "close":"close_cover"},
    "lock": {"lock":"lock", "unlock":"unlock"},
}

def ha_call_service(entity_id: str, action: str) -> object:
    domain=entity_id.split('.',1)[0]
    if domain not in SERVICE_MAP or action not in SERVICE_MAP[domain]:
        raise ValueError(f"unsupported action: {domain}/{action}")
    service=SERVICE_MAP[domain][action]
    payload=json.dumps({"entity_id":entity_id}).encode()
    req=urllib.request.Request(f"{HA_URL}/api/services/{domain}/{service}",data=payload,method="POST")
    req.add_header('Authorization',f'Bearer {HA_TOKEN}')
    req.add_header('Content-Type','application/json')
    with urllib.request.urlopen(req,timeout=5) as response:
        body=response.read().decode('utf-8')
        return json.loads(body) if body else None
def ha_request(path):
    r=urllib.request.Request(HA_URL+path);r.add_header('Authorization',f'Bearer {HA_TOKEN}');r.add_header('Content-Type','application/json')
    with urllib.request.urlopen(r,timeout=5) as x:return json.loads(x.read().decode())
def feature_bits(domain,attrs):
    b=0
    if domain in {'light','switch','fan','lock','cover'}:b|=1
    if domain=='light' and (attrs.get('brightness') is not None or attrs.get('supported_color_modes')):b|=2
    if domain=='cover':b|=4
    if domain=='lock':b|=8
    if domain in {'sensor','climate'}:b|=32
    if domain in {'cover','light','fan','climate'}:b|=64
    return b
def state_code(domain,state):
    s=state.lower()
    if s in {'on','open','unlocked','playing','home','detected'}:return 1
    if s in {'off','closed','locked','idle','away','clear','undetected'}:return 0
    return 2
def numeric_value(domain,state,attrs):
    candidate=attrs.get('brightness') if domain=='light' and attrs.get('brightness') is not None else state
    try:return max(0,min(65534,int(round(float(candidate)*100))))
    except (TypeError,ValueError):return None
def discover():
    while True:
        try:
            raw=ha_request('/api/states');out=[]
            for item in raw:
                eid=str(item.get('entity_id','')); domain=eid.split('.',1)[0] if '.' in eid else ''
                if domain not in SUPPORTED:continue
                attrs=item.get('attributes') or {}; state=str(item.get('state','unknown')); name=str(attrs.get('friendly_name') or eid)
                out.append(Entity(SUPPORTED[domain],state_code(domain,state),feature_bits(domain,attrs),eid,name,state,str(attrs.get('unit_of_measurement') or ''),numeric_value(domain,state,attrs)))
            out.sort(key=lambda e:(e.domain,e.name.lower(),e.entity_id));store.replace(out)
        except Exception as exc:store.error(str(exc))
        time.sleep(POLL_SECONDS)
def crc16(data):
    crc=0xffff
    for b in data:
        crc^=b
        for _ in range(8):crc=(crc>>1)^0xA001 if crc&1 else crc>>1
    return crc
def pack_snapshot(es):
    out=bytearray(b'SH'+bytes([1,len(es)]))
    for e in es:
        name=e.name.encode('ascii','replace')[:28]; n=0xffff if e.numeric_value_x100 is None else e.numeric_value_x100
        out+=bytes([e.domain,e.state_code,e.features,len(name)])+struct.pack('<H',n)+name
    out+=struct.pack('<H',crc16(out));return bytes(out)
class Handler(BaseHTTPRequestHandler):
    def send_json(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False,indent=2).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/health':return self.send_json(200,store.meta())
        if self.path=='/entities':return self.send_json(200,[asdict(e) for e in store.snapshot()])
        if self.path=='/snapshot.bin':
            data=pack_snapshot(store.snapshot());self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        self.send_json(404,{'error':'not found'})

    def do_POST(self):
        if self.path != '/command':
            return self.send_json(404,{'error':'not found'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            req=json.loads(self.rfile.read(length).decode('utf-8'))
            entity_id=str(req.get('entity_id',''))
            action=str(req.get('action',''))
            result=ha_call_service(entity_id,action)
            self.send_json(200,{'ok':True,'entity_id':entity_id,'action':action,'result':result})
        except Exception as exc:
            self.send_json(400,{'ok':False,'error':str(exc)})
    def log_message(self,format,*args):print('[http]',format%args)
def tcp_server():
    with socket.create_server(('0.0.0.0',TCP_PORT)) as s:
        print('[tcp]',TCP_PORT)
        while True:
            c,a=s.accept();print('[tcp] client',a)
            with c:
                try:
                    while True:
                        d=pack_snapshot(store.snapshot());c.sendall(struct.pack('<H',len(d))+d);time.sleep(POLL_SECONDS)
                except (BrokenPipeError,ConnectionResetError):pass
def main():
    if not HA_TOKEN:print('WARNING: set HA_TOKEN')
    Thread(target=discover,daemon=True).start();Thread(target=tcp_server,daemon=True).start();ThreadingHTTPServer(('0.0.0.0',HTTP_PORT),Handler).serve_forever()
if __name__=='__main__':main()
