



import os



import matplotlib

import matplotlib.ft2font as ft



font = ft.FT2Font(

                                         

    os.path.join(matplotlib.get_data_path(),

                 'fonts/ttf/DejaVuSans-Oblique.ttf'))



print('Num instances:  ', font.num_named_instances)                                     

print('Num faces:      ', font.num_faces)                                     

print('Num glyphs:     ', font.num_glyphs)                                         

print('Family name:    ', font.family_name)                            

print('Style name:     ', font.style_name)                            

print('PS name:        ', font.postscript_name)                           

print('Num fixed:      ', font.num_fixed_sizes)                                  



                                                   

if font.scalable:

                                                           

    print('Bbox:               ', font.bbox)

                                            

    print('EM:                 ', font.units_per_EM)

                                

    print('Ascender:           ', font.ascender)

                                 

    print('Descender:          ', font.descender)

                              

    print('Height:             ', font.height)

                                       

    print('Max adv width:      ', font.max_advance_width)

                              

    print('Max adv height:     ', font.max_advance_height)

                                            

    print('Underline pos:      ', font.underline_position)

                                         

    print('Underline thickness:', font.underline_thickness)



for flag in ft.StyleFlags:

    name = flag.name.replace('_', ' ').title() + ':'

    print(f"{name:17}", flag in font.style_flags)



for flag in ft.FaceFlags:

    name = flag.name.replace('_', ' ').title() + ':'

    print(f"{name:17}", flag in font.face_flags)

