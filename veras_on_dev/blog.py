from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from veras_on_dev.auth import login_required
from veras_on_dev.db import get_db

bp = Blueprint( 'blog', __name__ )

@bp.route( '/' )
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, COALESCE( like_count, 0 ) AS like_count'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' LEFT JOIN ('
        ' SELECT post_id, COUNT(*) AS like_count FROM likes GROUP BY post_id'
        ') l ON p.id = l.post_id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template( 'blog/index.html', posts = posts )

@bp.route( '/create', methods = ( 'GET', 'POST' ) )
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Title is required'
        
        if error is not None:
            flash( error )
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                ( title, body, g.user[ 'id' ] )
            )
            db.commit()
            return redirect( url_for( 'blog.index' ) )
    
    return render_template( 'blog/create.html' )

def get_post( id, check_author = True ):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', ( id, )
    ).fetchone()

    if post is None:
        abort( 404, f"Post id {id} doesn't exist." )
    
    if check_author and post[ 'author_id' ] != g.user[ 'id' ]:
        abort( 403 )
    
    return post

@bp.route( '/<int:id>/update', methods = ( 'GET', 'POST' ) )
@login_required
def update( id ):
    post = get_post( id )

    if request.method == 'POST':
        title = request.form.get( 'title' )
        body = request.form.get( 'body' )
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash( error )
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                ( title, body, id )
            )

            db.commit()
            return redirect( url_for( 'blog.index' ) )
    
    return render_template( 'blog/update.html', post = post )

@bp.route('/<int:id>/delete', methods = ( 'POST', ) )
@login_required
def delete( id ):
    get_post( id )
    db = get_db()
    db.execute( 'DELETE FROM post WHERE id = ?', ( id,  ) )
    db.execute(
                'DELETE FROM likes WHERE post_id = ?',
                ( id, )
            )
    db.commit()
    return redirect( url_for( 'blog.index' ) )

@bp.route( '/<int:id>/like', methods = ( 'POST', ) )
@login_required
def like( id ):
    if request.method == 'POST':
        
        db = get_db()

        like = db.execute(
            'SELECT * FROM likes WHERE user_id = ? AND post_id = ?',
            ( g.user[ 'id' ], id )
        ).fetchone()

        if like is None:
            db.execute(
                'INSERT INTO likes (user_id, post_id)'
                ' VALUES (?, ?)',
                ( g.user[ 'id' ], id )
            )
            db.commit()
        else:
            db.execute(
                'DELETE FROM likes WHERE user_id = ? AND post_id = ?',
                ( g.user[ 'id' ], id )
            )
            db.commit()

        return redirect( url_for( 'blog.index' ) )

@bp.route( 'post/<int:id>', methods = ( 'GET', 'POST' ) )
def post( id ):
    post = get_post( id )

    if request.method == 'POST':
        return redirect

    return render_template( 'blog/post.html', post = post )