





from io import BytesIO

import xml.etree.ElementTree as ET



import matplotlib.pyplot as plt



ET.register_namespace("", "http://www.w3.org/2000/svg")



fig, ax = plt.subplots()



                                                    

rect1 = plt.Rectangle((10, -20), 10, 5, fc='blue')

rect2 = plt.Rectangle((-20, 15), 10, 5, fc='green')



shapes = [rect1, rect2]

labels = ['This is a blue rectangle.', 'This is a green rectangle']



for i, (item, label) in enumerate(zip(shapes, labels)):

    patch = ax.add_patch(item)

    annotate = ax.annotate(labels[i], xy=item.get_xy(), xytext=(0, 0),

                           textcoords='offset points', color='w', ha='center',

                           fontsize=8, bbox=dict(boxstyle='round, pad=.5',

                                                 fc=(.1, .1, .1, .92),

                                                 ec=(1., 1., 1.), lw=1,

                                                 zorder=1))



    ax.add_patch(patch)

    patch.set_gid(f'mypatch_{i:03d}')

    annotate.set_gid(f'mytooltip_{i:03d}')



                                       

ax.set_xlim(-30, 30)

ax.set_ylim(-30, 30)

ax.set_aspect('equal')



f = BytesIO()

plt.savefig(f, format="svg")



                           



                                    

tree, xmlid = ET.XMLID(f.getvalue())

tree.set('onload', 'init(event)')



for i in shapes:

                                

    index = shapes.index(i)

                       

    tooltip = xmlid[f'mytooltip_{index:03d}']

    tooltip.set('visibility', 'hidden')

                                                             

    mypatch = xmlid[f'mypatch_{index:03d}']

    mypatch.set('onmouseover', "ShowTooltip(this)")

    mypatch.set('onmouseout', "HideTooltip(this)")



                                                                        

script = """
    <script type="text/ecmascript">
    <![CDATA[

    function init(event) {
        if ( window.svgDocument == null ) {
            svgDocument = event.target.ownerDocument;
            }
        }

    function ShowTooltip(obj) {
        var cur = obj.id.split("_")[1];
        var tip = svgDocument.getElementById('mytooltip_' + cur);
        tip.setAttribute('visibility', "visible")
        }

    function HideTooltip(obj) {
        var cur = obj.id.split("_")[1];
        var tip = svgDocument.getElementById('mytooltip_' + cur);
        tip.setAttribute('visibility', "hidden")
        }

    ]]>
    </script>
    """



                                                       

tree.insert(0, ET.XML(script))

ET.ElementTree(tree).write('svg_tooltip.svg')

