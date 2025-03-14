export size='512':
    #!/usr/bin/env bash
    for f in `find -wholename './src/*.svg'`
    do
        inkscape --export-width={{size}} --export-type=png --export-area-drawing $f
    done
    mkdir export
    for f in `find -name '*.png'`
    do
        n=`basename $f`
        mv $f 'export/'$n
    done

demo:
    #!/usr/bin/env bash
    s=512
    c=8
    echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' >> 'demo.svg'
    echo "<svg width=\"${s}\" height=\"${s}\" version=\"1.1\" id=\"svg1\" xmlns=\"http://www.w3.org/2000/svg\">" >> 'demo.svg'
    i=0
    for f in `find -wholename './src/*.svg'`
    do
        w=$((s/c))
        y=$((w*(i/c)))
        x=$((w*(i%c)))
        i=$((i+1))
        echo "<image width=\"${w}\" height=\"${w}\" x=\"${x}\" y=\"${y}\" href=\"${f}\"/>" >> 'demo.svg'
    done
    echo '</svg>' >> 'demo.svg'
    inkscape --export-width=512 --export-type=png --export-area-drawing 'demo.svg'
    rm 'demo.svg'

build:
    python3 build_icon_theme.py

clean:
    rm -r 'export'
