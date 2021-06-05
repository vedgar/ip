import subprocess, pathlib, re, runpy, sys, operator, contextlib, io, \
        difflib, time, webbrowser, argparse, tempfile, os, filecmp

t00 = time.perf_counter()
službeni = pathlib.Path('out_test.txt')
argv = argparse.ArgumentParser()
argv.add_argument('--replace', action='store_true')
argv = argv.parse_args()
izlaz = io.StringIO()
datoteke = sorted((datoteka for datoteka in pathlib.Path().glob('*/*.py')
    if re.match('\d\d_', datoteka.stem)), key=operator.attrgetter('stem'))

for datoteka in datoteke:
    t0 = time.perf_counter()
    print(datoteka.stem.center(78, '#'), flush=True, file=izlaz)
    rezultat = subprocess.run([sys.executable, datoteka],
                capture_output=True, check=True, text=True, input='2\n')
    print(rezultat.stdout, end='', file=izlaz)
    print(format(time.perf_counter() - t0, '.3f'), datoteka)
print(f'Ukupno {time.perf_counter()-t00:.3f}s')

if argv.replace: službeni.write_text(izlaz.getvalue())
else:
    fromlines = službeni.read_text().splitlines()
    tolines = izlaz.getvalue().splitlines()
    if fromlines == tolines: print('Nema razlike.')
    else:
        diff = difflib.HtmlDiff(wrapcolumn=79)
        diff = diff.make_file(fromlines, tolines, context=True)
        with tempfile.NamedTemporaryFile(
                mode='w', prefix='_vepar_', delete=False) as tmp:
            print(diff, file=tmp)
        webbrowser.open(tmp.name, 2)
        time.sleep(6)
        pathlib.Path(tmp.name).unlink()
