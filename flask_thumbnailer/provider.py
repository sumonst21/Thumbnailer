from flask import abort, Flask, request, make_response

import requests

from PIL import Image
from StringIO import StringIO


app = Flask(__name__)
app.debug=True

@app.route('/resize/')
def resize():
    # 1. Get the image or raise 404
    url = request.args.get('url', None)
    width = int(request.args.get('width', 800))
    height = int(request.args.get('height', 600))
    opts = [x.strip() for x in request.args.get('opts', 'crop').split(',')]
    if url:
        response = requests.get(url)
        image = Image.open(StringIO(response.content))
    else:
        abort(404)

    # 2. Resize the image
    version = scale_and_crop(image, width, height, opts)
    if not version:
        print "Not version"
        version = image

    # 3. Returns the image
    thumb = StringIO()
    version.save(thumb, 'PNG')
    response = make_response(thumb.getvalue())
    response.content_type = 'image/png'
    return response

def scale_and_crop(im, width, height, opts):
    """
    Scale and Crop.
    """
    
    x, y = [float(v) for v in im.size]

    if 'upscale' not in opts and x < width:
        # version would be bigger than original
        # no need to create this version, because "upscale" isn't defined.
        return False
    
    if width:
        xr = float(width)
    else:
        xr = float(x*height/y)
    if height:
        yr = float(height)
    else:
        yr = float(y*width/x)
    
    if 'crop' in opts:
        r = max(xr/x, yr/y)
    else:
        r = min(xr/x, yr/y)
    
    if r < 1.0 or (r > 1.0 and 'upscale' in opts):
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)
    
    if 'crop' in opts:
        x, y   = [float(v) for v in im.size]
        ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
        if ex or ey:
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))
    return im
    
scale_and_crop.valid_options = ('crop', 'upscale')


if __name__ == '__main__':
    app.run()
