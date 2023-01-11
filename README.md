# TROPOMI Processing Tools

#### External Libraries required:    
    xmltodict
    numpy
    netCDF4
    shapely
## Introduction
Observing small areas for methane emissions via TROPOMI is complicated by the fact that downloaded datasets can contain 
substantial data outside the required bounds of an area being observed, and data is available in swathes from the orbiting 
satellite, rather than a timeseries that can be fed into modelling or data inspection tools.

The overall goal is to assist or automate the conversion of multiple downloaded orbits to a time series that can be applied 
more easily.

## Sentinel-5P
All credit to the copernicus programme, information about Sentinel-5P can be found below
Copernicus Open Access Hub: https://scihub.copernicus.eu/userguide/WebHome
Information of methane product: https://sentinels.copernicus.eu/documents/247904/0/Sentinel-5P-Methane-Product-Readme-File/d7214038-25a9-416f-8deb-d5d6c766f92e

## tropomi_archiving.py functions
    bounds_to_string(bounds)
    Converts array of pairs of longitudes and latitudes to a string to query s5phub by footprint.
    returns string
    
    sentinel5_query(satellite, product, limits, rows)
    Takes satellite, product, limits and rows inputs to query the s5phub for a list of files meeting the query requirements.
    Note that rows dictates the number of file links returned by the query with a maximum of 100. 
    PLEASE NOTE: This function is pending change to incorporate additional query options, and specifically the "skip" parameter which is required for returning additional files from the 100 with the same parameters.
    returns list
  
    download_tropomi_file(query_item, output_folder)
    Takes in a list of files returned from sentinel5_query as "query_item" and downloads the resulting netCDF4 file to the "output_folder".
    returns None
    
## tropomi_reader.py functions
    class MethaneNC (filename, limits, location_name="Map")
    Class that will produce an output .nc file and additional methods for appending to as a time series and for interacting with it.
    filename = Output .nc filename
    limits = List of longitude/latitude pairs to limit appended data to [(130.604, -26.725), (130.604, -12.725), (144.604, -12.725), (144.604, -26.725)]
    location_name = Name detail that will be included in the output filename and the properties of the netCDF4 file itself.
    
    Methods:
    time_series_nc_creation(self)
    Structures and creates an output .nc file for appending to.
    
    append_orbit_nc(self, input_dataset_filename)
    Appends the methane analysis data from a TROPOMI sourced .nc file to the main file as a time series rather than being separated by swathe.
    
    open_file(self)
    Reopens the main file
    
    delete_file(self)
    Deletes the main file, used for restarting, and for bug checking.
    
    plot_methane(self)
    Creates matplotlib plots of all data, separated by orbit and viewable using a slider.
    PLEASE NOTE: This graphing function is very very basic and is only creating a simple scatter plot at the moment. This will be iterated upon.
    
    
    Stand alone functions:
    
    read_tropomi_nc(filename)
    Opens a TROPOMI .nc file as a Dataset and outputs a dictionary of properties and an orbit number for additional processing.
    returns dict (data), integer (orbit)
    
    reduce_data(data, orbit, qa_filter=True, limits=[(-180., -90.), (-180., 90.), (180., 90.), (180., -90.)])
    Reads in data of the format returned by read_tropomi_nc and filters data outside of the latitude and longitude boundaries, data with a quality 
    factor below 0.5 as specified by TROPOMI, and where the methane value is not produced.
    return dict
    
    check_latlong_intersect(coords, test_point)
    Uses shapely to check whether a point specified by "test_point" is within a polygon defined by "coords".
    returns bool
    
    create_all_data_array(self, directory)
    Creates a list from a directory of .nc files, indexed as swathes. This function is redundant and should be retired.
    returns list
    
## Usage
TROPOMI data should be downloaded from the sentinel-5P API using tropomi_archiving.py and saved into a sub directory 
"tropomi_data/" before using tropomi_reader.py to reprocess methane format data into a time series.

## To Do
- Implement unit test program
- Implement further query options, and potential automation to download a large quantity of data for a certain area
- Improve plotting functions
- Implement statistical observation outputs

## Contact
Shannon Egan - shan@egan.mobi

Link to project - https://github.com/ShannonEgan0/image_altar.git
