from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rockbands-mm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)

# ==========================
# DATABASE MODELS
# ==========================

class Bands(db.Model):
    BandID = db.Column(db.Integer, primary_key=True)
    BandName = db.Column(db.String(80), nullable=False)
    FormedYear = db.Column(db.Integer)
    HomeLocation = db.Column(db.String(80))
    memberships = db.relationship('Memberships', backref='band', lazy=True)
    album_connections = db.relationship('AlbumConnections', backref='band', lazy=True)


class Members(db.Model):
    MemberID = db.Column(db.Integer, primary_key=True)
    MemberName = db.Column(db.String(80), nullable=False)
    MainPosition = db.Column(db.String(80))
    memberships = db.relationship('Memberships', backref='member', lazy=True)


class Memberships(db.Model):
    MembershipID = db.Column(db.Integer, primary_key=True)
    BandID = db.Column(db.Integer, db.ForeignKey('bands.BandID'), nullable=False)
    MemberID = db.Column(db.Integer, db.ForeignKey('members.MemberID'), nullable=False)
    StartYear = db.Column(db.Integer)
    EndYear = db.Column(db.Integer)
    Role = db.Column(db.Text)


class Albums(db.Model):
    AlbumID = db.Column(db.Integer, primary_key=True)
    AlbumTitle = db.Column(db.String(80), nullable=False)
    ReleaseYear = db.Column(db.Integer)
    # Many-to-many relationship with Bands through AlbumConnections
    album_connections = db.relationship('AlbumConnections', backref='album', lazy=True)


class AlbumConnections(db.Model):
    """Junction table for many-to-many relationship between Albums and Bands"""
    ConnectionID = db.Column(db.Integer, primary_key=True)
    BandID = db.Column(db.Integer, db.ForeignKey('bands.BandID'), nullable=False)
    AlbumID = db.Column(db.Integer, db.ForeignKey('albums.AlbumID'), nullable=False)
    BandConnection = db.Column(db.Text)  # e.g., "Primary Artist", "Featured", "Collaboration"
    ReleaseYear = db.Column(db.Integer)  # Can differ from album's original release year


# ==========================
# ROUTES
# ==========================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bands/add', methods=['GET', 'POST'])
def add_band():
    if request.method == 'POST':
        new_band = Bands(
            BandName=request.form['bandname'],
            FormedYear=request.form['formedyear'],
            HomeLocation=request.form['homelocation']
        )
        db.session.add(new_band)
        db.session.commit()
        flash('Band added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_band.html')


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    # bands = Bands.query.all()
    if request.method == 'POST':
        new_member = Members(
            MemberName=request.form['membername'],
            MainPosition=None
        )
        db.session.add(new_member)
        db.session.commit()
        flash('Member added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_member.html')


@app.route('/albums/add', methods=['GET', 'POST'])
def add_album():
    if request.method == 'POST':
        release_year = request.form.get('releaseyear')
        new_album = Albums(
            AlbumTitle=request.form['albumtitle'],
            ReleaseYear=int(release_year) if release_year else None
        )
        db.session.add(new_album)
        db.session.commit()
        flash('Album added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_album.html')


@app.route('/bands/view')
def view_by_band():
    bands = Bands.query.all()
    return render_template('display_by_band.html', bands=bands)


@app.route('/bands/view/<int:id>')
def view_band(id):
    band = Bands.query.get_or_404(id)
    return render_template('display_by_band.html', bands=[band])


@app.route('/memberships/add', methods=['GET', 'POST'])
def add_membership():
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership = Memberships(
            BandID=request.form.get('bandid'),
            MemberID=request.form.get('memberid'),
            Role=request.form.get('role'),
            StartYear=request.form.get('startyear') or None,
            EndYear=request.form.get('endyear') or None
        )
        db.session.add(membership)
        db.session.commit()
        flash('Membership assigned', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('add_membership.html', bands=bands, members=members)


@app.route('/memberships/edit/<int:id>', methods=['GET', 'POST'])
def edit_membership(id):
    membership = Memberships.query.get_or_404(id)
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership.BandID = request.form.get('bandid')
        membership.MemberID = request.form.get('memberid')
        membership.Role = request.form.get('role')
        membership.StartYear = request.form.get('startyear') or None
        membership.EndYear = request.form.get('endyear') or None
        db.session.commit()
        flash('Membership updated', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('edit_membership.html', membership=membership, bands=bands, members=members)


@app.route('/memberships/delete/<int:id>')
def delete_membership(id):
    membership = Memberships.query.get_or_404(id)
    db.session.delete(membership)
    db.session.commit()
    flash('Membership removed', 'success')
    return redirect(url_for('view_by_band'))


@app.route('/album-connections/add', methods=['GET', 'POST'])
def add_album_connection():
    bands = Bands.query.all()
    albums = Albums.query.all()
    if request.method == 'POST':
        connection = AlbumConnections(
            BandID=request.form.get('bandid'),
            AlbumID=request.form.get('albumid'),
            BandConnection=request.form.get('bandconnection'),
            ReleaseYear=request.form.get('releaseyear') or None
        )
        db.session.add(connection)
        db.session.commit()
        flash('Album assigned to band', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('add_album_connection.html', bands=bands, albums=albums)


@app.route('/album-connections/edit/<int:id>', methods=['GET', 'POST'])
def edit_album_connection(id):
    connection = AlbumConnections.query.get_or_404(id)
    bands = Bands.query.all()
    albums = Albums.query.all()
    if request.method == 'POST':
        connection.BandID = request.form.get('bandid')
        connection.AlbumID = request.form.get('albumid')
        connection.BandConnection = request.form.get('bandconnection')
        connection.ReleaseYear = request.form.get('releaseyear') or None
        db.session.commit()
        flash('Album connection updated', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('edit_album_connection.html', connection=connection, bands=bands, albums=albums)


@app.route('/album-connections/delete/<int:id>')
def delete_album_connection(id):
    connection = AlbumConnections.query.get_or_404(id)
    db.session.delete(connection)
    db.session.commit()
    flash('Album connection removed', 'success')
    return redirect(url_for('view_by_band'))


# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)