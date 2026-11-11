import subprocess, os

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
abs_html = os.path.abspath('test_edge_telugu.html')
abs_out = os.path.abspath('test_edge_rendered.png')

cmd = f'"{edge_path}" --headless=new --screenshot="{abs_out}" --window-size=1000,500 "file:///{abs_html}"'
subprocess.run(cmd, shell=True)
print('Generated test_edge_rendered.png:', os.path.exists(abs_out))
