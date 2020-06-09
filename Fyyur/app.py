#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import  Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)
# (done) TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue',lazy=True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120)) # PickleType?
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='artist',lazy=True)
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable= False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
  #Venue
  start_time = db.Column(db.String(120),nullable = False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues') #DONE
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  dataload=[]
  distinct_venues = Venue.query.distinct(Venue.city).all()
  for venue_city in distinct_venues:
    venues_all = Venue.query.filter(Venue.city == venue_city.city)
    
    body = {}
    body['city'] = venue_city.city
    body['state'] = venue_city.state
    bodyshell= []
    for venue in venues_all:
      bodyinner = {}
      bodyinner['id'] = venue.id
      bodyinner['name'] = venue.name
      bodyinner['num_upcoming_shows'] = len(Venue.query.filter(Venue.city==venue_city.city).all())
      bodyshell.append(bodyinner)
    body['venues'] = bodyshell
    dataload.append(body)

  return render_template('pages/venues.html', areas=dataload);

@app.route('/venues/search', methods=['POST']) #DONE
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchterm = request.form.get('search_term')
  if searchterm =="":
    redirect(url_for('venues'))
  filtered_venues = Venue.query.filter(func.lower(Venue.name).contains(searchterm.lower())).all()
  dataload = []
  for venue in filtered_venues:
    body = {}
    body['id'] = venue.id
    body['name'] = venue.name
    body['num_upcoming_shows'] = len(venue.shows)
    dataload.append(body)

  response={
    "count": len(filtered_venues),
    "data": dataload
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>') # DONE
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  my_venue = Venue.query.filter(Venue.id==venue_id).first()
  venue_count = len(Venue.query.all())
  #print(str(venue_count) + ' < ' + venue_id)
  if venue_count < venue_id:
    return redirect(url_for('create_venue_form'))
  dataload = {}
  dataload['name'] = my_venue.name
  dataload['genres'] = str(my_venue.genres).replace('{','').replace('}','').split(',') # NOT BEST PRACTISE...
  #print('THESE ARE THE GENRES---->')
  #print(str(my_venue.genres).replace('{','').replace('}','').split(','))
  #print('-------------------------')
  dataload['address'] = my_venue.address
  dataload['city'] = my_venue.city
  dataload['state'] = my_venue.state
  dataload['phone'] = my_venue.phone
  dataload['website'] = my_venue.website
  dataload['facebook_link'] = my_venue.facebook_link
  dataload['seeking_talent'] = my_venue.seeking_talent
  dataload['seeking_description'] = my_venue.seeking_description
  dataload['image_link'] = my_venue.image_link

  #past_shows
  past_shows = []
  for past_event in Show.query.filter(Show.venue_id==venue_id).all(): #,Show.start_time<datetime.now
    if dateutil.parser.parse(past_event.start_time) < datetime.now():
      for artist in Artist.query.filter(Artist.id==past_event.artist_id):
        past_show_artist = {}
        past_show_artist['artist_id'] = artist.id
        past_show_artist['artist_name'] = artist.name
        past_show_artist['artist_image_link'] = artist.image_link
        past_show_artist['start_time'] = past_event.start_time
        past_shows.append(past_show_artist)
  dataload['past_shows'] = past_shows

  #upcoming_shows
  upcoming_shows = []
  for upcoming_event in Show.query.filter(Show.venue_id==venue_id).all(): #, Show.start_time>datetime.now
    if dateutil.parser.parse(upcoming_event.start_time) >= datetime.now():
      for artist in Artist.query.filter(Artist.id==upcoming_event.artist_id):
        upcoming_show_artist = {}
        upcoming_show_artist['artist_id'] = artist.id
        upcoming_show_artist['artist_name'] = artist.name
        upcoming_show_artist['artist_image_link'] = artist.image_link
        upcoming_show_artist['start_time'] = upcoming_event.start_time
        upcoming_shows.append(upcoming_show_artist)
  dataload['upcoming_shows'] = upcoming_shows

  dataload['past_shows_count'] = len(past_shows)
  dataload['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=[dataload][0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET']) # DONE from before
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) #DONE
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    print(request.form.items)
    name  = request.form.get('name')
    city  = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone  = request.form.get('phone')
    genres =  request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, genres = genres, facebook_link = facebook_link)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE']) #DONE
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('Could not delete venue ' + venue_id + '.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return redirect(url_for('venues'),method = ['GET'])
  return render_template('pages/home.html')
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') # DONE --
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST']) #DONE
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchterm = request.form.get('search_term')
  filtered_artists = Artist.query.filter(func.lower(Artist.name).contains(searchterm.lower())).all()
  dataload = []
  for artist in filtered_artists:
    body = {}
    body['id'] = artist.id
    body['name'] = artist.name
    body['num_upcoming_shows'] = len(artist.shows)
    dataload.append(body)

  response={
    "count": len(filtered_artists),
    "data": dataload
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>') #DONE
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #venues = # All venues where artist has shows 
  my_artist = Artist.query.get(artist_id)
  artist_count = len(Artist.query.all())
  if artist_count < artist_id:
    return redirect(url_for('create_artist_form'))
  dataload = {}
  dataload['name'] = my_artist.name
  dataload['genres'] = str(my_artist.genres).replace('{','').replace('}','').split(',') # NOT BEST PRACTISE...
  dataload['city'] = my_artist.city
  dataload['state'] = my_artist.state
  dataload['phone'] = my_artist.phone
  dataload['website'] = my_artist.website
  dataload['facebook_link'] = my_artist.facebook_link
  dataload['seeking_venue'] = my_artist.seeking_venue
  dataload['seeking_description'] = my_artist.seeking_description
  dataload['image_link'] = my_artist.image_link

  #print('Past Events times:')
  #past_shows
  past_shows = []
  for past_event in Show.query.filter(Show.artist_id==artist_id).all(): #,Show.start_time<datetime.now
    print(past_event.start_time)
    if dateutil.parser.parse(past_event.start_time) < datetime.now():
      for venue in Venue.query.filter(Venue.id==past_event.venue_id):
        past_show_venue = {}
        past_show_venue['venue_id'] = venue.id
        past_show_venue['venue_name'] = venue.name
        past_show_venue['venue_image_link'] = venue.image_link
        past_show_venue['start_time'] = past_event.start_time
        #print('-->'+past_event.start_time)
        past_shows.append(past_show_venue)
  dataload['past_shows'] = past_shows

  #print('Upcoming Events times:')
  #upcoming_shows
  upcoming_shows = []
  for upcoming_event in Show.query.filter(Show.artist_id==artist_id).all(): #, Show.start_time>datetime.now
    if dateutil.parser.parse(upcoming_event.start_time) >= datetime.now():
      for venue in Venue.query.filter(Venue.id==upcoming_event.venue_id):
        upcoming_show_venue = {}
        upcoming_show_venue['venue_id'] = venue.id
        upcoming_show_venue['venue_name'] = venue.name
        upcoming_show_venue['venue_image_link'] = venue.image_link
        upcoming_show_venue['start_time'] = upcoming_event.start_time
        #print('-->'+upcoming_event.start_time)
        upcoming_shows.append(upcoming_show_venue)
  dataload['upcoming_shows'] = upcoming_shows

  dataload['past_shows_count'] = len(past_shows)
  dataload['upcoming_shows_count'] = len(upcoming_shows)
 
  return render_template('pages/show_artist.html', artist=[dataload][0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) #DONE
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST']) #DONE
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #user = User.query.get(some_id)
  #user.name = 'Some new name'
  #db.session.commit()
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres =request.form.get('genres')
    artist.facebook_link = request.form.get('facebook_link')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET']) #DONE
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST']) #DONE
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city= request.form.get('city')
    venue.state= request.form.get('state')
    venue.address= request.form.get('address')
    venue.genres= request.form.get('genres')
    venues.facebook_link = request.form.get('facebook_link')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET']) #DONE
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST']) #DONE
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    artist = Artist(name=name, city=city, state= state, phone = phone, genres = genres, image_link = image_link, facebook_link = facebook_link)
    # on successful db insert, flash success
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name']+ ' could not be added to database.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')  # DONE 
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  dataload = []
  for show in shows:
    body = {}
    associated_venue = Venue.query.get(show.venue_id)
    associated_artist = Artist.query.get(show.artist_id)
    body['venue_id'] = show.id
    body['venue_name'] = associated_venue.name
    body['artist_id'] = show.id        
    body['artist_name'] = associated_artist.name
    body['artist_image_link'] = associated_artist.image_link
    body['start_time'] = show.start_time
    dataload.append(body)

  return render_template('pages/shows.html', shows=dataload)

@app.route('/shows/create') # DONE from before
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) #DONE
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    artist_name = Artist.query.filter(Artist.id == artist_id).first().name
    venue_name = Venue.query.filter(Venue.id == venue_id).first().name
    name = artist_name + ' at ' + venue_name + "!"
    start_time = request.form.get('start_time')
    show = Show(name= name, artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
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
