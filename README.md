# PNG2ASS

## Installation

Install pypng: `pip3 install pypng`

## How to use it?

```
python3 png2ass.py picture.png --start-time 0:00:10.00 --with-ass-header --text-prefix "{\fad(500,500)}" > nekopoi.ass
```

## Options

`--layer`: the layer of this picture (0 by default)<br>
`--start-time`: the beginning time of the displaying png (for eg 0:00:10.00)<br>
`--end-time`: the ending time of the displaying png (for eg 0:00:20.00 - 1hour by default)<br>
`--pos`: the position of the png, by default "0,0"<br>
`--text-prefix`<br>
`--text-suffix`<br>
`--with-ass-header`
