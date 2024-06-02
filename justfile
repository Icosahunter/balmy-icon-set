export size='512':
    #!/usr/bin/env bash
    for f in `find -name '*.svg'`
    do
        inkscape --export-width={{size}} --export-type=png --export-area-drawing $f
    done
    mkdir export
    for f in `find -name '*.png'`
    do
        n=`basename $f`
        mv $f 'export/'$n 
    done

clean:
    rm -r 'export'
