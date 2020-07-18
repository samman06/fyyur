from flask import Flask, render_template, request, Response, flash, redirect, url_for

from model.models import Artist,ArtistGeners,Shows,Venue,VenueGeners
from app import db
print(db,333)
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #  using https://docs.sqlalchemy.org/en/13/orm/tutorial.html
  venues_cities = db.session.query(Venue.city, Venue.state).order_by(Venue.state).distinct().all()
  # print('-------------------------------------')
  # print(venues_cities)
  data=[]
  print('-------------------------------------')
  for city, state in venues_cities:
    sub_dict = {}
    sub_dict["city"] = city
    sub_dict["state"] = state
    venue_list = []
    shows_subquery = db.session.query(Shows.venue_id, func.count('*').label('num_upcoming_shows')).filter(Shows.date >= func.current_date()).group_by(Shows.venue_id).subquery()
    venues_data = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state,shows_subquery.c.num_upcoming_shows).outerjoin(shows_subquery, Venue.id==shows_subquery.c.venue_id).filter(Venue.city==city, Venue.state==state).order_by(Venue.state, Venue.city).all()
    for v in venues_data:
      venue_list.append(v)
    print(venue_list, '----------------')
    sub_dict["venues"] = venue_list
    data.append(dict(sub_dict))
    # print(data)
  # data=[   
  #   {
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # ]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form["search_term"]
  print(search_term)
  shows_subquery = db.session.query(Shows.venue_id, func.count('*').label('num_upcoming_shows')).filter(Shows.date >= func.current_date()).group_by(Shows.venue_id).subquery()
  venues_data = db.session.query(Venue.name, Venue.id,shows_subquery.c.num_upcoming_shows).filter(Venue.name.ilike('%'+search_term+'%')).outerjoin(shows_subquery, Venue.id==shows_subquery.c.venue_id)  
  response = {}
  venue_list = []
  response["count"] = venues_data.count()
  for venue in venues_data.all():
    venue_list.append(venue)
  response["data"] = venue_list
    

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
@app.route('/venues/<int:venue_id>/')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
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
  data["website"] = venue.website
  data["facebook_link"] = venue.facebook_link
  data["seeking_talent"] = venue.seeking_talent
  data["seeking_description"] = venue.seeking_description
  data["image_link"] = venue.image_link
  geners = []
  for g in Venue.query.get(venue_id).geners:
    geners.append(g.name)
  data["genres"] = geners
  
  past_shows = db.session.query(Artist.name.label('artist_name'), Artist.id.label('artist_id'), Artist.image_link.label('artist_image_link'),Shows.date.label('start_time')).join(Artist).filter(Shows.date < func.current_date(), Shows.venue_id == venue_id)
  upcoming_shows = db.session.query(Artist.name.label('artist_name'), Artist.id.label('artist_id'), Artist.image_link.label('artist_image_link'),Shows.date.label('start_time')).join(Artist).filter(Shows.date >= func.current_date(), Shows.venue_id == venue_id)
  data["past_shows"] = list(past_shows.all())
  data["past_shows_count"] = past_shows.count()
  data["upcoming_shows"] = list(upcoming_shows.all())
  data["upcoming_shows_count"] = upcoming_shows.count()

  print(data)
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
    
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = VenueForm()
  if request.method == 'POST':
    if form.validate():
      print('form ', request.form)
      try:
        # requestkeys = request.form.keys() 
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']

        image_link= ''

        # get file image and save it under image folder, and rename image file after name of venue
        if request.files:
          image = request.files["image_link"]
          image_link= request.form['name'] + '_Image.' + request.files["image_link"].filename.rsplit(".", 1)[1]
          image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_link))

        print(image_link + 'image_link')
        genres = request.form.getlist('genres')
        print('geners: ', genres)
        facebook_link = request.form['facebook_link']
        website = request.form['website']
        seeking_talent = False
        if 'seeking_talent' in request.form:
          if request.form['seeking_talent'] == 'y':
            seeking_talent = True
        print(seeking_talent)
        seeking_description = request.form['seeking_description']

        venue = Venue(name=name, city=city, state=state,address=address,phone=phone, facebook_link=facebook_link, image_link= image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
        for g in genres:
          venuegeners = VenueGeners(name=g)
          venuegeners.venue = venue
        # venue.geners = geners
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + '  could not be listed.')
      finally:
        db.session.close()

      return render_template('pages/home.html')
    else:
      flash('Check Validators')

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
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

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.id, Artist.name).all()
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form["search_term"]
  print(search_term)
  shows_subquery = db.session.query(Shows.artist_id, func.count('*').label('num_upcoming_shows')).filter(Shows.date >= func.current_date()).group_by(Shows.artist_id).subquery()
  artists_data =  db.session.query(Artist.name, Artist.id,shows_subquery.c.num_upcoming_shows).filter(Artist.name.ilike('%'+search_term+'%')).outerjoin(shows_subquery, Artist.id==shows_subquery.c.artist_id)  
  response = {}
  artists_list = []
  response["count"] = artists_data.count()
  for artist in artists_data.all():
    artists_list.append(artist)
  response["data"] = artists_list

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
@app.route('/artists/<int:artist_id>/')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  
  data = {}
  artist = Artist.query.get(artist_id)
  if artist is None:
    flash('There is no artist with enterd ID, Try with another ID')
    return redirect(url_for('index'))

  data["id"] = artist.id
  data["name"] = artist.name
  geners = []
  for g in Artist.query.get(artist_id).geners:
    geners.append(g.name)
  data["genres"] = geners
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website
  data["facebook_link"] = artist.facebook_link
  data["seeking_venue"] = artist.seeking_venue
  data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link
  
  past_shows = db.session.query(Venue.name.label('venue_name'), Venue.id.label('venue_id'), Venue.image_link.label('venue_image_link'),Shows.date.label('start_time')).join(Venue).filter(Shows.date < func.current_date(), Shows.artist_id == artist_id)
  upcoming_shows = db.session.query(Venue.name.label('venue_name'), Venue.id.label('venue_id'), Venue.image_link.label('venue_image_link'),Shows.date.label('start_time')).join(Venue).filter(Shows.date >= func.current_date(), Shows.artist_id == artist_id)
  data["past_shows"] = list(past_shows.all())
  data["past_shows_count"] = past_shows.count()
  data["upcoming_shows"] = list(upcoming_shows.all())
  data["upcoming_shows_count"] = upcoming_shows.count()

  
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_obj = Artist.query.get(artist_id)
  
  if artist_obj is None:
    flash('There is no artist with enterd ID, Try with another ID')
    return redirect(url_for('index'))
  
  geners = []
  artist={}
  artist["id"] = artist_obj.id
  artist["name"] = artist_obj.name
  form.name.data = artist_obj.name

  for g in Artist.query.get(artist_id).geners:
    geners.append(g.name)
  form.genres.data = geners
  
  artist["genres"] = geners
  artist["city"] = artist_obj.city
  form.city.data = artist_obj.city

  artist["state"] = artist_obj.state
  form.state.data = artist_obj.state

  artist["phone"] = artist_obj.phone
  form.phone.data = artist_obj.phone

  artist["website"] = artist_obj.website
  form.website.data = artist_obj.website

  artist["facebook_link"] = artist_obj.facebook_link
  form.facebook_link.data = artist_obj.facebook_link

  artist["seeking_venue"] = artist_obj.seeking_venue
  form.seeking_venue.data = artist_obj.seeking_venue

  artist["seeking_description"] = artist_obj.seeking_description
  form.seeking_description.data = artist_obj.seeking_description
  
  artist["image_link"] = artist_obj.image_link
  form.image_link.data = artist_obj.image_link

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:

    artist = Artist.query.get(artist_id)
    

    old_artist_name = artist.name
    old_artist_img = artist.image_link

    print(old_artist_name)
    print(old_artist_img)

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    
    # get file image and save it under image folder, and rename image file after name of venue
    if request.files:
      # remove old file
      imgfile = old_artist_img
      # if os.path.isfile(os.path.join(app.config["IMAGE_UPLOADS"], imgfile)):
      #   os.remove(imgfile)
      #   print('removed ------------------------------')
      # Add new file image
      image = request.files["image_link"]
      image_link = request.form['name'] + '_Image.' + request.files["image_link"].filename.rsplit(".", 1)[1]
      artist.image_link= image_link
      image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_link))

    artist.website = request.form['website']
    # print(request.form['seeking_venue'])

    artist.seeking_venue = False
    if 'seeking_venue' in request.form:
      if request.form['seeking_venue'] == 'y':
        artist.seeking_venue = True
    print(artist.seeking_venue)

    artist.seeking_description = request.form['seeking_description']

    # compare new genres list with added geners
    
    added_geners = []
    for g in artist.geners:
      added_geners.append(g.name)

    new_geners = request.form.getlist('genres')
    # print(added_geners)
    # print(new_geners)
    # print('---------------------------------------------------------------')
    
    for new_genere in set(new_geners).difference(added_geners):
      artistgener = ArtistGeners(name=new_genere)
      artistgener.artist = artist
      # print('---------------------------added ------------------------------')
      # print(new_genere)

    for genere_to_be_deleted in set(added_geners).difference(new_geners):
      # print(genere_to_be_deleted)
      db.session.query(ArtistGeners).filter(ArtistGeners.name == genere_to_be_deleted, ArtistGeners.artist_id == artist.id).delete()
    

    # for g in Artist.query.get(artist_id).geners:
    #   artistgener = ArtistGeners(name=g)
    #   artistgener.artist = artist
    #   print(g)
    # db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
     # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + '  could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_obj = Venue.query.get(venue_id)
  
  if venue_obj is None:
    flash('There is no venue with enterd ID, Try with another ID')
    return redirect(url_for('index'))
  
  geners = []
  venue={}
  venue["id"] = venue_obj.id
  venue["name"] = venue_obj.name
  form.name.data = venue_obj.name

  for g in Venue.query.get(venue_id).geners:
    geners.append(g.name)
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

  venue["website"] = venue_obj.website
  form.website.data = venue_obj.website

  venue["facebook_link"] = venue_obj.facebook_link
  form.facebook_link.data = venue_obj.facebook_link

  venue["seeking_talent"] = venue_obj.seeking_talent
  form.seeking_talent.data = venue_obj.seeking_talent

  venue["seeking_description"] = venue_obj.seeking_description
  form.seeking_description.data = venue_obj.seeking_description
  
  venue["image_link"] = venue_obj.image_link
  form.image_link.data = venue_obj.image_link


  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    

    old_venue_name = venue.name
    old_venue_img = venue.image_link
    print('-----------------------------------------------------------------------------')
    print(old_venue_name)
    print(old_venue_img)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address']

    venue.facebook_link = request.form['facebook_link']
    
    # get file image and save it under image folder, and rename image file after name of venue
    # if request.files:
    #   # remove old file
    #   print('herere')
    #   imgfile = old_venue_img
    #   print('999999999999999999999999999999999999 ' + imgfile)
    #   # if os.path.isfile(os.path.join(app.config["IMAGE_UPLOADS"], imgfile)):
    #   #   os.remove(imgfile)
    #   #   print('removed ------------------------------')
    #   # Add new file image
    #   image = request.files["image_link"]
    #   image_link = request.form['name'] + '_Image.' + request.files["image_link"].filename.rsplit(".", 1)[1]
    #   venue.image_link= image_link
    #   image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_link))

    venue.website = request.form['website']
    # print(request.form['seeking_venue'])

    venue.seeking_talent = False
    if 'seeking_talent' in request.form:
      if request.form['seeking_talent'] == 'y':
        venue.seeking_talent = True
    print(venue.seeking_talent)

    venue.seeking_description = request.form['seeking_description']

    # compare new genres list with added geners
    
    added_geners = []
    for g in venue.geners:
      added_geners.append(g.name)

    new_geners = request.form.getlist('genres')
    # print(added_geners)
    # print(new_geners)
    # print('---------------------------------------------------------------')
    
    if set(new_geners).difference(added_geners) is not None:
      for new_genere in set(new_geners).difference(added_geners):
        venuegener = VenueGeners(name=new_genere)
        venuegener.venue = venue
        print('---------------------------added ------------------------------')
        print(new_genere)

    if set(added_geners).difference(new_geners) is not None:
      for genere_to_be_deleted in set(added_geners).difference(new_geners):
        print(genere_to_be_deleted)
        db.session.query(VenueGeners).filter(VenueGeners.name == genere_to_be_deleted, VenueGeners.vanue_id == venue.id).delete()
    

    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
     # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + request.form['name'] + '  could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

