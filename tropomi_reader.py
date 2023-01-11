from netCDF4 import Dataset
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
import os
from matplotlib.widgets import Slider
from datetime import datetime
import sys

# Main function
def main():
    limits = [(130.604, -26.725), (130.604, -12.725), (144.604, -12.725), (144.604, -26.725)]
    counter = 1
    total_files = len(os.listdir("tropomi_data"))
    time_series_file = MethaneNC("Map - TROPOMI Methane Data.nc", limits)
    time_series_file.time_series_nc_creation()
    directory = "tropomi_data/"
    for filename in os.listdir(directory):
        time_series_file.append_orbit_nc(directory + filename)
        print(f'"File number {counter} of {total_files} complete')
        counter += 1
    return time_series_file


def read_tropomi_nc(filename):
    # Need to institute a try except to account for corrupt files, need to know exception type
    with Dataset(filename) as dataset:
        PRODUCT = dataset["/PRODUCT/"]
        GEOLOCATIONS = dataset["/PRODUCT/SUPPORT_DATA/GEOLOCATIONS"]
        DETAILED_RESULTS = dataset["/PRODUCT/SUPPORT_DATA/DETAILED_RESULTS"]
        INPUT_DATA = dataset["/PRODUCT/SUPPORT_DATA/INPUT_DATA"]

        out_dict = {}

        orbit = dataset.orbit

        out_dict.update({'methane': np.array(PRODUCT["methane_mixing_ratio_bias_corrected"][0])})
        out_dict.update({'methane_error': np.array(PRODUCT["methane_mixing_ratio_precision"][0])})
        out_dict.update({'timeUTC': np.array(PRODUCT["time_utc"][0])})
        out_dict.update({'latitude_bounds': np.array(GEOLOCATIONS.variables['latitude_bounds'][0])})
        out_dict.update({'longitude_bounds': np.array(GEOLOCATIONS.variables['longitude_bounds'][0])})
        out_dict.update({'ground_pixel': np.array(PRODUCT.variables['ground_pixel'])})
        out_dict.update({'latitude_cp': np.array(PRODUCT["latitude"][0])})
        out_dict.update({'longitude_cp': np.array(PRODUCT["longitude"][0])})
        out_dict.update({'surface_press': np.array(INPUT_DATA["surface_pressure"][0])})
        out_dict.update({'pressure_int': np.array(INPUT_DATA["pressure_interval"][0])})
        out_dict.update({'solar_zenith': np.array(GEOLOCATIONS["/solar_zenith_angle"][0])})
        out_dict.update({'sensor_zenith': np.array(GEOLOCATIONS["/viewing_zenith_angle"][0])})
        out_dict.update({'solar_azimuth': np.array(GEOLOCATIONS["/solar_azimuth_angle"][0])})
        out_dict.update({'sensor_azimuth': np.array(GEOLOCATIONS["/viewing_azimuth_angle"][0])})
        out_dict.update({'column_averaging_kernel': np.array(DETAILED_RESULTS["/column_averaging_kernel"][0])})
        out_dict.update({'methane_profile_apriori': np.array(INPUT_DATA["/methane_profile_apriori"][0])})
        out_dict.update({'qa': np.array(dataset["/PRODUCT/qa_value"][0])})

        print(f"Orbit {orbit} read")
        return out_dict, orbit


