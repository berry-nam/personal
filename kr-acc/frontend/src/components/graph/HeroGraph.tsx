import { useEffect, useRef, useCallback } from "react";
import * as d3 from "d3";
import type { GraphData } from "@/types/api";
import { getPartyColor } from "@/lib/partyColors";

interface HeroGraphProps {
  data: GraphData;
  selectedNodeId: string | null;
  onNodeClick: (nodeId: string, name: string, party: string | null) => void;
}

interface SimNode extends d3.SimulationNodeDatum {
  id: string;
  name: string;
  party: string | null;
}

interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  weight: number;
}

export default function HeroGraph({
  data,
  selectedNodeId,
  onNodeClick,
}: HeroGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null);

  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;

  const selectedRef = useRef(selectedNodeId);
  selectedRef.current = selectedNodeId;

  // Highlight selected node reactively
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);

    svg.selectAll<SVGCircleElement, SimNode>("circle.node").each(function (d) {
      const isSelected = d.id === selectedNodeId;
      d3.select(this)
        .attr("r", isSelected ? 10 : connectedWeight(d) > 0 ? 5 + Math.min(connectedWeight(d) * 0.3, 5) : 4)
        .attr("stroke", isSelected ? "#fff" : "none")
        .attr("stroke-width", isSelected ? 2.5 : 0);
    });

    svg
      .selectAll<SVGTextElement, SimNode>("text.node-label")
      .attr("opacity", (d) =>
        d.id === selectedNodeId ? 1 : 0,
      );

    // Dim unconnected nodes/links when something is selected
    if (selectedNodeId) {
      const connectedIds = new Set<string>();
      connectedIds.add(selectedNodeId);
      svg.selectAll<SVGLineElement, SimLink>("line.link").each(function (d) {
        const s = (d.source as SimNode).id;
        const t = (d.target as SimNode).id;
        if (s === selectedNodeId) connectedIds.add(t);
        if (t === selectedNodeId) connectedIds.add(s);
      });

      svg
        .selectAll<SVGCircleElement, SimNode>("circle.node")
        .attr("opacity", (d) => (connectedIds.has(d.id) ? 1 : 0.15));
      svg
        .selectAll<SVGLineElement, SimLink>("line.link")
        .attr("opacity", (d) => {
          const s = (d.source as SimNode).id;
          const t = (d.target as SimNode).id;
          return s === selectedNodeId || t === selectedNodeId ? 0.6 : 0.03;
        });
    } else {
      svg.selectAll<SVGCircleElement, SimNode>("circle.node").attr("opacity", 0.85);
      svg.selectAll<SVGLineElement, SimLink>("line.link").attr("opacity", 0.15);
    }
  }, [selectedNodeId]);

  // Track link weights per node for sizing
  const weightMapRef = useRef<Map<string, number>>(new Map());
  const connectedWeight = useCallback(
    (d: SimNode) => weightMapRef.current.get(d.id) ?? 0,
    [],
  );

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || data.nodes.length === 0)
      return;

    const rect = containerRef.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const nodes: SimNode[] = data.nodes.map((n) => ({ ...n }));
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const links: SimLink[] = data.edges
      .filter((e) => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map((e) => ({ source: e.source, target: e.target, weight: e.weight }));

    // Build weight map for node sizing
    const wm = new Map<string, number>();
    for (const l of links) {
      const s = typeof l.source === "string" ? l.source : (l.source as SimNode).id;
      const t = typeof l.target === "string" ? l.target : (l.target as SimNode).id;
      wm.set(s, (wm.get(s) ?? 0) + l.weight);
      wm.set(t, (wm.get(t) ?? 0) + l.weight);
    }
    weightMapRef.current = wm;

    const maxWeight = d3.max(links, (d) => d.weight) ?? 1;

    const simulation = d3
      .forceSimulation<SimNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<SimNode, SimLink>(links)
          .id((d) => d.id)
          .distance(60),
      )
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(10));

    simulationRef.current = simulation;

    // Defs for glow filter
    const defs = svg.append("defs");
    const filter = defs
      .append("filter")
      .attr("id", "glow")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");
    filter
      .append("feGaussianBlur")
      .attr("stdDeviation", "3")
      .attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Zoom
    const g = svg.append("g");
    svg.call(
      d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 6])
        .on("zoom", (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
          g.attr("transform", event.transform.toString());
        }),
    );

    // Links
    g.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("class", "link")
      .attr("stroke", "#4b5563")
      .attr("stroke-opacity", 0.15)
      .attr("stroke-width", (d) =>
        Math.max(0.5, (d.weight / maxWeight) * 3),
      );

    // Nodes
    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("class", "node")
      .attr("r", (d) => {
        const w = wm.get(d.id) ?? 0;
        return 4 + Math.min(w * 0.3, 6);
      })
      .attr("fill", (d) => getPartyColor(d.party))
      .attr("opacity", 0.85)
      .attr("filter", "url(#glow)")
      .style("cursor", "pointer")
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(drag(simulation) as any);

    // Labels (hidden by default, shown on hover/select)
    g.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .attr("class", "node-label")
      .text((d) => d.name)
      .attr("font-size", 10)
      .attr("font-weight", 600)
      .attr("dx", 10)
      .attr("dy", 3)
      .attr("fill", "#e5e7eb")
      .attr("opacity", 0)
      .attr("pointer-events", "none");

    // Hover & click
    node
      .on("mouseover", function (_event, d) {
        if (selectedRef.current && selectedRef.current !== d.id) return;
        d3.select(this).attr("r", 12).attr("stroke", "#fff").attr("stroke-width", 2);
        svg
          .selectAll<SVGTextElement, SimNode>("text.node-label")
          .filter((l) => l.id === d.id)
          .attr("opacity", 1);
      })
      .on("mouseout", function (_event, d) {
        if (selectedRef.current === d.id) return;
        const w = wm.get(d.id) ?? 0;
        d3.select(this)
          .attr("r", 4 + Math.min(w * 0.3, 6))
          .attr("stroke", "none");
        svg
          .selectAll<SVGTextElement, SimNode>("text.node-label")
          .filter((l) => l.id === d.id)
          .attr("opacity", 0);
      })
      .on("click", (_event, d) => {
        onNodeClickRef.current(d.id, d.name, d.party);
      });

    simulation.on("tick", () => {
      svg
        .selectAll<SVGLineElement, SimLink>("line.link")
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0);

      svg
        .selectAll<SVGCircleElement, SimNode>("circle.node")
        .attr("cx", (d) => d.x ?? 0)
        .attr("cy", (d) => d.y ?? 0);

      svg
        .selectAll<SVGTextElement, SimNode>("text.node-label")
        .attr("x", (d) => d.x ?? 0)
        .attr("y", (d) => d.y ?? 0);
    });

    return () => {
      simulation.stop();
    };
  }, [data]);

  return (
    <div ref={containerRef} className="h-full w-full">
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        className="cursor-grab active:cursor-grabbing"
      />
    </div>
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
