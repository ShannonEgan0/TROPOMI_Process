import xmltodict
import requests
import sys
import os


def main():
    limits = ((136.604, -20.725), (136.604, -16.725), (140.604, -16.725), (140.604, -20.725))
    files_to_download = 30
    product_type = "L2__CH4___"
    satellite_name = "TROPOMI"

    output_folder = "tropomi_data"

    limits = bounds_to_string(limits)
    query_results = sentinel5_query(satellite_name, product_type, limits, files_to_download)

    for i in query_results:
        download_tropomi_file(i, output_folder)
    print("All Downloads Complete")


# Function below takes in a tuple of any length that will return to index 0 of the tuple
# Each element of the bounds input is a pair of floating point values indicating a longitude and a latitude
# Defines the bounds of a polygon that is used to query TROPOMI for any swathes intersecting the bounded area
def bounds_to_string(bounds):
    bound_text = ""
    counter = 0
    for i in bounds:
        counter += 1
        if 180 >= i[0] >= -180 or 90 >= i[0] >= -90:
            bound_text += f"{i[0]} {i[1]},"
        else:
            raise Exception(f"Limits point {counter} = {i} is not within bounds of latitude and longitude")
    bound_text += f"{bounds[0][0]} {bounds[0][1]}"
    return bound_text


# This returns a list of length of the specified rows
# Each item in list is dictionary with details returned from the query
# dict_keys(['title', 'link', 'id', 'summary', 'ondemand', 'date', 'int', 'str'])
def sentinel5_query(satellite, product, limits, rows):
    list_of_results = []
    pages, remains = rows // 100, rows % 100
    for x in range(pages):
        url = f'https://s5phub.copernicus.eu/dhus/search?q= instrumentshortname:{satellite} AND ' \
              f'producttype:{product} AND ' \
              f'( footprint:"Intersects(POLYGON(({limits})))"' \
              f')&rows={100}&start={x * 100}'
        query = requests.get(url, auth=('s5pguest', 's5pguest'))
        a = xmltodict.parse(query.text)['feed']['entry']
        for i in a:
            list_of_results.append({"title": i['title'], "link": i['link'][0]['@href']})
    if remains:
        url = f'https://s5phub.copernicus.eu/dhus/search?q= instrumentshortname:{satellite} AND ' \
              f'producttype:{product} AND ' \
              f'( footprint:"Intersects(POLYGON(({limits})))"' \
              f')&rows={remains}&start={pages * 100}'
        query = requests.get(url, auth=('s5pguest', 's5pguest'))
        a = xmltodict.parse(query.text)['feed']['entry']
        if remains > 1:
            for i in a:
                list_of_results.append({"title": i['title'], "link": i['link'][0]['@href']})
        else:
            list_of_results.append({"title": a['title'], "link": a['link'][0]['@href']})
    return list_of_results


def download_tropomi_file(query_item, output_folder):
    if os.path.isdir(output_folder):
        pass
    else:
        os.mkdir(output_folder)
    current_archive = os.listdir(output_folder)

    download_link = query_item['link']
    response = requests.get(download_link, auth=('s5pguest', 's5pguest'), stream=True)
    file_name = query_item['title'] + ".nc"
    if file_name in current_archive:
        print(file_name, "already downloaded.")
    else:
        with open(output_folder + "/" + file_name, "wb") as f:
            print(file_name, "downloading:")
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        print()
    return


if __name__ == "__main__":
    main()