class MethaneNC:
    def __init__(self, filename, limits, location_name="Map"):
        self.filename = filename
        self.limits = limits
        self.location_name = location_name

    def time_series_nc_creation(self):
        # Need error checking in place for existing filename that matches the intended output
        filename = self.filename
        if filename not in os.listdir():
            with Dataset(filename, "w") as rootgrp:
                rootgrp.location_name = self.location_name
                rootgrp.location_bounds = str(self.limits)
                rootgrp.sensor = "TROPOMI CH4"
                rootgrp.information = "Recompiled data from TROPOMI netCDF4 methane sensor data referred to at " \
                                      "http://www.tropomi.eu/data-products/methane"
                rootgrp.creation_datetime = datetime.utcnow().isoformat().replace("T", " ")
                rootgrp.updated_date = "None"

                corner_dim = rootgrp.createDimension('corner', 4)
                time_dim = rootgrp.createDimension('time', None)
                layer_dim = rootgrp.createDimension('layer', 12)

                orbit_number = rootgrp.createVariable('orbit_number', 'int32', 'time', zlib=True, chunksizes=(1000,),
                                                      complevel=4)
                orbit_number.comment = 'Swathe number increasing since beginning of data record and ' \
                                       'correlates to data source filenames'
                orbit_number.units = '1'

                timeUTC = rootgrp.createVariable('timeUTC', 'float64', 'time', zlib=True, chunksizes=(1000,),
                                                 complevel=4)
                timeUTC.units = 'seconds since 2010-1-1 00:00:00'
                timeUTC.axis = 'T'
                timeUTC.calendar = 'gregorian'

                methane_error = rootgrp.createVariable('methane_error', 'float32', 'time', zlib=True,
                                                       chunksizes=(1000,), complevel=4)
                methane_error.units = 'ppb'
                methane_error.long_name = 'dry_atmosphere_mole_fraction_of_methane standard_error'

                methane = rootgrp.createVariable('methane', 'float32', 'time', zlib=True,
                                                 chunksizes=(1000,), complevel=4)
                methane.units = 'ppb'
                methane.long_name = 'bias corrected column-averaged dry-air mole fraction of methane'
                methane.comment = 'This variable refers to the measued methane fraction ' \
                                  'in the associated bounded area'
                methane.coordinates = 'time longitude latitude'

                latitude_bounds = rootgrp.createVariable('latitude_bounds', 'float32', ('time', 'corner'), zlib=True,
                                                         chunksizes=(1000, 4), complevel=4)
                latitude_bounds.units = 'degrees_north'
                longitude_bounds = rootgrp.createVariable('longitude_bounds', 'float32', ('time', 'corner'), zlib=True,
                                                          chunksizes=(1000, 4), complevel=4)
                longitude_bounds.units = 'degrees_east'
                latitude_bounds.comment = 'The latitudes of the corners of a pixel, ' \
                                          'ordered counter-clockwise beginning from the South-West Corner'
                longitude_bounds.comment = 'The longitudes of the corners of a pixel, ' \
                                           'ordered counter-clockwise beginning from the South-West Corner'

                latitude_cp = rootgrp.createVariable('latitude_cp', 'float32', 'time', zlib=True, chunksizes=(1000,),
                                                     complevel=4)
                longitude_cp = rootgrp.createVariable('longitude_cp', 'float32', 'time', zlib=True,
                                                      chunksizes=(1000,), complevel=4)
                latitude_cp.units = 'degrees_north'
                longitude_cp.units = 'degrees_east'
                latitude_cp.comment = 'The latitude of the mid point of a pixel'
                longitude_cp.comment = 'The longitude of the mid point of a pixel'

                surface_press = rootgrp.createVariable('surface_press', 'float32', 'time', zlib=True,
                                                       chunksizes=(1000,), complevel=4)
                surface_press.comment = 'surface air pressure'
                surface_press.units = 'Pa'

                pressure_int = rootgrp.createVariable('pressure_int', 'float32', 'time', zlib=True,
                                                      chunksizes=(1000,), complevel=4)
                pressure_int.comment = 'pressure difference between levels in the retrieval'
                pressure_int.units = 'Pa'

                sensor_azimuth = rootgrp.createVariable('sensor_azimuth', 'float32', 'time', zlib=True,
                                                        chunksizes=(1000,),
                                                        complevel=4)
                sensor_azimuth.comment = 'Satellite azimuth angle at the ground pixel location on the reference ' \
                                         'ellipsoid. Angle is measured clockwise from the North (East = 90, ' \
                                         'South = 180, West = 270)'
                sensor_azimuth.units = 'degree'

                solar_azimuth = rootgrp.createVariable('solar_azimuth', 'float32', 'time', zlib=True,
                                                       chunksizes=(1000,),
                                                       complevel=4)
                solar_azimuth.comment = 'Solar azimuth angle at the ground pixel location on the reference ' \
                                        'ellipsoid. Angle is measured clockwise from the North (East = 90, ' \
                                        'South = 180, West = 270)'
                solar_azimuth.units = 'degree'

                sensor_zenith = rootgrp.createVariable('sensor_zenith', 'float32', 'time', zlib=True,
                                                       chunksizes=(1000,),
                                                       complevel=4)
                sensor_zenith.comment = 'Zenith angle of the satellite at the ground pixel location on the reference ' \
                                        'ellipsoid. Angle is measured away from the vertical'
                sensor_zenith.units = 'degree'

                solar_zenith = rootgrp.createVariable('solar_zenith', 'float32', 'time', zlib=True, chunksizes=(1000,),
                                                      complevel=4)
                solar_zenith.comment = 'Solar zenith angle at the ground pixel location on the reference ellipsoid. ' \
                                       'Angle is measured away from the vertical'
                solar_zenith.units = 'degree'

                column_averaging_kernel = rootgrp.createVariable('column_averaging_kernel', 'float32',
                                                                 ('time', 'layer'),
                                                                 zlib=True,
                                                                 chunksizes=(1000, 12), complevel=4)
                column_averaging_kernel.comment = 'Column averaging kernel for the methane retrieval'

                methane_profile_apriori = rootgrp.createVariable('methane_profile_apriori', 'float32',
                                                                 ('time', 'layer'),
                                                                 zlib=True,
                                                                 chunksizes=(1000, 12), complevel=4)
                methane_profile_apriori.comment = 'Mole content of methane in atmosphere layer'
                methane_profile_apriori.units = 'mol m-2'

                qa = rootgrp.createVariable('qa', 'uint8', 'time', zlib=True, chunksizes=(1000,), complevel=4)
                qa.comment = 'a continuous quality descriptor, varying between 0 (no data) and 1 ' \
                             '(full quality data). Recommend to ignore data with qa_value < 0.5'
                qa.scale_factor = 0.01
                qa.units = '1'
        else:
            check = (input("Filename already exists, do you wish to proceed? (Y/N)")).lower()
            if check in ("y", "yes"):
                return 0
            else:
                print("Quitting")
                sys.exit()

    def append_orbit_nc(self, input_dataset_filename):
        with Dataset(self.filename, "a") as f:
            f.updated_date = datetime.utcnow().isoformat().replace("T", " ")
            data, orbit = read_tropomi_nc(input_dataset_filename)
            if orbit in f['orbit_number']:
                print(f"{input_dataset_filename} already in compiled dataset, skipping file")
                return 0
            reduced = reduce_data(data, orbit=orbit, limits=self.limits)
            print(f"Appending orbit {orbit}")
            length = len(f['timeUTC'][:])
            for i in reduced.keys():
                if i == 'latitude_bounds' or i == 'longitude_bounds':
                    f[i][length:] = reduced[i].reshape(-1, 4)
                elif i == 'column_averaging_kernel' or i == 'methane_profile_apriori':
                    f[i][length:] = reduced[i].reshape(-1, 12)
                elif i == 'timeUTC':
                    timearray = []
                    for j in reduced['timeUTC']:
                        timearray.append(np.array([(datetime.strptime(j, '%Y-%m-%dT%H:%M:%S.%fZ') -
                                                    datetime(2010, 1, 1)).total_seconds()]))
                    f['timeUTC'][length:] = np.array(timearray)
                else:
                    f[i][length:] = reduced[i][:]
            f['orbit_number'][length:] = np.full(len(reduced['methane']), orbit)

    # The two methods below (open and delete) are for testing purposes mainly
    def open_file(self):
        if os.path.exists(self.filename):
            return Dataset(self.filename, 'a')
        else:
            raise OSError("The file no longer exists")

    def delete_file(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        else:
            raise OSError("The file no longer exists")

    # Plotting function plotting data from continuous series with slider
    # Simple implementation, currently just a scatter plot
    def plot_methane(self):
        ds = self.open_file()
        orbit_array = ds['orbit_number'][:]
        plot_array = np.array([ds['longitude_cp'][:], ds['latitude_cp'], ds['methane'][:]])
        orbits = np.unique(orbit_array)

        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.25)
        ax.scatter(plot_array[0][orbit_array == orbits[0]], plot_array[1][orbit_array == orbits[0]],
                   c=plot_array[2][orbit_array == orbits[0]], lw=0, marker=',')
        orbit_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
        orbit_slider = Slider(ax=orbit_ax, valstep=1, valmin=0, valmax=len(orbits - 1), label="orbit")

        def update_orbit(val):
            v = int(orbit_slider.val)
            ax.cla()
            ax.scatter(plot_array[0][orbit_array == orbits[v]], plot_array[1][orbit_array == orbits[v]],
                       c=plot_array[2][orbit_array == orbits[v]], lw=0, marker=',')

        orbit_slider.on_changed(update_orbit)
        plt.show()

        ds.close()


