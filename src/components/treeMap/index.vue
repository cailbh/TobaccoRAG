<!-- tree map -->
<template>
  <div id="treeMap">

  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  data() {
    return {
      treeData: {},
    }
  },
  props: {
    treedata: Object,
  },
  methods: {
    treeDataUpdate(pre, val) {
      this.drawTree(val)
    },
    drawTree(data) {
      console.log("Tree data", data)
      const format = d3.format(",");
      const nodeSize = 17;
      const root = d3.hierarchy(data).eachBefore((i => d => d.index = i++)(0));
      const nodes = root.descendants();
      const width = document.getElementById("treeMap").offsetWidth;
      // const height = (nodes.length + 1) * nodeSize;
      const height = document.getElementById("treeMap").offsetHeight

      const svg = d3.select("#treeMap")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-nodeSize / 2, -nodeSize * 3 / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif; overflow: visible;");

      const link = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", "#999")
        .selectAll()
        .data(root.links())
        .join("path")
        .attr("d", d =>
          `
        M${d.source.depth * nodeSize},${d.source.index * nodeSize}
        V${d.target.index * nodeSize}
        h${nodeSize}
          `
        );

      const node = svg.append("g")
        .selectAll()
        .data(nodes)
        .join("g")
        .attr("transform", d => `translate(0,${d.index * nodeSize})`);

      node.append("circle")
        .attr("cx", d => d.depth * nodeSize)
        .attr("r", 2.5)
        .attr("fill", d => d.children ? null : "#999");

      node.append("text")
        .attr("dy", "0.32em")
        .attr("x", d => d.depth * nodeSize + 6)
        .text(d => d.data.name);

      node.append("title")
        .text(d => d.ancestors().reverse().map(d => d.data.name).join("/"));
    }
  },
  watch: {
  }
}
</script>

<style scoped>
@import './index.css';
</style>
