/** Assumes road data is loaded into a variable
 *  named roads_small
 */

/**
 * Create a graph from vicroads json data
 * @param {object[]} data
 * @returns [Node[], edges[]]
 */
function vicroadsGraph(data) {
  let nodes = [], 
      edges = [];
  for (let i = 0; i < data.length; i++) {
    let points = data[i].points;
    for (let j = 0; j < points.length; j++) {
      let point = points[j];
      nodes.push(new Node(i, point[0], point[1]));
    }
  }
  // todo: edges
  return [nodes, edges];
}

$(document).ready(function() {
  for (let i = 0; i < roads_small.length; i++) {
    console.log(roads_small[i].declared_name);
  }
});