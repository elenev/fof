import requests
import io
import zipfile
import re
from requests.exceptions import HTTPError

def filtersub(series_prefix, series_sector, series_instrument, series_type, frequency):
    return (series_prefix in ['FL', 'LM']) and frequency == 'Q'

def buffer_to_csv(infile, outfile, dictfile=None):
    
    # Write the header to the output file
    outfile.write("series_code,frequency,time_period,obs_value\n")
    
    if dictfile is not None:
        dictfile.write("series_code,sector,instrument,series_type,unit,currency,mult\n")

    isZ1 = False
    filter = False

    # Read and process each line from the input file
    for line in infile:
        if "<frb:DataSet" in line:
            isZ1 = 'id="Z1"' in line
        elif "<kf:Series" in line:
            series_prefix = re.search(r'SERIES_PREFIX="(.*?)"', line).group(1)
            frequency = re.search(r'FREQ="(.*?)"', line).group(1)
            series_name = re.search(r'SERIES_NAME="(.*?)"', line).group(1)
            series_code, frequency = series_name.split('.')

            filter = filtersub(series_prefix, '', '', '', frequency)

            if dictfile is not None and filter:
                currency = re.search(r'CURRENCY="(.*?)"', line).group(1)
                instrument = re.search(r'SERIES_INSTRUMENT="(.*?)"', line).group(1)
                sector = re.search(r'SERIES_SECTOR="(.*?)"', line).group(1)
                series_type = re.search(r'SERIES_TYPE="(.*?)"', line).group(1)
                unit = re.search(r'UNIT="(.*?)"', line).group(1)
                mult = re.search(r'UNIT_MULT="(.*?)"', line).group(1)
                dictfile.write(f"{series_code},{sector},{instrument},{series_type},{unit},{currency},{mult}\n")
            
        elif "<frb:Obs" in line and isZ1 and filter:
            obs_status = re.search(r'OBS_STATUS="(.*?)"', line).group(1)
            time_period = re.search(r'TIME_PERIOD="(.*?)"', line).group(1)
            obs_value = re.search(r'OBS_VALUE="(.*?)"', line).group(1)

            outfile.write(f"{series_code},{frequency},{time_period},{obs_value}\n")

def parse_fof(outpath='FRB_Z1.csv', 
              url='https://www.federalreserve.gov/datadownload/Output.aspx?rel=Z1&filetype=zip',
              dictfile=None):

    # Step 1: Download the zipped file into memory
    response = requests.get(url)
    if response.status_code == 200:
        zipped_file = io.BytesIO(response.content)

        # Step 2: Read the zipped file from memory
        with zipfile.ZipFile(zipped_file) as zf:
            # Assuming there's only one XML file in the zip archive
            xml_filenames = [name for name in zf.namelist() if name.endswith('.xml')]
            if not xml_filenames:
                raise FileNotFoundError("No XML file found in the zip archive.")
            
            xml_file_name = xml_filenames[0]  # Take the first XML file found
            with zf.open(xml_file_name) as xml_file, open(outpath, 'w', encoding='UTF-8') as outfile:
                # Wrap the binary file-like object with io.TextIOWrapper to treat it as text
                infile = io.TextIOWrapper(xml_file, encoding='UTF-8')

                # Step 3: Convert the XML file to CSV
                buffer_to_csv(infile, outfile, dictfile)
                    
    else:
        raise HTTPError("Failed to download the file. Status code:", response.status_code)