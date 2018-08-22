from flask import render_template, flash, redirect, make_response, url_for
from app import app_var
from listing_scraper import *
from app.forms import LoginForm
import datetime

@app_var.route('/')
@app_var.route('/index')
def index():
    return render_template('index.html')


@app_var.route('/cityinput', methods = ['GET', 'POST'])
def cityinput():
    form = LoginForm()
    if form.validate_on_submit():
        
        flash('listings requested for {}'.format(form.city.data))
        listings_list = listings_scrape(form.city.data)
        if listings_list == None:
            flash('city entered incorrectly, please try again')
            return redirect(url_for('cityinput'))
        else:
            spaces_df = pd.DataFrame(listings_list, columns = ('Address', 'City', 
                                    'Zipcode', 'Property Type', 
                                    'Rentable Building Area (SF)', 'Rental Rate', 
                                    'Service Type', 'Space Available (SF)'))
        
            csv = spaces_df.to_csv()
            #print(csv)
            response = make_response(csv)
            now = datetime.datetime.now()
            city = form.city.data.lower().replace(' ', '-')
            response.headers['Content-Disposition'] = "attachment; filename =" + now.strftime("%m-%d-%Y") + "_" + city + "_listings.csv"
            response.headers['Content-Type'] = "text/csv"
            flash('table for ' + city + ' downloaded')
            return response

    else:
        return render_template('cityinput.html', title='Enter City', form=form)
        
