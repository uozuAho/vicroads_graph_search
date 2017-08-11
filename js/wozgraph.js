/** Assumes road data is loaded into a variable named roads_data
 */

// scale latitude to fit in 500x500 grid
function latToY(lat) {
  return 500 - (lat + 39.0307555294734) * 56.91535750124111;
}

// scale longitude to fit in 500x500 grid
function lonToX(lon) {
  return (lon - 140.963092910004) * 56.91535750124111;
}

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
      // push each road point into the graph as a node
      nodes.push(new Node(i, lonToX(point[1]), latToY(point[0])));
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
  let ne = vicroadsNodesAndEdges(roads_data);
  console.log('nodes: ' + ne.nodes.length);
  let lat = ne.nodes[0].y;
  let lon = ne.nodes[0].x;
  console.log(`node1 lat,lon: ${lat}, ${lon}`);
  let graph = new WozGraph(ne.nodes, ne.edges);
  let problem = new BidirectionalProblem(graph);
  let vicDiagram = new BFSDiagram(d3.select('#vicroads_div').select('#vicCanvas'), 600, 600);
  vicDiagram.init(problem, d3.select('#vicroads_div').select('#vicStepCount'));
});