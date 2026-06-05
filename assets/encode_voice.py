import base64
with open('assets/amber_voice.wav', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
print(f'Length: {len(b64)} chars ({len(b64)//1024} KB)')
with open('assets/amber_b64.py', 'w') as out:
    out.write(f'AMBER_VOICE_B64 = "{b64}"\n')
print('Written to assets/amber_b64.py')
