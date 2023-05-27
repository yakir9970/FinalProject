<template>
  <div class='collapsible-tidy-tree' id='tree-content'>
    <svg id='tree-content-svg' :width='width' :height='height'></svg>
  </div>
</template>

<script>
import * as d3 from 'd3';
import _ from 'lodash';

export default {
  name: 'CollapsibleTidyTree',
  props: {
    data: {
      type: Object,
      required: true,
    },
    width: {
      default: 2000,
      type: Number,
    },
    height: {
      default: 1000,
      type: Number,
    },
    offsetTop: {
      default: 20,
      type: Number,
    },
    offsetLeft: {
      default: 190,
      type: Number,
    },
    offsetRight: {
      default: 90,
      type: Number,
    },
    offsetBottom: {
      default: 30,
      type: Number,
    },
  },
  data() {
    return {
      treemap: null,
      objectsGroup: null,
      duration: 750,
      root: null,
      i: 0,
      zoom: null,
    };
  },
  mounted() {
    if (!_.isEmpty(this.data)) {
      this.buildChart();
    }
  },

  methods: {
    buildChart() {
      // Set the dimensions and margins of the diagram
      const width = this.width - this.offsetLeft - this.offsetRight;
      const height = this.height - this.offsetTop - this.offsetBottom;

      const svg = d3.select('#tree-content-svg');
      svg.selectAll('*').remove();
      this.objectsGroup = svg.append('g').attr('transform', `translate(${ this.offsetLeft },${ this.offsetTop })`);

      // declares a tree layout and assigns the size
      this.treemap = d3.tree().size([height, width]);

      // Assigns parent, children, height, depth
      this.root = d3.hierarchy(this.data, d => d.children);
      this.root.x0 = height / 2;
      this.root.y0 = 0;

      // create zoom
      this.zoom = d3.zoom()
        .scaleExtent([0.1, 3])
        .on('zoom', this.handleZoom);

      svg.call(this.zoom);
      this.updateTree(this.root);
    },
    // zoom and pan handler
    handleZoom(e) {
      this.objectsGroup
        .attr('transform', e.transform);
    },
    // Collapse the node and all it's children
    collapse(d) {
      if (d.children) {
        d._children = d.children;
        d._children.forEach(this.collapse);
        d.children = null;
      }
    },

    updateTree(source) {
      const levelWidth = [1];
      const childCount = (level, n) => {
        if (n.children && n.children.length > 0) {
          if (levelWidth.length <= level + 1) levelWidth.push(0);

          levelWidth[level + 1] += n.children.length;
          n.children.forEach(d => {
            childCount(level + 1, d);
          });
        }
      };
      childCount(0, this.root);
      const width = this.width - this.offsetLeft - this.offsetRight;
      const height = this.height - this.offsetTop - this.offsetBottom;
      const maxLevelWidth = d3.max(levelWidth);
      const newHeight = maxLevelWidth * d3.max([height / maxLevelWidth, 25]); // calculate pixels per line
      this.treemap = this.treemap.size([newHeight, width]);
      // Assigns the x and y position for the nodes
      const treeData = this.treemap(this.root);

      // Compute the new tree layout.
      const nodes = treeData.descendants();
      const links = treeData.descendants().slice(1);

      // Normalize for fixed-depth.
      nodes.forEach(d => {
        d.y = d.depth * 180;
      });

      // ****************** Nodes section ***************************

      // Update the nodes...
      const node = this.objectsGroup.selectAll('g.node')
        .data(nodes, d => {
          if (!d.id) {
            this.i += 1;
            d.id = this.i;
          }
          return d.id;
        });

      // Enter any new modes at the parent's previous position.
      const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr('transform', () => `translate(${ source.y0 },${ source.x0 })`)
        .on('click', this.click);

      // Add Circle for the nodes
      nodeEnter.append('circle')
        .attr('class', 'node')
        .attr('r', 1e-6);    
      // Add labels for the nodes
      nodeEnter.append('text')
        .attr('dy', d => d.data.children.length > 0 ? "-0.20em" : "0.25em")
        .attr('dx', d => d.data.children.length > 0 ? "-0.35em" : "0.35em")
        .attr('x', d => (d.children || d._children ? -13 : 13))
        .attr('text-anchor', d => (d.children || d._children ? 'end' : 'start'))
        .text(d => d.data.data)

      // Update
      const nodeUpdate = nodeEnter.merge(node);

      // Transition to the proper position for the node
      nodeUpdate.transition()
        .duration(this.duration)
        .attr('transform', d => `translate(${ d.y*3 },${ d.x})`);

      function colorizeNodes(node) {
        // set the color of the current node based on its parent
        if (node.parent && node.parent.data.color) {
          node.data.color = node.parent.data.color;
        }
        else {
          if (node.data.color) {
            node.data.color = node.data.color;
          }
        }

        // recursively set the colors of the children
        if (node.children) {
          node.children.forEach(colorizeNodes);
        }
        if (node._children) {
          node._children.forEach(colorizeNodes);
        }
      }

      // Call the function to colorize the nodes
      colorizeNodes(treeData);

      // Update the node attributes and style
      nodeUpdate.select('circle.node')
        .attr('r', 10)
        .style('fill', d => d.data.children.length > 0 ? (d.data.color || "#222222") : "#fff")
        .style('stroke', d => d.data.children.length > 0 ? (d.data.color || "#222222") : (d.data.color || "#222222"))
        .attr('cursor', 'pointer');

      // Remove any exiting nodes
      const nodeExit = node.exit().transition()
        .duration(this.duration)
        .attr('transform', () => `translate(${source.y},${source.x})`)
        .remove();

      // On exit reduce the node circles size to 0
      nodeExit.select('circle')
        .attr('r', 1e-6);

      // On exit reduce the opacity of text labels
      nodeExit.select('text')
        .style('fill-opacity', 1e-6);

      // ****************** links section ***************************

      // Update the links...
      const link = this.objectsGroup.selectAll('path.link')
        .data(links, d => d.id);

      // Enter any new links at the parent's previous position.
      const linkEnter = link.enter().insert('path', 'g')
        .attr('class', 'link')
        .attr('d', () => {
          const o = { x: source.x0, y: source.y0 };
          return this.diagonal(o, o);
        })

      // Update
      const linkUpdate = linkEnter.merge(link);

      // Transition back to the parent element position
      linkUpdate.transition()
        .duration(this.duration)
        .attr('d', d => this.diagonal(d, d.parent))

      // Remove any exiting links
      const linkExit = link.exit().transition()
        .duration(this.duration)
        .attr('d', () => {
          const o = { x: source.x, y: source.y };
          return this.diagonal(o, o);
        })
        .remove();

      // Store the old positions for transition.
      nodes.forEach(d => {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    },

    // Creates a curved (diagonal) path from parent to the child nodes
    diagonal(s, d) {
      const path = `M ${s.y*3} ${s.x}
              C ${(s.y + d.y*2) } ${s.x},
                ${(s.y + d.y*2) } ${d.x},
                ${d.y*3} ${d.x}`;

      return path;
    },

    // Toggle children on click.
    click(event, d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }
      this.updateTree(d);
    },
  },
  watch: {
    data: {
      async handler() {
        if (!_.isEmpty(this.data)) {
          this.treemap = null;
          this.objectsGroup = null;
          this.root = null;
          this.i = 0;
          this.zoom = null;
          this.buildChart();
        }
      },
      deep: true,
    },
  },
};
</script>

<style lang='scss'>
@import url('https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
.collapsible-tidy-tree {
  .node circle {
    stroke-width: 7px;
  }
  .link {
    fill: none;
    stroke: #ffffff;
    stroke-width: 2px;
  }
  .node text {
    font-weight: 700;
    font-family: 'Raleway', sans-serif;
    font-size: 20px;
  }
}

</style>
