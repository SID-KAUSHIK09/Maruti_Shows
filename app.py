from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import random


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///ticket.db"
db=SQLAlchemy(app)

@app.route('/')
def start():
    return render_template('start.html')
@app.route('/admin_login',methods=['POST','GET'])
def admin_login():
    if request.method=='POST':
        a_name_=request.form['a_name']
        a_password_=request.form['a_password']
        query = admin.query.filter_by(name=a_name_, password=a_password_).first()
        db.session.commit()
        if query is not None:
            return redirect('/admin_work')
    return render_template('admin_login.html')


@app.route('/user_login',methods=['POST','GET'])
def user_login():
    if request.method=='POST':
        u_name=request.form['u_name']
        u_password=request.form['u_password']
        query=user.query.filter_by(name=u_name,password=u_password).first()
        db.session.commit()
        user_sno=query.sno
        if query is not None:
            return render_template('userpage.html',user_sno=user_sno)
        else:
            return render_template('user_login.html',message="Can't find, please check username and password.")
    return render_template('user_login.html', message='')


@app.route('/user_register',methods=['POST','GET'])
def user_register():
    if request.method=='POST':
        u_name=request.form['u_name']
        u_password=request.form['u_password']
        user_name=user.query.filter_by(name=u_name).first()
        if user_name is not None:
            return render_template('user_login.html',message="Username already exists!, try another.")
        else:
            User=user(name=u_name,password=u_password)
            db.session.add(User)
            db.session.commit()
            return render_template('user_login.html',message="Registered!, now login.")
    return render_template('user_login.html',message="")


@app.route('/book/<int:sno>/<int:user_sno>',methods=['POST','GET'])
def book(sno,user_sno):
    target_show=shows.query.filter_by(sno=sno).first()  
    target_venue=venue.query.filter_by(sno=target_show.venue_id).first()      
    return render_template('ticket_book.html',target_show=target_show,sno=sno,target_venue=target_venue,user_sno=user_sno)

@app.route('/book_tickets/<int:sno>/<int:user_sno>',methods=['POST'])
def book_tickets(sno,user_sno):
    if request.method=='POST':
        target_show=shows.query.filter_by(sno=sno).first()
        ticket_count=request.form['tickets_count']
        real_count=target_show.available
        new_count=int(real_count)-int(ticket_count)
        print(new_count)
        if new_count>=0:
            if request.method=='POST':
                show_name=target_show.show_name
                start_time=target_show.start_time
                end_time=target_show.end_time
                rating=target_show.rating
                tags=target_show.tags
                price=target_show.price
                Show=shows.query.filter_by(sno=sno).first()
                Show.show_name=show_name
                Show.start_time=start_time
                Show.end_time=end_time
                Show.rating=rating
                Show.tags=tags
                Show.price=price
                Show.available=new_count
                db.session.add(Show)
                db.session.commit()
            if request.method=='POST':
                show_name_=target_show.show_name
                start_time_=target_show.start_time
                end_time_=target_show.end_time
                no_of_tickets_=ticket_count
                target_venue_id=target_show.venue_id
                # print(target_venue_id)
                venue_targeted=venue.query.filter_by(sno=target_venue_id).first()
                venue_name_=venue_targeted.name
                venue_place_=venue_targeted.place
                venue_location_=venue_targeted.location
                # print(venue_name_)
                string=str(no_of_tickets_)+' tickets booked for '+str(show_name_)+',time: '+str(start_time_)+'-'+str(end_time_)+' at '+venue_name_+', '+venue_place_+', '+venue_location_+'.'
                print(string)
                print(user_sno)
                User=user.query.filter_by(sno=user_sno).first()
                if User.data is None:
                    User.data=string
                else:
                    User.data=User.data+string
                db.session.add(User)
                db.session.commit()

        else:
            return render_template('message.html',message="No, not possible due to seats constaints!")
    return render_template('message.html',message="Booked Successfully!")


