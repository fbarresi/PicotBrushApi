import io

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, send_file, url_for, make_response)
from flask_cors import CORS
import PIL
from PIL import Image, ImageOps

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

default_width = 800
default_height = 480


def convert_picture(rawBytes, **kwargs):

   print("converting picture with following arguments:", kwargs)

   width = kwargs.get('width', default_width)
   height = kwargs.get('height', default_height)
   rotation = kwargs.get('rotation', 0)
   preserveRatio = kwargs.get('preserveAspectRatio') is not None

   try:
      if(width <= 0):
         width = 1
   except:
      width = default_width
   try:
      if(height <= 0):
         height = 1
   except:
      height = default_height

   # Create a pallette with the 7 colors supported by the panel
   pal_image = Image.new("P", (1,1))
   pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249)

   image = Image.open(rawBytes)

   size = (width, height)
   
   # Resize and check if we need to rotate the image
   if rotation > 0:
      image_temp = image.rotate(rotation, expand=True)
   else:
      image_temp = image

   if preserveRatio :
      # resize and keep the ratio
      image_temp = ImageOps.contain(image_temp, size)
      #print(image_temp.size)
      
      # fill the new picture into a box to ensure final size
      x, y = image_temp.size
      box = Image.new('RGB', (width, height), (255, 255, 255, 1))
      box.paste(image_temp, (int((width - x) / 2), int((height - y) / 2)))
   else :
      box = image_temp.resize(size)

   # Convert the soruce image to the 7 colors, dithering if needed
   image_7color = box.convert("RGB").quantize(palette=pal_image) 

   return image_7color



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
   #print('Request for index page received')
   return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
   if 'file' not in request.files:
      print('No file part')
      redirect(url_for('index'))

   form_args = request.form.to_dict()
   for key in form_args:
      try:
         form_args[key] = int(form_args[key])
      except:
         pass
   
   file = request.files['file']

   if file and allowed_file(file.filename):

      rawBytes = io.BytesIO(file.read())
      image_7color = convert_picture(rawBytes, **form_args)
      buf_7color = bytearray(image_7color.tobytes('raw'))

      # PIL does not support 4 bit color, so pack the 4 bits of color
      # into a single byte to transfer to the panel
      buf = [0x00] * int(width * height / 2)
      idx = 0
      for i in range(0, len(buf_7color), 2):
         buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
         idx += 1

      buffer = io.BytesIO(bytes(buf))
      
      return send_file(buffer, download_name=file.filename+'.bin', mimetype='application/octet-stream')
   
   else:
      return redirect(url_for('index'))

@app.route('/paint', methods=['POST'])
def paint():

   if 'file' not in request.files:
      print('No file part')
      redirect(url_for('index'))

   form_args = request.form.to_dict()
   for key in form_args:
      try:
         form_args[key] = int(form_args[key])
      except:
         pass

   file = request.files['file']

   if file and allowed_file(file.filename):

      rawBytes = io.BytesIO(file.read())
      image_7color = convert_picture(rawBytes, **form_args)

      img_io = io.BytesIO()
      image_7color.convert('RGB').save(img_io, 'JPEG', quality=70)
      img_io.seek(0)

      return send_file(img_io, mimetype='image/jpeg')
   
   else:
      return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
