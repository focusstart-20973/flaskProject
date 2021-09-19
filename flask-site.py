import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, render_template, flash, request, redirect, session
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from PIL import Image, ImageColor
from numpy import asarray

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ks275aXCZseRQ#@$XF'
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

class MyForm(FlaskForm):
    image = FileField('image')

@app.route('/', methods=['GET', 'POST'])
def uploads():
    form = MyForm()
    if form.validate_on_submit():
        filename = images.save(form.image.data)
        pixels = asarray(Image.open('uploads/images/' + filename))
        black = 0
        white = 0
        x = 0
        y = 0
        while x < pixels.shape[0]:
            while y < pixels.shape[1]:
                if list(pixels[x][y]) == [0, 0, 0]:
                    black = black+1
                elif list(pixels[x][y]) == [255, 255, 255]:
                    white = white+1
                y = y + 1
            x = x + 1
            y = 0
        print(black, white)
        session['filename'] = filename
        session['difference'] = black - white
        return redirect('/your-image')
    return render_template('uploads.html', form=form)

@app.route('/your-image', methods=['GET', 'POST'])
def yourimage():
    if request.method == "POST":
        hexcode = request.form['HEX']
        rgb = list(ImageColor.getcolor(hexcode, "RGB"))
        pixels = asarray(Image.open('uploads/images/' + session['filename']))
        identical_pixels = 0
        x = 0
        y = 0
        while x < pixels.shape[0]:
            while y < pixels.shape[1]:
                if list(pixels[x][y]) == rgb:
                    identical_pixels = identical_pixels + 1
                y = y + 1
            x = x + 1
            y = 0
        return f'There are {identical_pixels} of {hexcode} pixels in the uploaded image.'
    else:
        difference = session['difference']
        if difference > 0:
            flash('There are more black pixels on the uploaded image then white.')
        elif difference < 0:
            flash('There are more white pixels on the uploaded image then black.')
        else:
            flash('The amount of black and white pixels on the uploaded image is the same.')
        return render_template('image.html')

if __name__==('__main__'):
    app.run(debug=True)