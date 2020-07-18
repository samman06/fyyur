from datetime import datetime
import enum
from enum import Enum
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, FileField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Regexp, Optional


class State(enum.Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'


class Geners(enum.Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    HipHop = 'Hip-Hop '
    HeavyMetal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    MusicalTheatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    RB = 'R&B'
    Reggae = 'Reggae'
    RocknRoll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'


geners_name = [(gener.value, gener.value) for gener in Geners]
states_name = [(state.value, state.value) for state in State]
phone_regex = "^[0-9]{3}[-]?[0-9]{3}[-]?[0-9]{4}?"


def check_allowed_image(form, field):
    if field.raw_data is not None:
        if field.raw_data[0] is not None:
            filename = field.raw_data[0].filename
    if filename is not None:
        if not "." in filename:
            raise ValidationError('select file')
    if filename is not None:
        ext = filename.rsplit(".", 1)[1]
        ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
        if ext.upper() in ALLOWED_IMAGE_EXTENSIONS:
            return True
        else:
            raise ValidationError('Not Allowed File Extension')
    else:
        return True


class ShowForm(Form):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField('start_time',
                               validators=[DataRequired()],
                               default=datetime.today())


class VenueForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=states_name)
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone', validators=[Regexp(phone_regex)])
    genres = SelectMultipleField('genres', choices=geners_name)
    facebook_link = StringField('facebook_link', validators=[URL()])
    image_link = FileField('image_link', validators=[check_allowed_image])


class ArtistForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=states_name)
    phone = StringField('phone', validators=[Regexp(phone_regex)])
    genres = SelectMultipleField('genres',
                                 validators=[DataRequired()],
                                 choices=geners_name)
    facebook_link = StringField('facebook_link', validators=[URL()])
    image_link = FileField('image_link', validators=[check_allowed_image])