@app.route('/theatres/<int:user_sno>',methods=['POST','GET'])
def theatres(user_sno):
    if request.method=='POST':
        location_=(request.form['location']).lower()
        shows_rows=shows.query.all()
        venue_rows=venue.query.filter_by(location=location_).all()
        return render_template('theatres_search.html',shows_rows=shows_rows,venue_rows=venue_rows,user_sno=user_sno)
    return render_template('theatres_search.html',shows_rows=[],venue_rows=[],user_sno=user_sno)


@app.route('/shows_search/<int:user_sno>',methods=['POST','GET'])
def shows_search(user_sno):
    if request.method=='POST':
        show_name=request.form['movie'].lower()
        start_time=request.form['start']
        end_time=request.form['end']
        rating=request.form['rating']
        tags_=request.form['tags'].lower()
        full_list=shows.query.all()
        all_venues=venue.query.all()
        # print(show_name)
        # print(rating)
        # print(type(rating))
        shows_rows_end=full_list
        shows_rows_start=full_list
        shows_rows_rating=full_list
        shows_rows_name=full_list
        shows_rows_tags=full_list
        # print(shows_rows_end,shows_rows_start,shows_rows_rating,shows_rows_name,shows_rows_tags)

        if show_name != '':
            shows_rows_name=shows.query.filter_by(show_name=show_name).all()
        if start_time != '':
            shows_rows_start=shows.query.filter_by(start_time=start_time).all()
        if end_time != '':
            shows_rows_end=shows.query.filter_by(end_time=end_time).all()
        if rating != '':
            shows_rows_rating=shows.query.filter_by(rating=rating).all()
        if tags_ != '':
            shows_rows_tags = shows.query.filter(shows.tags.like('%{}%'.format(tags_))).all()
        # print(shows_rows_end,shows_rows_start,shows_rows_rating,shows_rows_name,shows_rows_tags)
        ans=list(set(shows_rows_name).intersection(shows_rows_end,shows_rows_start,shows_rows_rating,shows_rows_tags))
        return render_template('shows_search.html',shows_rows=ans,all_venues=all_venues,user_sno=user_sno)
    return render_template('shows_search.html',shows_rows=[],all_venues=[],user_sno=user_sno)

@app.route('/admin_work',methods=['GET','POST'])
def venue_func():
    if request.method=='POST':
        name=request.form['name'].lower()
        place=request.form['place'].lower()
        location=request.form['location'].lower()
        capacity=request.form['capacity']
        Venue=venue(name=name,place=place,location=location,capacity=capacity)
        db.session.add(Venue)
        db.session.commit()
    all_venues=venue.query.all()
    return render_template('admin_work.html',all_venues=all_venues)

@app.route('/delete_venue/<int:sno>')
def delete_venue(sno):
    Venue=venue.query.filter_by(sno=sno).first()
    db.session.delete(Venue)
    db.session.commit()
    return redirect('/admin_work')

@app.route('/edit_venue/<int:sno>',methods=['GET','POST'])
def edit_venue(sno):
    if request.method=='POST':
        name=request.form['name'].lower()
        place=request.form['place'].lower()
        location=request.form['location'].lower()
        capacity=request.form['capacity']
        Venue=venue.query.filter_by(sno=sno).first()
        Venue.name=name
        Venue.place=place
        Venue.location=location
        Venue.capacity=capacity
        db.session.add(Venue)
        db.session.commit()
        return redirect('/admin_work')
    Venue=venue.query.filter_by(sno=sno).first()
    return render_template('edit_venue.html',Venue=Venue)

@app.route('/shows/<int:sno>',methods=['GET','POST'])
def shows(sno):
    if request.method=='POST':
        show_name=request.form['name'].lower()
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        rating=request.form['rating']
        tags=request.form['tags'].lower()
        price=request.form['price']
        query=venue.query.filter_by(sno=sno).first()
        available=query.capacity
        Show=shows(show_name=show_name,start_time=start_time,end_time=end_time,rating=rating,tags=tags,price=price,available=available,venue_id=sno)
        db.session.add(Show)
        db.session.commit()
    all_shows=shows.query.filter_by(venue_id=sno)
    target_venue=venue.query.filter_by(sno=sno).first()
    venue_name=target_venue.name+', '+target_venue.place+', '+target_venue.location
    return render_template('shows.html',sno=sno,all_shows=all_shows,venue_name=venue_name)


