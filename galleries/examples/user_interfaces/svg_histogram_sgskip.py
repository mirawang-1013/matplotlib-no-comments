





from io import BytesIO

import json

import xml.etree.ElementTree as ET



import matplotlib.pyplot as plt

import numpy as np



plt.rcParams['svg.fonttype'] = 'none'



                                                                             

                             

ET.register_namespace("", "http://www.w3.org/2000/svg")



                                         

np.random.seed(19680801)



                                            

plt.figure()

r = np.random.randn(100)

r1 = r + 1

labels = ['Rabbits', 'Frogs']

H = plt.hist([r, r1], label=labels)

containers = H[-1]

leg = plt.legend(frameon=False)

plt.title("From a web browser, click on the legend\n"

          "marker to toggle the corresponding histogram.")





                                             



hist_patches = {}

for ic, c in enumerate(containers):

    hist_patches[f'hist_{ic}'] = []

    for il, element in enumerate(c):

        element.set_gid(f'hist_{ic}_patch_{il}')

        hist_patches[f'hist_{ic}'].append(f'hist_{ic}_patch_{il}')



                                

for i, t in enumerate(leg.get_patches()):

    t.set_gid(f'leg_patch_{i}')



                              

for i, t in enumerate(leg.get_texts()):

    t.set_gid(f'leg_text_{i}')



                                 

f = BytesIO()

plt.savefig(f, format="svg")



                                    

tree, xmlid = ET.XMLID(f.getvalue())





                           



                                      

for i, t in enumerate(leg.get_patches()):

    el = xmlid[f'leg_patch_{i}']

    el.set('cursor', 'pointer')

    el.set('onclick', "toggle_hist(this)")



                                     

for i, t in enumerate(leg.get_texts()):

    el = xmlid[f'leg_text_{i}']

    el.set('cursor', 'pointer')

    el.set('onclick', "toggle_hist(this)")



                                                    

                                                                    

                                                                        

                                                                       

                       



script = """
<script type="text/ecmascript">
<![CDATA[
var container = %s

function toggle(oid, attribute, values) {
    /* Toggle the style attribute of an object between two values.

    Parameters
    ----------
    oid : str
      Object identifier.
    attribute : str
      Name of style attribute.
    values : [on state, off state]
      The two values that are switched between.
    */
    var obj = document.getElementById(oid);
    var a = obj.style[attribute];

    a = (a == values[0] || a == "") ? values[1] : values[0];
    obj.style[attribute] = a;
    }

function toggle_hist(obj) {

    var num = obj.id.slice(-1);

    toggle('leg_patch_' + num, 'opacity', [1, 0.3]);
    toggle('leg_text_' + num, 'opacity', [1, 0.5]);

    var names = container['hist_'+num]

    for (var i=0; i < names.length; i++) {
        toggle(names[i], 'opacity', [1, 0])
    };
    }
]]>
</script>
""" % json.dumps(hist_patches)



                         

css = tree.find('.//{http://www.w3.org/2000/svg}style')

css.text = css.text + "g {-webkit-transition:opacity 0.4s ease-out;" +
    "-moz-transition:opacity 0.4s ease-out;}"



                                     

tree.insert(0, ET.XML(script))



ET.ElementTree(tree).write("svg_histogram.svg")

