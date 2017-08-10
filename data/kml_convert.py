""" Convert vicroads kml data to json, csv """


import argparse
import json
import xml.etree.ElementTree as etree


def main():
    args = parse_args()
    if args.out.endswith('.json'):
        kml_2_json(args.kml, args.out)
    elif args.out.endswith('.csv'):
        print('csv output not implemented')
    else:
        print('unknown output extension')


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('kml', help='vicroads kml data file')
    parser.add_argument('out', help='output path. Format determined by output extension')
    if args is None:
        return parser.parse_args()
    else:
        return parser.parse_args(args)


def kml_2_json(kml_path, json_path):
    placemarks = kml_2_placemarks(kml_path)
    placemarks_to_json(placemarks, json_path)


def kml_2_placemarks(kml_path):
    """ Parse vicroads kml into a list of Placemarks
        Returns: Placemark iterator
    """
    kmltree = etree.parse(kml_path).getroot()

    for p in kmltree.iter('Placemark'):
        yield placemark_e2obj(p)


def placemarks_to_json(placemarks, outpath):
    """ Write placemarks to json file """
    placemark_dicts = [p.to_jsondict() for p in placemarks]
    with open(outpath, 'w') as ofile:
        # indent \t saves MBs over spaces
        # and funnily enough loads much quicker in sublime than
        # single-line json
        json.dump(placemark_dicts, ofile, indent='\t')


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
    for xy in text.split():
        x, y = xy.split(',')
        yield Point(float(x), float(y))


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
        self.lat = lat
        self.lon = lon


if __name__ == '__main__':
    main()