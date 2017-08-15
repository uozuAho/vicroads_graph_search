""" Convert vicroads kml data to json, csv, js """


import argparse
import csv
import json
import xml.etree.ElementTree as etree

import placemark_graph


def main():
    args = parse_args()
    placemarks = kml_2_placemarks(args.kml, args.limit)
    if args.bbox:
        placemarks = filter_placemarks_bbox(placemarks, args.bbox)
    if args.out.endswith('.json'):
        placemarks_to_json(placemarks, args.out, args.pretty)
    elif args.out.endswith('.csv'):
        placemarks_2_csv(placemarks, args.out)
    elif args.out.endswith('.graph.js'):
        placemarks_to_js_graph(placemarks, args.out, args.pretty)
    elif args.out.endswith('.js'):
        placemarks_to_js(placemarks, args.out, args.pretty)
    else:
        print('unknown output extension')


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Convert vicroads kml data to csv, js, json')
    parser.add_argument('kml', help='vicroads kml data file')
    parser.add_argument('out', help='output path. Format determined by output extension')
    parser.add_argument('-l', '--limit', type=int, help='limit the numer of output placemarks')
    parser.add_argument('-p', '--pretty', action='store_true', help='pretty print (js(on) only)')
    parser.add_argument('-b', '--bbox', type=float, nargs=4,
                        help='bounding box: [lat lon lat lon]. Points outside this box are removed')
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
        ofile.write(placemarks_to_json_str(placemarks, pretty))

def placemarks_to_js_graph(placemarks, outpath, pretty=False, var_name='roads_graph'):
    """ Write a js data variable of nodes and edges:
        {'nodes': [(lat, lon), ...], 'edges': [(0, 1), (1, 0), ...]}
    """
    nodes = placemark_graph.placemarks_to_graph(placemarks)
    graph = {'nodes': [], 'edges': []}
    node_idx = 0
    for node in nodes:
        graph['nodes'].append(node.xy)
        for a in node.adjacent:
            graph['edges'].append((node_idx, a))
        node_idx += 1
    with open(outpath, 'w') as ofile:
        ofile.write('let {} = '.format(var_name))
        indent = '\t' if pretty else None
        ofile.write(json.dumps(graph, indent=indent))


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


def filter_placemarks_bbox(placemarks, bbox):
    """ Remove points outside the bbox. If a placemark has no points, it is removed.
        bbox: [lat, lon, lat, lon]
    """
    maxlat = max(bbox[0], bbox[2])
    minlat = min(bbox[0], bbox[2])
    maxlon = max(bbox[1], bbox[3])
    minlon = min(bbox[1], bbox[3])
    for p in placemarks:
        p.points = list(filter_points_bbox(p.points, minlat, maxlat, minlon, maxlon))
        if len(p.points) > 0:
            yield p


def filter_points_bbox(points, minlat, maxlat, minlon, maxlon):
    """ Yield points within the given bounds """
    for p in points:
        if p.lat >= minlat and p.lat < maxlat and p.lon >= minlon and p.lon < maxlon:
            yield p


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
    """ A 2D (latitude, longitude) point """
    def __init__(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)


if __name__ == '__main__':
    main()