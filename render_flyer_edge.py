import subprocess, os, shutil
from PIL import Image

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(edge_path):
    edge_path = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

abs_html = os.path.abspath('business_flyer_telugu.html')
out_png = os.path.abspath(os.path.join('static', 'images', 'business_flyer_7jyotirlinga_hd.png'))

cmd = f'"{edge_path}" --headless=new --screenshot="{out_png}" --window-size=1200,2200 "file:///{abs_html}"'
print("Running command:", cmd)
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Returncode:", res.returncode)

if os.path.exists(out_png):
    im = Image.open(out_png)
    print(f"Generated {out_png}: {im.size}, {os.path.getsize(out_png) / 1024:.1f} KB")
    
    # Also copy to artifacts dir
    art_path = r"C:\Users\Krishna\.gemini\antigravity\brain\07429a57-70c2-42e3-acfc-b368133aefc7\business_flyer_7jyotirlinga_hd.png"
    shutil.copyfile(out_png, art_path)
    print(f"Copied to artifact dir: {art_path}")
else:
    print("Failed to generate out_png")
