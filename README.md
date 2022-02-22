# Asheville Crime Data
Analysis of Asheville Crime Data
Nicholas Pierson (nmpierson@gmail.com)
<h2>Introduction</h2>

<p>This repository utilizes Asheville Public Safety data (https://data-avl.opendata.arcgis.com/search?tags=publicsafety)
  from the City of Asheville, North Carolina. </p>

<p>The Asheville Police Department recently released materials implying that "Large Encampments" are responsible for a substantial
  proportion of the city's crime. They support this claim first by showing percentages of total crime within 500 or 1000 feet of areas they
  label as encampments; second with two tables showing select violent and property crime counts within those distances of each encampment. </p>

<p>Our analysis suggests that the police's first claim falls into a correlation vs. causation fallacy. The areas labeled as "large encampments" correspond
  to densely populated areas across the city. A similar selection of bars and restaurants yields almost identical crime results. </p>
<p>We also find that the police's data tables for crimes within 500 and 1000 feet of different encampments drastically overcount crime.
  They do not take into account crimes that occur within the radius of more than one encampment; as a result, arrests are overcounted by 25% within 500 feet
  and 106% within 1000 feet. </p>
  
 <h2> Limitations </h2>
 <p> While arrest and 911 call data are both publicly available, it is not clear what exactly constitutes "Total Crime." Police cited 22,611 total crimes
  over the past two years in a recent press release. Our analysis uses Arrest information, 15,015 total. This is not a perfect replication; therefore we 
  encourage the Asheville PD to release a full summary of the metrics they use to arrive at total crime, as well as a full summary of the data they 
  used to create their recent press releases. </p>
 <p> Not all crimes were able to be geotagged from police address report to latitude and longitude coordinates using API calls. However, with approximately 90% matched, the    dataset should be strongly representative. </p>
  
 <h2>Requirements</h2>
 <p>Viewing the powerpoint summary, map, and output files can be done without running any code. </p>
 <p>In order to replicate the data transformation and geotagging steps, Python is required. The necessary modules
  for running are included in requirements.txt. </p>
 <p> Note: the script utilizes the open source Nominatim API to encampment and arrest coordinates. This API
  is capped at ~1 request per second and can therefore be time-consuming. If a faster API is available,
  it is recommended to rewrite the location function to utilize the faster API. </p>
 <p> In order to replicate the mapping steps, Jupyter Notebook and geopandas are required. See https://geopandas.org/en/stable/getting_started/install.html for
  detailed installation information. </p>

<h2> Resources </h2>

<p> The Asheville Crime Analysis powerpoint contains a summary of findings, and visualizations. </p>
<p> The apd_original_slides folder contains information previously presented by the Asheville Police Department. </p>
<p> The source_files folder contains downloads from Asheville's Public Safety data. asheville_crime_data.py loads, cleans, transforms, and analyzes this data. <br>
  asheville_crime_data.py writes to the output folder.</p>
<p> The shapefiles folder contains shapefiles for Asheville's city limits, also downloaded from their data portal (Asheville City Limits at https://data-avl.opendata.arcgis.com/search?source=city%20of%20asheville%7C%20north%20carolina&tags=boundaries) <br>
  Asheville_Mapping.ipynb is a Jupyter notebook using the shapefiles and coordinates mapped from asheville_crime_data.py to create maps of the locations. Several of these maps     were manually saved and committed to the maps folder.</p>
