from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()


def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db


# Geners Main Table and sub Tables
class Geners(db.Model):
    __tablename__ = 'geners'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

# Show Assocciation Table
class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    date = db.Column(db.DateTime)
    artist = db.relationship('Artist', back_populates='shows')
    venue = db.relationship('Venue', back_populates='shows')


class VenueGeners(db.Model):
    __tablename__ = "venuegeners"
    venue_id = db.Column(db.Integer,
                         db.ForeignKey('venue.id'),
                         primary_key=True)
    name = db.Column(db.String(), primary_key=True)


class ArtistGeners(db.Model):
    __tablename__ = "artistgeners"
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('artist.id'),
                          primary_key=True)
    name = db.Column(db.String(), primary_key=True)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    geners = db.relationship('VenueGeners',
                             backref='venue',
                             lazy=True,
                             cascade="all, delete, delete-orphan")
    shows = db.relationship('Shows',
                            back_populates='venue',
                            cascade="all, delete, delete-orphan")


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    geners = db.relationship('ArtistGeners',
                            backref='artist',
                            lazy=True,
                            cascade="all, delete, delete-orphan")
    shows = db.relationship('Shows',
                            back_populates='artist',
                            cascade="all, delete, delete-orphan")
