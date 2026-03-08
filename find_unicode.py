import sys
lines = open(r'c:\Users\Rahmathullah\Desktop\recon\recon1\files\bughunter.py', encoding='utf-8').readlines()
for i, line in enumerate(lines, 1):
    for ch in line:
        if ord(ch) > 127:
            try:
                ch.encode('cp1252')
            except UnicodeEncodeError:
                print(f'Line {i}: U+{ord(ch):04X} -> {line.strip()[:80]}')
                break
print("SCAN DONE")
