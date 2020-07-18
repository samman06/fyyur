#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import os
from sqlalchemy.sql import func
from models import db_setup, Venue, Shows, Artist, VenueGeners, ArtistGeners
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime  #

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venue
#  ----------------------------------------------------------------


@app.route('/venues/')
def venues():
    venues_cities = db.session.query(Venue.city, Venue.state).order_by(
        Venue.state).distinct().all()
    data = []
    for city, state in venues_cities:
        sub_dict = {}
        sub_dict["city"] = city
        sub_dict["state"] = state
        shows_subquery = db.session.query(
            Shows.venue_id,
            func.count('*').label('num_upcoming_shows')).filter(
                Shows.date >= func.current_date()).group_by(
                    Shows.venue_id).subquery()
        venues_data = db.session.query(
            Venue.id, Venue.name, Venue.city, Venue.state,
            shows_subquery.c.num_upcoming_shows).outerjoin(
                shows_subquery, Venue.id == shows_subquery.c.venue_id).filter(
                    Venue.city == city,
                    Venue.state == state).order_by(Venue.state,
                                                   Venue.city).all()
        venue_list = [venue for venue in venues_data]
        sub_dict["venues"] = venue_list
        data.append(dict(sub_dict))
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/create/', methods=['GET', 'POST'])
def create_venue_submission():
    form = VenueForm()
    if request.method == 'POST':
        if form.validate():
            try:
                name = request.form['name']
                city = request.form['city']
                state = request.form['state']
                address = request.form['address']
                phone = request.form['phone']
                genres = request.form.getlist('genres')
                facebook_link = request.form['facebook_link']
                image_link = ''
                if request.files:
                    image = request.files["image_link"]
                    image_link = request.form[
                        'name'] + '_Image.' + request.files[
                            "image_link"].filename.rsplit(".", 1)[1]
                    image.save(
                        os.path.join(app.config["IMAGE_UPLOADS"], image_link))

                venue = Venue(name=name,
                              city=city,
                              state=state,
                              address=address,
                              phone=phone,
                              facebook_link=facebook_link,
                              image_link=image_link)
                for genre in genres:
                    venuegeners = VenueGeners(name=genre)
                    venuegeners.venue = venue
                db.session.add(venue)
                db.session.commit()
                flash('Venue ' + request.form['name'] +
                      ' was successfully Created!')
            except:
                db.session.rollback()
                flash('An error occurred. Venue ' + request.form['name'] +
                      '  could not be listed.')
            finally:
                db.session.close()
            return render_template('pages/home.html')
        else:
            flash('Check Validators')

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/delete/<venue_id>/')
def delete_venue(venue_id):
    try:
        venue_to_be_deleted = Venue.query.get(venue_id)
        db.session.delete(venue_to_be_deleted)
        db.session.commit()
        flash('Venue has been deleted.')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/')
