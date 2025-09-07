



import os

from pathlib import Path

import unicodedata



import matplotlib.pyplot as plt



import matplotlib.font_manager as fm

from matplotlib.ft2font import FT2Font





def print_glyphs(path):

    

    if path is None:

        path = fm.findfont(fm.FontProperties())                     



    font = FT2Font(path)



    charmap = font.get_charmap()

    max_indices_len = len(str(max(charmap.values())))



    print("The font face contains the following glyphs:")

    for char_code, glyph_index in charmap.items():

        char = chr(char_code)

        name = unicodedata.name(

                char,

                f"{char_code:#x} ({font.get_glyph_name(glyph_index)})")

        print(f"{glyph_index:>{max_indices_len}} {char} {name}")





def draw_font_table(path):

    

    if path is None:

        path = fm.findfont(fm.FontProperties())                     



    font = FT2Font(path)

                                                                              

                                                                               

                        

                                                                           

                                                                         

                                                                              

                                                                          

                                                                         

                                       

                                                                             

                                                

    codes = font.get_charmap().items()



    labelc = [f"{i:X}" for i in range(16)]

    labelr = [f"{i:02X}" for i in range(0, 16*16, 16)]

    chars = [["" for c in range(16)] for r in range(16)]



    for char_code, glyph_index in codes:

        if char_code >= 256:

            continue

        row, col = divmod(char_code, 16)

        chars[row][col] = chr(char_code)



    fig, ax = plt.subplots(figsize=(8, 4))

    ax.set_title(os.path.basename(path))

    ax.set_axis_off()



    table = ax.table(

        cellText=chars,

        rowLabels=labelr,

        colLabels=labelc,

        rowColours=["palegreen"] * 16,

        colColours=["palegreen"] * 16,

        cellColours=[[".95" for c in range(16)] for r in range(16)],

        cellLoc='center',

        loc='upper left',

    )

    for key, cell in table.get_celld().items():

        row, col = key

        if row > 0 and col > -1:                                               

            cell.set_text_props(font=Path(path))



    fig.tight_layout()

    plt.show()





if __name__ == "__main__":

    from argparse import ArgumentParser



    parser = ArgumentParser(description="Display a font table.")

    parser.add_argument("path", nargs="?", help="Path to the font file.")

    parser.add_argument("--print-all", action="store_true",

                        help="Additionally, print all chars to stdout.")

    args = parser.parse_args()



    if args.print_all:

        print_glyphs(args.path)

    draw_font_table(args.path)

