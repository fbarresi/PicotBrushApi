import io
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
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

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


async def read_form(request: Request):
   form = await request.form()
   form_args = {}
   file = None
   for key, value in form.items():
      if key == 'file':
         file = value
         continue
      try:
         form_args[key] = int(value)
      except (TypeError, ValueError):
         form_args[key] = value
   return file, form_args


def redirect_to_index():
   # 303 so the browser follows with GET after a POST
   return RedirectResponse('/', status_code=303)


@app.get('/', include_in_schema=False)
def index():
   return FileResponse(BASE_DIR / 'templates' / 'index.html')

@app.post('/convert')
async def convert(request: Request):
   file, form_args = await read_form(request)

   if file is not None and hasattr(file, 'read') and allowed_file(file.filename):

      rawBytes = io.BytesIO(await file.read())
      image_7color = convert_picture(rawBytes, **form_args)
      buf_7color = bytearray(image_7color.tobytes('raw'))

      width = form_args.get('width', default_width)
      height = form_args.get('height', default_height)

      # PIL does not support 4 bit color, so pack the 4 bits of color
      # into a single byte to transfer to the panel
      buf = [0x00] * int(width * height / 2)
      idx = 0
      for i in range(0, len(buf_7color), 2):
         buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
         idx += 1

      filename = file.filename.replace('"', '')
      return Response(bytes(buf), media_type='application/octet-stream',
                      headers={'Content-Disposition': f'attachment; filename="{filename}.bin"'})

   else:
      return redirect_to_index()

@app.post('/paint')
async def paint(request: Request):
   file, form_args = await read_form(request)

   if file is not None and hasattr(file, 'read') and allowed_file(file.filename):

      rawBytes = io.BytesIO(await file.read())
      image_7color = convert_picture(rawBytes, **form_args)

      img_io = io.BytesIO()
      image_7color.convert('RGB').save(img_io, 'JPEG', quality=70)

      return Response(img_io.getvalue(), media_type='image/jpeg')

   else:
      return redirect_to_index()


if __name__ == '__main__':
   import uvicorn
   uvicorn.run(app, host='127.0.0.1', port=5000)
