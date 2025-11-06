# PicotBrushApi
tribute to Jean-Claude Picot into an open source project based on rpi pico you are going to love

[![Azure Web App - picotbrush](https://github.com/fbarresi/PicotBrushApi/actions/workflows/main_picotbrush.yml/badge.svg)](https://github.com/fbarresi/PicotBrushApi/actions/workflows/main_picotbrush.yml)

This project offers a web api to transform picture in the way to they can be rendered by an E-Ink display.<br>
Like Waveshare E-Ink-Color-Display, 7.3 inch, 800x480, Spectra 6:

<img width="256" height="180" alt="image" src="https://github.com/user-attachments/assets/83f8e591-f7ef-42aa-a778-a6503a391901" />

## How to use

The simplest way to use it is over the web - visit [picotbrush](https://picotbrush.azurewebsites.net/) and give it a try!

Just upload your picture, press `paint` for a preview or `convert` to download the picture in binary format.<br>
You may include a rotation if you need it.

<img width="546" height="547" alt="image" src="https://github.com/user-attachments/assets/c3ff2ef1-df95-4414-83a2-950b6ffa8ede" />

This will transform your picture from:


<img width="400" height="241" alt="image" src="https://github.com/user-attachments/assets/4c170257-abfb-4453-bd0f-45d002e9c1db" />

into this:

<img width="400" height="241" alt="image" src="https://github.com/user-attachments/assets/11a71174-a3b6-4731-90d0-339a9ba87c3f" />


## Contribute?

Yes, please!

Don't forget to ⭐ this project and feel free to open an issue/discussion/pull-request.

I would be happy to receive donations, this will help to cover hosting costs.

## Quick dev guide

- check out this repository and open it locally
- install a python virtual environment `python3 -m venv .venv`
- activate it with `.venv\Scripts\activate`
- install all requirements with `pip install -r .\requirements.txt`
- start the application with `flask run`
- visit [http://127.0.0.1:5000](http://127.0.0.1:5000) and have fun!

## Credits

The implementation was partially overtaken and adapted from [waveshare](https://github.com/waveshareteam/Pico_ePaper_Code) examples.

Example pictures: “Les Voiles le Soir,” Jean-Claude Picot - [Park West Gallery](https://www.parkwestgallery.com/blog/jean-claude-picot-remembered/)
