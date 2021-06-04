import subprocess, pathlib, re, runpy, sys, operator

datoteke = sorted((datoteka for datoteka in pathlib.Path().glob('*/*.py')
    if re.match('\d\d_', datoteka.stem)), key=operator.attrgetter('stem'))

for datoteka in datoteke:
    print(datoteka.stem.center(78, '#'))
    subprocess.run([sys.executable, datoteka], check=True)
