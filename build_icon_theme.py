from pathlib import Path
import tomllib
import subprocess
import shlex
import shutil
from tqdm import tqdm
import itertools
import sys

sizes = [48, 64, 128, 256, 'scalable']
sections = ['apps', 'categories', 'devices', 'mimetypes', 'places']
contexts = {
    'apps': 'Applications',
    'categories': 'Categories',
    'devices': 'Devices',
    'mimetypes': 'MimeTypes',
    'places': 'Places'
}
srcdir = Path('src')
distdir = Path('dist')
themedir = distdir / 'balmy-icons'

def create_theme_file():
    print('Generating index.theme file...')

    subdirs = list(itertools.chain.from_iterable([[f'{section}/{size}' for size in sizes] for section in sections]))
    subdirs.extend([f'{section}/scalable' for section in sections])
    subdirs = ','.join(subdirs)

    theme_file_text = f"[Icon Theme]\nName=Balmy Icons\nComment=Simple CC0 pastel icons\nDirectories={subdirs}\n\n"

    for section in sections:
        for size in sizes:
            theme_file_text += f"[{section}/{size}]\nSize={size}\nContext={contexts[section]}\nType=Fixed\n\n"

    for section in sections:
        theme_file_text += f"[{section}/scalable]\nSize=512\nContext={contexts[section]}\nType=Scalable\n\n"

    themedir.mkdir(exist_ok=True, parents=True)
    with open(themedir / 'index.theme', '+w') as f:
        f.write(theme_file_text)

    print('Done.')

def export_icons():
    print('Exporting icons...')

    icon_mapping = None
    with open('fd-name-mapping.toml', 'rb') as f:
        icon_mapping = tomllib.load(f)

    files = itertools.chain.from_iterable(((((section, size, file, src)
        for file, src in icon_mapping[section].items())
        for size in sizes)
        for section in sections))
    files = list(itertools.chain.from_iterable(files))

    for section, size, file, src in tqdm(files):
        export_icon(srcdir/src, f'{themedir}/{section}/{size}/{file}', size)

    print('Done.')

def export_icon(src, dest, size):
    dest = Path(dest)
    if size == 'scalable':
        filename = dest.with_suffix('.svg')
        filename.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy(src, filename)
    else:
        filename = dest.with_suffix('.png')
        filename.parent.mkdir(exist_ok=True, parents=True)
        cmd = f"inkscape --export-width={size} --export-filename={filename} --export-area-drawing {src}"
        subprocess.run(shlex.split(cmd))

def compress_theme():
    print('Compressing theme...')
    cmd = f"tar czf --directory={distdir} balmy-icons-theme.tar.gz {themedir}"
    subprocess.run(shlex.split(cmd))
    print('Done.')

if __name__ == '__main__':
    shutil.rmtree(distdir, ignore_errors=True)
    action = 'build-dist'
    if len(sys.argv) > 1:
        action = sys.argv[1]

    if action == 'build-index':
        create_theme_file()
    elif action == 'build-dist':
        create_theme_file()
        export_icons()
        compress_theme()
    if action == 'build':
        create_theme_file()
        export_icons()
    if action == 'compress':
        compress_theme()
