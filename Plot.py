import pandas as pd
import plotly as py

from config import OUTPUT_FILE

def plotly_plot_us(df, title, name, color='rgb(0,116,217)'):
	df['text'] = df['name'] + '<br>' + df['city'] + '<br>' + df['state']
	color = color
	cities = []

	city = dict(
	    type = 'scattergeo',
	    locationmode = 'USA-states',
	    lon = df['lon'],
	    lat = df['lat'],
	    text = df['text'],
	    marker = dict(
	        #size = 1000,
	        color = color,
	        line = dict(width=0.5, color='rgb(40,40,40)'),
	        sizemode = 'area'
	    ),
	    name = name )
	cities.append(city)

	layout = dict(
	        title = title,
	        showlegend = True,
	        geo = dict(
	            scope='usa',
	            projection=dict( type='albers usa' ),
	            showland = True,
	            landcolor = 'rgb(217, 217, 217)',
	            subunitwidth=1,
	            countrywidth=1,
	            subunitcolor="rgb(255, 255, 255)",
	            countrycolor="rgb(255, 255, 255)"
	        ),
	    )

	fig = dict( data=cities, layout=layout )

	return fig

df = pd.read_csv(OUTPUT_FILE)
fig = plotly_plot_us(df, 'Colleges with Programs in AI', 'AI Colleges')
py.offline.plot(fig, validate=False, filename='colleges_with_AI_programs.html' )