def show_venue(venue_id):
    data = {}
    venue = Venue.query.get(venue_id)
    if venue is None:
        flash('There is no venue with enterd ID, Try with another ID')
        return redirect(url_for('index'))
    data["id"] = venue.id
    data["name"] = venue.name
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["facebook_link"] = venue.facebook_link
    data["image_link"] = venue.image_link
    geners = [gener for gener in Venue.query.get(venue_id).geners]
    data["genres"] = geners

    past_shows = db.session.query(
        Artist.name.label('artist_name'), Artist.id.label('artist_id'),
        Artist.image_link.label('artist_image_link'),
        Shows.date.label('start_time')).join(Artist).filter(
            Shows.date < func.current_date(), Shows.venue_id == venue_id)
    upcoming_shows = db.session.query(
        Artist.name.label('artist_name'), Artist.id.label('artist_id'),
        Artist.image_link.label('artist_image_link'),
        Shows.date.label('start_time')).join(Artist).filter(
            Shows.date >= func.current_date(), Shows.venue_id == venue_id)
    data["past_shows"] = list(past_shows.all())
    data["past_shows_count"] = past_shows.count()
    data["upcoming_shows"] = list(upcoming_shows.all())
    data["upcoming_shows_count"] = upcoming_shows.count()
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/<int:venue_id>/edit/', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_obj = Venue.query.get(venue_id)
    if venue_obj is None:
        flash('There is no venue with enterd ID, Try with another ID')
        return redirect(url_for('index'))

    venue = {}
    venue["id"] = venue_obj.id
    venue["name"] = venue_obj.name
    form.name.data = venue_obj.name
    geners = [g.name for g in Venue.query.get(venue_id).geners]
    form.genres.data = geners
    venue["genres"] = geners
    venue["address"] = venue_obj.address
    form.address.data = venue_obj.address
    venue["city"] = venue_obj.city
    form.city.data = venue_obj.city
    venue["state"] = venue_obj.state
    form.state.data = venue_obj.state
    venue["phone"] = venue_obj.phone
    form.phone.data = venue_obj.phone
    venue["facebook_link"] = venue_obj.facebook_link
    form.facebook_link.data = venue_obj.facebook_link
    venue["image_link"] = venue_obj.image_link
    form.image_link.data = venue_obj.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit/', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        old_venue_name = venue.name
        old_venue_img = venue.image_link
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.address = request.form['address']
        venue.facebook_link = request.form['facebook_link']
        added_geners = [g.name for g in venue.geners]

        new_geners = request.form.getlist('genres')

        if set(new_geners).difference(added_geners) is not None:
            for new_genere in set(new_geners).difference(added_geners):
                venuegener = VenueGeners(name=new_genere)
                venuegener.venue = venue

        if set(added_geners).difference(new_geners) is not None:
            for genere_to_be_deleted in set(added_geners).difference(
                    new_geners):
                db.session.query(VenueGeners).filter(
                    VenueGeners.name == genere_to_be_deleted,
                    VenueGeners.vanue_id == venue.id).delete()

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] +
              '  could not be updated.')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form["search_term"]
    shows_subquery = db.session.query(
        Shows.venue_id,
        func.count('*').label('num_upcoming_shows')).filter(
            Shows.date >= func.current_date()).group_by(
                Shows.venue_id).subquery()
    venues_data = db.session.query(
        Venue.name, Venue.id, shows_subquery.c.num_upcoming_shows).filter(
            Venue.name.ilike('%' + search_term + '%')).outerjoin(
                shows_subquery, Venue.id == shows_subquery.c.venue_id)
    response = {}
    response["count"] = venues_data.count()
    venue_list = [venue for venue in venues_data]
    response["data"] = venue_list
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/<int:artist_id>/')
def show_artist(artist_id):
    data = {}
    artist = Artist.query.get(artist_id)
    if artist is None:
        flash('There is no artist with enterd ID, Try with another ID')
        return redirect(url_for('index'))

    data["id"] = artist.id
    data["name"] = artist.name
    data["city"] = artist.city
    data["state"] = artist.state
    data["phone"] = artist.phone
    data["facebook_link"] = artist.facebook_link
    data["image_link"] = artist.image_link
    geners = [gener for gener in Artist.query.get(artist_id).geners]
    data["genres"] = geners
    print(geners)
    past_shows = db.session.query(
        Venue.name.label('venue_name'), Venue.id.label('venue_id'),
        Venue.image_link.label('venue_image_link'),
        Shows.date.label('start_time')).join(Venue).filter(
            Shows.date < func.current_date(), Shows.artist_id == artist_id)
    upcoming_shows = db.session.query(
        Venue.name.label('venue_name'), Venue.id.label('venue_id'),
        Venue.image_link.label('venue_image_link'),
        Shows.date.label('start_time')).join(Venue).filter(
            Shows.date >= func.current_date(), Shows.artist_id == artist_id)
    data["past_shows"] = list(past_shows.all())
    data["past_shows_count"] = past_shows.count()
    data["upcoming_shows"] = list(upcoming_shows.all())
    data["upcoming_shows_count"] = upcoming_shows.count()
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/create/', methods=['GET', 'POST'])
def create_artist():
    form = ArtistForm()
    if request.method == 'POST':
        if form.validate():
            try:
                name = request.form['name']
                city = request.form['city']
                state = request.form['state']
                phone = request.form['phone']
                genres = request.form.getlist('genres')
                facebook_link = request.form['facebook_link']
                image_link = ''
                if request.files:
                    image = request.files["image_link"]
                    image_link = request.form[
                        'name'] + '_Image.' + request.files[
                            "image_link"].filename.rsplit(".", 1)[1]
                    image.save(
                        os.path.join(app.config["IMAGE_UPLOADS"], image_link))
                artist = Artist(name=name,
                                city=city,
                                state=state,
                                phone=phone,
                                facebook_link=facebook_link,
                                image_link=image_link)
                for genre in genres:
                    print(genre,1)
                    print(artist,2)
                    artistgener = ArtistGeners(name=genre)
                    artistgener.artist = artist
                db.session.add(artist)
                db.session.commit()
                flash('Artist ' + request.form['name'] +
                      ' was successfully listed!')
            except:
                flash('An error occurred. Artist ' + request.form['name'] +
                      '  could not be listed.')
                db.session.rollback()
            finally:
                db.session.close()

            return render_template('pages/home.html')
        else:
            flash('Check Validators')
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/delete/<artist_id>/')
def delete_artist(artist_id):
    try:
        artist_to_be_deleted = Artist.query.get(artist_id)
        db.session.delete(artist_to_be_deleted)
        db.session.commit()
        flash('Artist has been deleted.')
    except:
        db.session.rollback()
        flash('An error occurred. Artist could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))



@app.route('/artists/<int:artist_id>/edit/', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_obj = Artist.query.get(artist_id)
    if artist_obj is None:
        flash('There is no artist with enterd ID, Try with another ID')
        return redirect(url_for('index'))
    artist = {}
    artist["id"] = artist_obj.id
    artist["name"] = artist_obj.name
    form.name.data = artist_obj.name
    geners =[g.name for g in Artist.query.get(artist_id).geners]
    form.genres.data = geners
    artist["genres"] = geners
    artist["city"] = artist_obj.city
    form.city.data = artist_obj.city
    artist["state"] = artist_obj.state
    form.state.data = artist_obj.state
    artist["phone"] = artist_obj.phone
    form.phone.data = artist_obj.phone
    artist["facebook_link"] = artist_obj.facebook_link
    form.facebook_link.data = artist_obj.facebook_link
    artist["image_link"] = artist_obj.image_link
    form.image_link.data = artist_obj.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit/', methods=['POST'])
def edit_artist_submission(artist_id):
    try:

        artist = Artist.query.get(artist_id)
        old_artist_name = artist.name
        old_artist_img = artist.image_link
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']
        if request.files:
            imgfile = old_artist_img
            image = request.files["image_link"]
            image_link = request.form['name'] + '_Image.' + request.files[
                "image_link"].filename.rsplit(".", 1)[1]
            artist.image_link = image_link
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_link))
        added_geners = []
        for g in artist.geners:
            added_geners.append(g.name)
        new_geners = request.form.getlist('genres')
        for new_genere in set(new_geners).difference(added_geners):
            artistgener = ArtistGeners(name=new_genere)
            artistgener.artist = artist
        for genere_to_be_deleted in set(added_geners).difference(new_geners):
            db.session.query(ArtistGeners).filter(
                ArtistGeners.name == genere_to_be_deleted,
                ArtistGeners.artist_id == artist.id).delete()
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] +
              '  could not be updated.')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form["search_term"]
    shows_subquery = db.session.query(
        Shows.artist_id,
        func.count('*').label('num_upcoming_shows')).filter(
            Shows.date >= func.current_date()).group_by(
                Shows.artist_id).subquery()
    artists_data = db.session.query(
        Artist.name, Artist.id, shows_subquery.c.num_upcoming_shows).filter(
            Artist.name.ilike('%' + search_term + '%')).outerjoin(
                shows_subquery, Artist.id == shows_subquery.c.artist_id)
    response = {}
    artists_list = []
    response["count"] = artists_data.count()
    for artist in artists_data.all():
        artists_list.append(artist)
    response["data"] = artists_list
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/shows')
def shows():
    data = db.session.query(Shows.date.label('start_time'), Shows.venue_id,
                            Venue.name.label('venue_name'), Shows.artist_id,
                            Artist.name.label('artist_name'),
                            Artist.image_link.label('artist_image_link')).join(
                                Venue, Artist).all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create/')
def create_shows(errors={}):
    artists = db.session.query(Artist.id, Artist.name).all()
    venues = db.session.query(Venue.id, Venue.name).all()
    form = ShowForm()
    return render_template('forms/new_show.html',
                           form=form,
                           artists=artists,
                           venues=venues,
                           errors=errors)


@app.route('/shows/create/', methods=['POST'])
def create_show_submission():
    try:
        venue_id = request.form['venue_id']
        artist_id = request.form['artist_id']
        artist = Artist.query.get(artist_id)
        venue = Venue.query.get(venue_id)
        if not venue or not artist:
            errors = {
                artist: "invalid artist",
                venue: "invalid venue",
            }
            return redirect(url_for('create_shows', errors=errors))

        date = request.form['start_time']
        show = Shows(venue_id=venue_id, artist_id=artist_id, date=date)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
