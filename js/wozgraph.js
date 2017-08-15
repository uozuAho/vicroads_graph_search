/** Assumes road data is loaded into a variable named roads_data
 */

/**
 * Create nodes and edges from vicroads json data
 * @param {object[]} roads_data
 * @returns [Node[], edges: [[idx1, idx2]]]
 */
function vicroadsNodesAndEdges(roads_data) {
  let nodes = [], 
      edges = [];
  for (let i = 0; i < roads_data.length; i++) {
    let points = roads_data[i].points;
    for (let j = 0; j < points.length; j++) {
      let point = points[j];
      // push each road point into the graph as a node (lon, lat coords)
      nodes.push(new Node(i, point[1], point[0]));
      if (j > 0) {
        // add edges between points on same road
        let lastidx = nodes.length - 1;
        let node1 = nodes[lastidx];
        let node2 = nodes[lastidx - 1];
        node1.adjacent.push[lastidx - 1];
        node2.adjacent.push[lastidx];
        edges.push([lastidx, lastidx - 1]);
      }
    }
  }
  return {nodes: nodes, edges: edges};
}

/** Convert the variable output by my python placemarks_to_js_graph
 *  function to a graph expected by the plotting stuff. Yeah. Great docs.
 */
function pyGraphToNodesAndEdges(roads_graph) {
  let nodes = [];
  for (let i = 0; i < roads_graph.nodes.length; i++) {
    nodes.push(new Node(i, ...roads_graph.nodes[i]))
  }
  return {nodes: nodes, edges: roads_graph.edges};
}

/** Scale nodes' x,y values to fit in box of size h,w. Maintain aspect ratio */
function scaleNodesToFit(nodes, height, width) {
  let minx = 999;
  let miny = 999;
  let maxx = -999;
  let maxy = -999;
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].x < minx)
      minx = nodes[i].x;
    if (nodes[i].y < miny)
      miny = nodes[i].y;
    if (nodes[i].x > maxx)
      maxx = nodes[i].x;
    if (nodes[i].y > maxy)
      maxy = nodes[i].y;
  }
  let scalex = width / (maxx - minx);
  let scaley = height / (maxy - miny);
  // want to maintain aspect ratio, so use the minimum x/y scale factor
  let scale = Math.min(scalex, scaley);
  console.log('minx: ' + minx);
  console.log('maxx: ' + maxx);
  console.log('miny: ' + miny);
  console.log('maxy: ' + maxy);
  console.log('scale: ' + scale);
  for (let i = 0; i < nodes.length; i++) {
    let node = nodes[i];
    node.x = (node.x - minx) * scale;
    // invert y since display y is inverted
    node.y = height - (node.y - miny) * scale;
  }
}

class WozGraph {
  constructor(nodes, edges) {
    this.nodes = nodes;
    this.edges = edges;
  }

  getAdjacent(id) {
    return this.nodes[id].adjacent;
  }
}

$(document).ready(function() {
  let height = 500;
  let width = 1100;
  // let ne = vicroadsNodesAndEdges(roads_data);
  let ne = pyGraphToNodesAndEdges(roads_graph);
  console.log('nodes: ' + ne.nodes.length);
  scaleNodesToFit(ne.nodes, height, width);
  let x = ne.nodes[0].x;
  let y = ne.nodes[0].y;
  console.log(`node 1 x,y: ${x}, ${y}`);
  let graph = new WozGraph(ne.nodes, ne.edges);
  let problem = new BidirectionalProblem(graph);
  let vicDiagram = new BFSDiagram(d3.select('#vicroads_div').select('#vicCanvas'), height, width);
  vicDiagram.init(problem, d3.select('#vicroads_div').select('#vicStepCount'));
});