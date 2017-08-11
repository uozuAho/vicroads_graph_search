""" Convert vicroads kml data to json, csv """


import argparse
import csv
import json
import xml.etree.ElementTree as etree


def main():
    args = parse_args()
    placemarks = kml_2_placemarks(args.kml, args.limit)
    if args.out.endswith('.json'):
        placemarks_to_json(placemarks, args.out, args.pretty)
    elif args.out.endswith('.csv'):
        placemarks_2_csv(placemarks, args.out)
    elif args.out.endswith('.js'):
        placemarks_to_js(placemarks, args.out, args.pretty)
    else:
        print('unknown output extension')


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('kml', help='vicroads kml data file')
    parser.add_argument('out', help='output path. Format determined by output extension')
    parser.add_argument('-l', '--limit', type=int, help='limit the numer of output placemarks')
    parser.add_argument('-p', '--pretty', action='store_true', help='pretty print (js(on) only)')
    if args is None:
        return parser.parse_args()
    else:
        return parser.parse_args(args)


def placemarks_2_csv(placemarks, csv_path):
    """ convert vicroads kml data file to csv file """
    with open(csv_path, 'w') as csvfile:
        fieldnames = ['declared_name', 'lat', 'lon']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for placemark in placemarks:
            for point in placemark.points:
                writer.writerow({"declared_name": placemark.declared_name,
                                 "lat": point.lat, "lon": point.lon})


def kml_2_placemarks(kml_path, limit=None):
    """ Parse vicroads kml into a list of Placemarks
        Returns: Placemark iterator
    """
    kmltree = etree.parse(kml_path).getroot()

    i = 0
    for p in kmltree.iter('Placemark'):
        i += 1
        if limit and i > limit:
            break
        yield placemark_e2obj(p)


def placemarks_to_json(placemarks, outpath, pretty=False):
    """ Write placemarks to json file """
    with open(outpath, 'w') as ofile:
        ofile.write(placemarks_to_json_str(placemarks, pretty))


def placemarks_to_json_str(placemarks, pretty=False):
    """ Return list of placemarks as a json string """
    placemark_dicts = [p.to_jsondict() for p in placemarks]
    indent = '\t' if pretty else None
    return json.dumps(placemark_dicts, indent=indent)


def placemarks_to_js(placemarks, outpath, pretty=False, var_name='roads_data'):
    """ Write list of placemarks to a js variable in a file """
    with open(outpath, 'w') as ofile:
        ofile.write('let {} = '.format(var_name))
        ofile.write(placemarks_to_json_str(placemarks))


def placemark_e2obj(placemark):
    """ Convert a placemark xml element to a python object """
    pm = Placemark()
    for sd in placemark.iter('SimpleData'):
        if sd.attrib['name'] == 'DECLARED':
            pm.declared_name = sd.text
        elif sd.attrib['name'] == 'ROADNAME':
            pm.road_name = sd.text
        elif sd.attrib['name'] == 'LOCALNAME':
            pm.local_name = sd.text
    for coords in placemark.iter('coordinates'):
        if len(pm.points) > 0:
            raise Exception('more than one coordinate set in placemark with declared name: ' + pm.declared_name)
        pm.points = list(coords_text_to_points(coords.text))
    return pm


def coords_text_to_points(text):
    """ Convert a list of coordinates (kml linestring) to a Point iterator """
    for lonlat in text.split():
        lon, lat = lonlat.split(',')
        yield Point(lat=lat, lon=lon)


class Placemark(object):
    """ Vicroads kml 'placemark' object """
    def __init__(self, declared_name=None, points=[]):
        self.declared_name = declared_name
        self.points = points
        self.road_name = None
        self.local_name = None
        self.alt_name = None
        self.alt_2_name = None

    def to_jsondict(self):
        return {
            "declared_name": self.declared_name,
            "points": [(p.lat, p.lon) for p in self.points]
        }

    def __str__(self):
        return "placemark: '{}', '{}', '{}', pts: {}".format(
            self.declared_name, self.road_name, self.local_name,
            len(self.points))

class Point:
    def __init__(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)


if __name__ == '__main__':
    main()