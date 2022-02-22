# Asheville Crime Data
Analysis of Asheville Crime Data
<h2>Introduction</h2>

<p>This repository utilizes Asheville Public Safety data (https://data-avl.opendata.arcgis.com/search?tags=publicsafety)
  from the City of Asheville, North Carolina. </p>

<p>The Asheville Police Department recently released materials implying that "Large Encampments" are responsible for a substantial
  proportion of the city's crime. They support this claim first by showing percentages of total crime within 500 or 1000 feet of areas they
  label as encampments; second with two tables showing select violent and property crime counts within those distances of each encampment. </p>

<p>Our analysis suggests that the police's first claim falls into a correlation vs. causation fallacy. The areas labeled as "large encampments" correspond
  to densely populated areas across the city. A similar selection of bars and restaurants yields almost identical crime results. <br>
  We also find that the police's data tables for crimes within 500 and 1000 feet of different encampments drastically overcount crime.
  They do not take into account crimes that occur within the radius of more than one encampment; as a result, arrests are overcounted by 25% within 500 feet
  and 106% within 1000 feet. </p>
  
 <h2>Requirements</h2>
 <p>Viewing the powerpoint summary, map, and output files can be done without running any code. </p>
 <p>In order to replicate the data transformation and geotagging steps, Python is required. The necessary modules
  for running are included in requirements.txt. </p>
 <p> Note: the script utilizes the open source Nominatim API to encampment and arrest coordinates. This API
  is capped at ~1 request per second and can therefore be time-consuming. If a faster API is available,
  it is recommended to rewrite the location function to utilize the faster API. </p>
 <p> In order to replicate the mapping steps, Jupyter Notebook and geopandas are required. See https://geopandas.org/en/stable/getting_started/install.html for
  detailed installation information. </p>
