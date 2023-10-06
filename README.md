# hotstar_add_silencer

## Motivation

Got tired of listening to the irritating adds on hotstar between the cricket match so wanted to create a script which can silence when the add is playing.

## Code

Take a screenshot and use a simple classifier to classify whether it is an add or a match and based on that set the volume. For the model, yolov8-small model is used.

## Steps to run

Install the requirements using `pip install -r requirements.txt` and then run `python3 screen_cls.py`.
