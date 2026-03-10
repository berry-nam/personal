import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { GraphData } from "@/types/api";
import { getPartyColor } from "@/lib/partyColors";

interface ForceGraphProps {
  data: GraphData;
  width: number;
  height: number;
}

interface SimNode extends d3.SimulationNodeDatum {
  id: string;
  name: string;
  party: string | null;
}

interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  weight: number;
}

export default function ForceGraph({ data, width, height }: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const nodes: SimNode[] = data.nodes.map((n) => ({
      ...n,
      id: n.id,
      name: n.name,
      party: n.party,
    }));

    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const links: SimLink[] = data.edges
      .filter((e) => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map((e) => ({
        source: e.source,
        target: e.target,
        weight: e.weight,
      }));

    const maxWeight = d3.max(links, (d) => d.weight) ?? 1;

    const simulation = d3
      .forceSimulation<SimNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<SimNode, SimLink>(links)
          .id((d) => d.id)
          .distance(80),
      )
      .force("charge", d3.forceManyBody().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(12));

    // Zoom
    const g = svg.append("g");
    svg.call(
      d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 5])
        .on("zoom", (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
          g.attr("transform", event.transform.toString());
        }),
    );

    // Links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#d1d5db")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d) => Math.max(1, (d.weight / maxWeight) * 4));

    // Nodes
    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 6)
      .attr("fill", (d) => getPartyColor(d.party))
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(drag(simulation) as any);

    // Labels
    const label = g
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.name)
      .attr("font-size", 9)
      .attr("dx", 8)
      .attr("dy", 3)
      .attr("fill", "#374151");

    // Tooltip on hover
    node
      .on("mouseover", function (_event, d) {
        d3.select(this).attr("r", 10).attr("stroke-width", 2);
        label
          .filter((l) => l.id === d.id)
          .attr("font-weight", "bold")
          .attr("font-size", 12);
      })
      .on("mouseout", function (_event, d) {
        d3.select(this).attr("r", 6).attr("stroke-width", 1.5);
        label
          .filter((l) => l.id === d.id)
          .attr("font-weight", "normal")
          .attr("font-size", 9);
      });

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0);

      node.attr("cx", (d) => d.x ?? 0).attr("cy", (d) => d.y ?? 0);

      label.attr("x", (d) => d.x ?? 0).attr("y", (d) => d.y ?? 0);
    });

    return () => {
      simulation.stop();
    };
  }, [data, width, height]);

  return (
    <svg
      ref={svgRef}
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="cursor-grab active:cursor-grabbing"
    />
  );
}

function drag(
  simulation: d3.Simulation<SimNode, SimLink>,
): d3.DragBehavior<SVGCircleElement, SimNode, SimNode | d3.SubjectPosition> {
  return d3
    .drag<SVGCircleElement, SimNode>()
    .on("start", (event: d3.D3DragEvent<SVGCircleElement, SimNode, SimNode>) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    })
    .on("drag", (event: d3.D3DragEvent<SVGCircleElement, SimNode, SimNode>) => {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    })
    .on("end", (event: d3.D3DragEvent<SVGCircleElement, SimNode, SimNode>) => {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    });
}