@app.route('/delete_show/<int:start_time>/<int:end_time>/<int:venue_id>')
def delete_show(start_time,end_time,venue_id):
    Show=shows.query.filter_by(start_time=start_time,end_time=end_time,venue_id=venue_id).first()
    db.session.delete(Show)
    db.session.commit()
    return redirect(f'/shows/{venue_id}')


@app.route('/sno_find/<int:start_time>/<int:end_time>/<int:venue_id>',methods=['GET','POST'])
def sno_find(start_time,end_time,venue_id):
    Show=shows.query.filter_by(start_time=start_time,end_time=end_time,venue_id=venue_id).first()
    sno_=Show.sno
    return redirect(f'/edit_show/{sno_}')

@app.route('/edit_show/<int:sno>',methods=['GET','POST'])
def edit_show(sno):
    if request.method=='POST':
        show_name=request.form['name'].lower()
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        rating=request.form['rating']
        tags=request.form['tags'].lower()
        price=request.form['price']
        Show=shows.query.filter_by(sno=sno).first()
        Show.show_name=show_name
        Show.start_time=start_time
        Show.end_time=end_time
        Show.rating=rating
        Show.tags=tags
        Show.price=price
        db.session.add(Show)
        db.session.commit()
        return redirect(f'/shows/{Show.venue_id}')
    Show=shows.query.filter_by(sno=sno).first()
    return render_template('edit_show.html',Show=Show)


@app.route('/statistics')
def statistics():
    all_venue_rows=venue.query.all()
    dict={}
    ans=[]
    x_axis=[]
    for i in range(1,len(all_venue_rows)+1):
        name_=venue.query.filter_by(sno=i).first().name
        capacity=venue.query.filter_by(sno=i).first().capacity
        target_shows=shows.query.filter_by(venue_id=i).all()
        dict[i]=0
        count=0
        for j in target_shows:
            count+=1
            dict[i]+=capacity-(j.available)#dict is storing values of sno of venue table and occupied seats
        if count==0:
            ans.append(0)        
        else:
            ans.append(dict[i]/(count*capacity))
        x_axis.append(name_)
    plt.figure(figsize=(15, 5))
    plt.bar(x_axis, ans, color='#33A1C9')
    plt.xlabel('Venue Names')
    plt.ylabel('Percentge occupancy')
    plt.title('Bar Chart showing percentage occupancy of venues')
    name=random.randrange(10000000)
    plt.savefig(f'static/{name}.png')
    return render_template('graph.html',name=name)
@app.route('/old_bookings/<int:user_sno>')
def old_bookings(user_sno):
    targeted_user=user.query.filter_by(sno=user_sno).first()
    ans=targeted_user.data
    if ans is not None:
        ans=ans.upper()
        ans=ans.split('.')
    else:
        ans=" "
    return render_template('old_bookings.html',ans=ans)

class venue(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    place=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    capacity=db.Column(db.Integer,nullable=False)
    def __repr__(self) -> str:
        return f"{self.name}-{self.capacity}"
    
class admin(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}'
    
class user(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    data=db.Column(db.String(10000),nullable=True)

    def __repr__(self) -> str:
        return f'{self.name}'

class shows(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    show_name=db.Column(db.String(100),nullable=False)
    start_time=db.Column(db.Integer,nullable=False)
    end_time=db.Column(db.Integer,nullable=False)
    rating=db.Column(db.Integer,nullable=False)
    tags=db.Column(db.String(100),nullable=False)
    price=db.Column(db.Integer,nullable=False)
    available = db.Column(db.Integer, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.sno'), nullable=False)
    venue = db.relationship('venue', backref=db.backref('shows', lazy=True))

    def __repr__(self) -> str:
        return f'{self.show_name}'


with app.app_context():
    db.create_all()
if __name__=="__main__":
    app.run(debug=True)