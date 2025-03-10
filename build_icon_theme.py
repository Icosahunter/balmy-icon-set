from pathlib import Path
import tomllib
import subprocess
import shlex
import shutil
from tqdm import tqdm
import itertools

sizes = [48, 64, 128, 256]
sections = ['apps', 'categories', 'devices', 'mimetypes', 'places']
distdir = Path('./dist')
themedir = distdir / 'balmy-icons'

def create_theme_file():
    print('Generating index.theme file...')
    subdirs = list(itertools.chain.from_iterable([[f'{section}/{size}' for size in sizes] for section in sections]))
    subdirs.extend([f'{section}/scalable' for section in sections])
    subdirs = ','.join(subdirs)
    theme_file_text = f"[Icon Theme]\nName=Balmy Icons\nComment=Simple CC0 pastel icons\nDirectories={subdirs}\n\n"
    for section in sections:
        for size in sizes:
            theme_file_text += f"[{section}/{size}]\nSize={size}\nContext={section.capitalize()}\nType=Fixed\n\n"
    for section in sections:
        theme_file_text += f"[{section}/scalable]\nSize=512\nContext={section.capitalize()}\nType=Scalable\n\n"
    themedir.mkdir(exist_ok=True, parents=True)
    with open(themedir / 'index.theme', '+w') as f:
        f.write(theme_file_text)
    print('Done.')

def export_icons():
    print('Exporting icons...')
    icon_mapping = None
    with open('fd-name-mapping.toml', 'rb') as f:
        icon_mapping = tomllib.load(f)
    for section in tqdm(sections):
        for size in tqdm(sizes):
            for destfile, srcfile in icon_mapping[section].items():
                filename = (themedir / section / str(size) / destfile).with_suffix('.png')
                filename.parent.mkdir(exist_ok=True, parents=True)
                cmd = f"inkscape --export-width={size} --export-filename={filename} --export-area-drawing {srcfile}"
                subprocess.run(shlex.split(cmd))
    for section in tqdm(sections):
        for destfile, srcfile in icon_mapping[section].items():
            filename = (themedir / section / 'scalable' / destfile).with_suffix('.svg')
            filename.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(srcfile, filename)
    print('Done.')

def compress_theme():
    print('Compressing theme...')
    cmd = f"tar czf --directory={distdir} balmy-icons-theme.tar.gz {themedir}"
    subprocess.run(shlex.split(cmd))
    print('Done.')

if __name__ == '__main__':
    shutil.rmtree(distdir)
    create_theme_file()
    export_icons()
    compress_theme()
