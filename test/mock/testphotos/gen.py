import numpy, Image

for n in xrange(30):
    a = numpy.random.rand(30,30,3) * 255
    im_out = Image.fromarray(a.astype('uint8')).convert('RGBA')
    im_out.save('out%000d.jpg' % n)
