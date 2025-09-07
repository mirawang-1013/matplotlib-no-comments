from pathlib import Path

import shutil



import numpy as np

import pytest

from pytest import approx



from matplotlib import _image

from matplotlib.testing.compare import compare_images

from matplotlib.testing.decorators import _image_directories

from matplotlib.testing.exceptions import ImageComparisonFailure





                                          

@pytest.mark.parametrize(

    'im1, im2, tol, expect_rms',

    [

                                                                           

                                                                              

                           

        ('basn3p02.png', 'basn3p02-minorchange.png', 10, None),

                                     

        ('basn3p02.png', 'basn3p02-minorchange.png', 0, 6.50646),

                                                                        

        ('basn3p02.png', 'basn3p02-1px-offset.png', 0, 90.15611),

                                                                               

               

        ('basn3p02.png', 'basn3p02-half-1px-offset.png', 0, 63.75),

                                                              

                                                                              

                    

                                                                         

                                                                             

                                                                            

                                                                   

                                                                               

                    

        ('basn3p02.png', 'basn3p02-scrambled.png', 0, 172.63582),

                                                               

                                                                               

                               

                                                                              

                                   

        ('all127.png', 'all128.png', 0, 1),

                                          

        ('all128.png', 'all127.png', 0, 1),

    ])

def test_image_comparison_expect_rms(im1, im2, tol, expect_rms, tmp_path,

                                     monkeypatch):

    

                                                                       

                             

    monkeypatch.chdir(tmp_path)

    baseline_dir, result_dir = map(Path, _image_directories(lambda: "dummy"))

                                                                    

                                                            

    result_im2 = result_dir / im1

    shutil.copyfile(baseline_dir / im2, result_im2)

    results = compare_images(

        baseline_dir / im1, result_im2, tol=tol, in_decorator=True)



    if expect_rms is None:

        assert results is None

    else:

        assert results is not None

        assert results['rms'] == approx(expect_rms, abs=1e-4)





def test_invalid_input():

    img = np.zeros((16, 16, 4), dtype=np.uint8)



    with pytest.raises(ImageComparisonFailure,

                       match='must be 3-dimensional, but is 2-dimensional'):

        _image.calculate_rms_and_diff(img[:, :, 0], img)

    with pytest.raises(ImageComparisonFailure,

                       match='must be 3-dimensional, but is 5-dimensional'):

        _image.calculate_rms_and_diff(img, img[:, :, :, np.newaxis, np.newaxis])

    with pytest.raises(ImageComparisonFailure,

                       match='must be RGB or RGBA but has depth 2'):

        _image.calculate_rms_and_diff(img[:, :, :2], img)



    with pytest.raises(ImageComparisonFailure,

                       match=r'expected size: \(16, 16, 4\) actual size \(8, 16, 4\)'):

        _image.calculate_rms_and_diff(img, img[:8, :, :])

    with pytest.raises(ImageComparisonFailure,

                       match=r'expected size: \(16, 16, 4\) actual size \(16, 6, 4\)'):

        _image.calculate_rms_and_diff(img, img[:, :6, :])

    with pytest.raises(ImageComparisonFailure,

                       match=r'expected size: \(16, 16, 4\) actual size \(16, 16, 3\)'):

        _image.calculate_rms_and_diff(img, img[:, :, :3])

