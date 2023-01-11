import requests
import os

# This first section is just cataloguing all .nc filenames from the copernicus site that have CH4 data
Skip = 0  # Only a certain number of files can be queried at one time
whole_list = []
new_list = [1]
Data_Type = "CH4"  # Target dataset, currently have tested NO2 and CH4
Output_Folder = "archived_methane_data"

# Main function
sets=0
while len(new_list) != 0 and sets != 3: # Will run until there are no files in the query
    print(Skip)
    # The URL queries the site itself, and filters it in a suitable way
    url = "https://s5phub.copernicus.eu/dhus/odata/v1/Products?$filter=substringof(%27L2__"+Data_Type+"__%27,Name)&$orderby=Name&$select=Id,Name&$skip="+str(Skip)+"&$top=50"
    r = requests.get(url, auth=('s5pguest','s5pguest'))
    information = r.text

    new_list = []
    info_list = information.split("<")
    # Extracts just the filename from the queried data
    for x in range(len(info_list)):
        if str(info_list[x][0:5]) == "d:Id>":
            temp = str(info_list[x][5:])
        if str(info_list[x][0:7]) == "d:Name>":
            new_list += [[str(info_list[x][7:])+".nc",temp]]


    whole_list += new_list
    Skip += 50 #Ensures the next query is with 50 new files
    r.close()
    sets += 1

print(len(whole_list))

if os.path.isdir(Output_Folder):
    pass
else:
    os.mkdir(Output_Folder)

#Checks download directory for all files, if a file already exists it won't be downloaded
main_directory = os.getcwd()
os.chdir(Output_Folder)
Current = os.getcwd()
Files = os.listdir(Current)
os.chdir(main_directory + "\\" +Output_Folder)

#Downloads all files previously catalogued in sequence
for x in range(len(whole_list)):
    if whole_list[x][0] not in Files:
        url = "https://s5phub.copernicus.eu/dhus/odata/v1/Products('" + whole_list[x][1] + "')/$value"
        r = requests.get(url, auth=('s5pguest','s5pguest'))
        name = whole_list[x][0]
        print("Downloading: " + name)
        with open(name, 'wb') as out_file:
            out_file.write(r.content)
        r.close()
