"""Copy renders from out/ into the repo: full size -> wallpapers/, page size -> proposal/img/.
usage: python3 export.py shoji tsuki sakyu hon"""
import os, sys, shutil
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'out')
for name in sys.argv[1:]:
    for fmt, full, page in (('outer', (1398, 2034), (699, 1017)), ('inner', (2670, 1878), (1335, 939))):
        src = os.path.join(OUT, f'{name}_{fmt}.jpg')
        im = Image.open(src)
        assert im.size == full, (src, im.size)
        shutil.copyfile(src, os.path.join(REPO, 'wallpapers', f'r5-{name}_{fmt}_{full[0]}x{full[1]}.jpg'))
        im.convert('RGB').resize(page, Image.LANCZOS).save(os.path.join(REPO, 'proposal', 'img', f'r5-{name}_{fmt}.jpg'),
                                                           quality=84, subsampling=0, optimize=True, progressive=True)
    print('exported', name)
