from pathlib import Path
import tomllib
import subprocess
import shlex
import shutil
import os
from tqdm import tqdm
import itertools
import sys
import hashlib

sizes = [48, 64, 128, 256, 'scalable']
contexts = {
    'apps': 'Applications',
    'categories': 'Categories',
    'devices': 'Devices',
    'mimetypes': 'MimeTypes',
    'places': 'Places',
    'actions': 'Actions',
    'status': 'Status',
    'emotes': 'Emotes'
}
srcdir = Path('./src')
distdir = Path('./dist')
themedir = distdir / 'balmy-icons'

used_srcs = {}

def verify_mappings():
    print('Verifying filename mappings...')
    missing_filenames = []
    icon_mapping = None
    with open('fd-name-mapping.toml', 'rb') as f:
        icon_mapping = tomllib.load(f)
    for section in icon_mapping.values():
        for filename in section.values():
            if not Path(srcdir / filename).exists():
                missing_filenames.append(filename)
    if missing_filenames:
        print('ERROR: Some files in the file mappings config could not be found:')
        for file in missing_filenames:
            print(f'\t - {file}')
        return False
    print('Done.')
    return True

def create_theme_file():

    print('Generating index.theme file...')

    subdirs = list(itertools.chain.from_iterable([[f'{section}/{size}' for size in sizes] for section in contexts.keys()]))
    subdirs.extend([f'{section}/scalable' for section in contexts.keys()])
    subdirs = ','.join(subdirs)

    theme_file_text = f"[Icon Theme]\nName=Balmy Icons\nComment=Simple CC0 pastel icons\nDirectories={subdirs}\n\n"

    for section in contexts.keys():
        for size in sizes:
            theme_file_text += f"[{section}/{size}]\nSize={size}\nContext={contexts[section]}\nType=Fixed\n\n"

    for section in contexts.keys():
        theme_file_text += f"[{section}/scalable]\nSize=512\nContext={contexts[section]}\nType=Scalable\n\n"

    if (themedir/'index.theme').exists():
        (themedir/'index.theme').unlink()

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
        for section in contexts.keys()))
    files = list(itertools.chain.from_iterable(files))

    filenames = set([themedir/'index.theme'])

    for section, size, file, src in tqdm(files):
        dest = Path(f'{themedir}/{section}/{size}/{file}')
        if size == 'scalable':
            dest = dest.with_suffix('.svg')
        else:
            dest = dest.with_suffix('.png')
        if not (Path(dest).exists() and hash(f'{themedir}/{section}/scalable/{file}.svg') == hash(srcdir/src)):
            export_icon(srcdir/src, dest, size)
        filenames.add(dest)

    used_srcs.clear()

    for file in set(themedir.glob('**/*.*')) - filenames:
        Path(file).unlink()

    print('Done.')

def export_icon(src, dest, size):
    dest = Path(dest)
    if src in used_srcs and dest.parent == used_srcs[src].parent:
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.symlink_to(used_srcs[src].name)
    else:
        if size == 'scalable':
            dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(src, dest)
        else:
            dest.parent.mkdir(exist_ok=True, parents=True)
            cmd = f"inkscape --export-width={size} --export-filename={dest} --export-area-drawing {src}"
            subprocess.run(shlex.split(cmd))
        used_srcs[src] = dest

def compress_theme():
    print('Compressing theme...')
    os.chdir(themedir.parent)
    cmd = f"tar czf balmy-icons-theme.tar.gz {themedir.name}"
    subprocess.run(shlex.split(cmd))
    print('Done.')

def hash(file):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    if Path(file).exists():
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()
    else:
        return None

if __name__ == '__main__':
    action = 'build-dist'
    if len(sys.argv) > 1:
        action = sys.argv[1]
    if action == 'build-index' and verify_mappings():
        create_theme_file()
    elif action == 'build-dist' and verify_mappings():
        #shutil.rmtree(distdir, ignore_errors=True)
        create_theme_file()
        export_icons()
        compress_theme()
    if action == 'build' and verify_mappings():
        #shutil.rmtree(distdir, ignore_errors=True)
        create_theme_file()
        export_icons()
    if action == 'compress':
        compress_theme()
