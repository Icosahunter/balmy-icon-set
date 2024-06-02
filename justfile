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
    echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' >> 'demo.svg'
    echo '<svg width="512" height="512" version="1.1" id="svg1" xmlns="http://www.w3.org/2000/svg">' >> 'demo.svg'
    i=0
    for f in `find -wholename './src/*.svg'`
    do
        y=$((128*(i/4)))
        x=$((128*(i%4)))
        i=$((i+1))
        echo "<image width=\"128\" height=\"128\" x=\"${x}\" y=\"${y}\" href=\"${f}\"/>" >> 'demo.svg'
    done
    echo '</svg>' >> 'demo.svg'
    inkscape --export-width=512 --export-type=png --export-area-drawing 'demo.svg'
    rm 'demo.svg'

clean:
    rm -r 'export'