# @app.route('/artists/create', methods=['GET'])
# def create_artist_form():
#   form = ArtistForm()
#   return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if request.method == 'POST':
    print('form ', request.form)
    # form = ArtistForm(request.form)
    if form.validate():
      # print('yyyyyayy')
      # flash('Something went wrong !')
      # return render_template('pages/home.html')
      try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        image_link= ''

        # get file image and save it under image folder, and rename image file after name of venue
        if request.files:
          image = request.files["image_link"]
          image_link= request.form['name'] + '_Image.' + request.files["image_link"].filename.rsplit(".", 1)[1]
          image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_link))

        website = request.form['website']
        # print(request.form['seeking_venue'])

        seeking_venue = False
        if 'seeking_venue' in request.form:
          if request.form['seeking_venue'] == 'y':
            seeking_venue = True
        print(seeking_venue)

        seeking_description = request.form['seeking_description']

        artist = Artist(name=name, city=city, state=state,phone=phone, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
        # loop throug all geners, create artistgenere and then assign its artist attribute to nwely created artist 
        for g in genres:
          artistgener = ArtistGeners(name=g)
          artistgener.artist = artist
          print(g)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + request.form['name'] + '  could not be listed.')
        db.session.rollback()
      finally:
        db.session.close()

      return render_template('pages/home.html')
    else:
      flash('Check Validators')

  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = db.session.query(Shows.date.label('start_time'), Shows.venue_id, Venue.name.label('venue_name'), Shows.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link')).join(Venue, Artist).all()
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create/')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create/', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    date = request.form['start_time']
    show = Shows(venue_id=venue_id, artist_id=artist_id, date=date)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