def create_all_data_array(limits, directory):
    all_data = []
    counter = 1
    for filename in os.listdir(directory):
        data, orbit = read_tropomi_nc(directory + filename)
        reduced = reduce_data(data, orbit=orbit, limits=limits)
        if len(reduced['methane']) != 0:
            all_data.append([orbit, reduced])
        else:
            print(f"File number {counter}, orbit {orbit} does not contain any acceptable data")
        print(f'File number {counter} of {len(os.listdir("tropomi_data"))} complete')
        counter += 1
    return all_data

def reduce_data(data, orbit, qa_filter=True, limits=[(-180., -90.), (-180., 90.),
                                                     (180., 90.), (180., -90.)]):
    out_dict = {}
    for i in data.keys():
        if i == 'latitude_bounds' or i == 'longitude_bounds':
            out_dict.update({i: np.empty((0, 4))})
        elif i != 'ground_pixel':
            out_dict.update({i: np.array([])})
    for x in range(len(data['timeUTC'])):
        for y in range(len(data['ground_pixel'])):
            if qa_filter and data['qa'][x][y] < 0.5:
                pass
            elif not check_latlong_intersect(limits, (data['longitude_cp'][x][y], data['latitude_cp'][x][y])):
                pass
            elif data['methane'][x][y] > 1e+30:
                pass
            else:
                for i in out_dict:
                    if i == 'latitude_bounds' or i == 'longitude_bounds':
                        out_dict[i] = np.append(out_dict[i][:], data[i][x][y])
                    elif i == 'timeUTC':
                        out_dict[i] = np.append(out_dict[i], data[i][x])
                    else:
                        out_dict[i] = np.append(out_dict[i], data[i][x][y])

    print(f"Orbit {orbit} reduced")
    return out_dict


def check_latlong_intersect(coords, test_point):
    polygon = Polygon(coords)
    point = Point(test_point[0], test_point[1])
    return polygon.contains(point)


if __name__ == "__main__":
    nc_out = main()
