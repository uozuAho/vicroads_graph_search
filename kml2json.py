import io
import json
import sys
import xml.etree.ElementTree as etree


def main():
    inpath = sys.argv[1]

    e = etree.parse(inpath).getroot()

    placemarks = []
    for p in e.iter('Placemark'):
        pobj = placemark_e2obj(p)
        placemarks.append(pobj.to_jsondict())

    with open('roads.json', 'w') as ofile:
        # indent \t saves MBs over spaces
        # and funnily enough loads much quicker in sublime than
        # single-line json
        json.dump(placemarks, ofile, indent='\t')


def placemark_e2obj(placemark):
    """ Convert a placemark element to a python object """
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
    for xy in text.split():
        x, y = xy.split(',')
        yield Point(float(x), float(y))


class Placemark:
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