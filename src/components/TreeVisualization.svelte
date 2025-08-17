<script>
  import { createEventDispatcher, onMount, onDestroy, tick } from 'svelte'
  import { treeData } from '../stores/dataStore.js'
  import * as d3 from 'd3'
    import { scale } from 'svelte/transition';
  
  const dispatch = createEventDispatcher()
  
  let svgElement
  let isLoading = true
  let errorMessage = ''
  let mounted = false
  let cameraSequencesRun = 0;
  let summaryCardCollapsed = false;
  const width = 800;
  const height = 600;

  // Reactive computed values for summary card
  $: totalNodes = $treeData ? $treeData.nodes.length : 0;
  $: userNode = $treeData ? $treeData.nodes.find(d => d.isUser) : null;
  $: userText = userNode ? userNode.id : '';
  $: currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  onMount(async () => {
    mounted = true
    // Check if we already have tree data from the store
    if ($treeData && mounted) {
      isLoading = false
      await tick() // Wait for DOM to update
      renderTree()
    } else {
      console.log('🔴 TreeVisualization: No tree data available, waiting for store update')
    }
  })

  // React to changes in treeData store
  $: if ($treeData && mounted) {
    isLoading = false
    tick().then(() => renderTree()) // Wait for DOM update before rendering
  }
  function calcScaleTranslateForGroup(group, zoomLevel){
      const xExtent = d3.extent(group, d => d.x)
      const yExtent = d3.extent(group, d => d.y)
      
      const padding = 100
      const groupWidth = xExtent[1] - xExtent[0] + padding * 2
      const groupHeight = yExtent[1] - yExtent[0] + padding * 2
      const centerX = (xExtent[0] + xExtent[1]) / 2
      const centerY = (yExtent[0] + yExtent[1]) / 2

      const fitScale = Math.min(
        width / groupWidth,
        height / groupHeight
      )
      const groupScale = fitScale * zoomLevel
      const groupTranslate = [
        width / 2 - groupScale * centerX,
        height / 2 - groupScale * centerY
      ]
      console.log(`[calcScaleTranslate] ${groupScale} ${groupTranslate}`)
      return [groupScale, groupTranslate];
  }
  function getRootToUserNodes(){
    let otherNodes = []
    let nextLinkArray = $treeData.links.filter(link => link.target.isUser == true)
    //while userNode is not rootNode: find link with Root as target
    while(nextLinkArray.length > 0) {
      let nextLink = nextLinkArray[0]
      let nextNode = nextLink.source;
      if(nextNode.isRoot){break}
      otherNodes.unshift(nextNode)
      nextLinkArray = $treeData.links.filter(link => link.target.id == nextNode.id)
    }
    console.log('[other nodes] ', otherNodes)
    return otherNodes
  }
  function renderTree() {
    if (!svgElement || !$treeData) {
      console.log('🔴 TreeVisualization: SVG element or tree data not available', { svgElement: !!svgElement, treeData: !!$treeData })
      return
    }
    console.log('🔴 TreeVisualization: Rendering tree with data:', $treeData)
    // Clear any existing content
    d3.select(svgElement).selectAll("*").remove()
    
    const svg = d3.select(svgElement)
    
    svg.attr("width", width).attr("height", height)
    
    const g = svg.append("g")
    
    // Set up zoom and pan
    //pass transform style from calculated event.transform
    const zoom = d3.zoom()
      .scaleExtent([0.1, 10])
      .on("zoom", (event) => {
        g.attr("transform", event.transform)
      })
    
    svg.call(zoom)
    
    // Create force simulation with collision detection for label spacing
    const simulation = d3.forceSimulation($treeData.nodes)
      .force("link", d3.forceLink($treeData.links).id(d => d.id).distance(d => d.distance * 300))
      .force("charge", d3.forceManyBody().strength(-180))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => {
        // Increase effective node size based on label length and type
        const textLength = d.name ? d.name.length : 0;
        const textMultiplier = d.isLeaf ? 2 : 1; // Leaf nodes have larger text
        return textLength * textMultiplier + 7;
      }).strength(0.3))
      .alphaDecay(0.03)    
      .velocityDecay(0.4)  
    
    // Draw nodes
    // Draw links
    const link = g.append("g")
      .selectAll("line")
      .data($treeData.links)
      .join("line")
      .attr("stroke", "var(--color-newspaper-brown-light)")  // Sepia brown for lines
      .attr("stroke-opacity", 0.8)
      .attr("stroke-width", 1)
    
    // Draw nodes
    const node = g.append("g")
      .selectAll("circle")
      .data($treeData.nodes)
      .join('circle')
      .attr('r', d => d.isLeaf ? 4 : 3)
      .attr('fill', d => d.isUser ? 'var(--color-tree-leaf)' : 'var(--color-newspaper-brown-light)')
      .attr('stroke', 'var(--color-newspaper-brown-dark)')
      .attr('stroke-width', 0)
      .style('cursor', 'pointer')
      .call(drag(simulation))

    // Draw labels - default to brown-light; make interactive so hover works
    const label = g.append('g')
      .selectAll('text')
      .data($treeData.nodes)
      .join('text')
      .text(d => d.name)
      .attr('font-size', d => d.isLeaf ? '0.875rem' : '0.625rem')
      .attr('fill', d => d.isUser ? 'var(--color-tree-leaf)' : 'var(--color-newspaper-brown-light)')
      .attr('dy', d => d.isLeaf ? '1.5em' : '-0.7em')
      .style('pointer-events', 'auto')
      .style('font-style', d => d.isLeaf ? 'normal' : 'italic')
      .style('font-weight', d => d.isLeaf ? '600' : '500')
      .call(drag(simulation))
    
    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)
      
      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
      
      label
        .attr("x", d => d.x)
        .attr("y", d => d.y)
    })

    // Hover interactions: when hovering node or label, make label brown-dark
    label.on('mouseover', function(event, d) {
        d3.select(this).attr('fill', 'var(--color-newspaper-brown-dark)')
        node.filter(n => n.id === d.id).attr('fill', 'var(--color-newspaper-brown-dark)')
      })
      .on('mouseout', function(event, d) {
        d3.select(this).attr('fill', 'var(--color-newspaper-brown-light)')
        node.filter(n => n.id === d.id).attr('fill', 'var(--color-newspaper-brown-light)')
      })

    node.on('mouseover', function(event, d) {
        label.filter(l => l.id === d.id).attr('fill', 'var(--color-newspaper-brown-dark)')
        node.filter(n => n.id === d.id).attr('fill', 'var(--color-newspaper-brown-dark)')
      })
      .on('mouseout', function(event, d) {
        label.filter(l => l.id === d.id).attr('fill', 'var(--color-newspaper-brown-light)')
        node.filter(n => n.id === d.id).attr('fill', 'var(--color-newspaper-brown-light)')
      })

    simulation.on("end", async () => {
      if(cameraSequencesRun > 1){
        return
      } 
      cameraSequencesRun++;
      await zoomToRoot(2000, 500);
      let rootToUserNodes = getRootToUserNodes();
      const userNode = $treeData.nodes.find(d => d.isUser)
      for (let i = 0; i < rootToUserNodes.length; i++){
        await panToNode(rootToUserNodes[i], 800, 0);
      }
      await panToNode(userNode, 1000, 1000);
      console.log('[onEnd] fitting all in View')
      await fitToView(2000);
    })

    //First, zoom to the root node.
    //svg is global drawn obj.
    function zoomToRoot(durationMs, pauseMs){
         console.log('[zoomToRoot]')
        return new Promise((resolve) => {
          const rootNode = $treeData.nodes.find(d => d.isRoot)
          //get ids of targetroot and sourceroot
          const rootNeighbors = $treeData.links.filter(link => 
          link.source.id === rootNode.id || link.target.id === rootNode.id)
          .map(link => link.source.id === rootNode.id ? link.target : link.source)
          const rootGroup = [rootNode]
          const [rootScale, rootTranslate] = calcScaleTranslateForGroup(rootGroup, 1);
          svg.transition() //what does this call do?
          .duration(durationMs)
          .call(zoom.transform, 
          d3.zoomIdentity.translate(rootTranslate[0], rootTranslate[1]).scale(rootScale))
          .on("end", () => {
            setTimeout(resolve, pauseMs)
          })
        })
    }

    //Then, pan to the user node, no change in zoom
    function panToNode(node, durationMs, pauseMs){
      return new Promise((resolve) => {
        const currentTransform = d3.zoomTransform(svg.node())
        const targetX = width / 2 - currentTransform.k * node.x
        const targetY = height / 2 - currentTransform.k * node.y
        console.log('[panToNode] node:', node.id)
        svg.transition()
        .duration(durationMs)
        .ease(d3.easeCubicInOut)
        .call(zoom.transform, d3.zoomIdentity.translate(targetX, targetY).scale(currentTransform.k))
        .on("end", () => {
          setTimeout(resolve, pauseMs)
        })
      })
    }
  //fit the entire tree in view.
  function fitToView(durationMs) {
    console.log('[fitToView]')
    return new Promise((resolve) => {
      // Calculate bounds from actual node positions
      const nodePositions = $treeData.nodes.map(d => ({ x: d.x, y: d.y }))
      const [nodesScale, nodesTranslate] = calcScaleTranslateForGroup(nodePositions, 1);
      
      svg.transition()
        .duration(durationMs)
        .ease(d3.easeCircleOut)
        .call(zoom.transform, d3.zoomIdentity.translate(nodesTranslate[0], nodesTranslate[1]).scale(nodesScale))
        .on("end", resolve)
    })
  }
    
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        event.subject.fx = event.subject.x
        event.subject.fy = event.subject.y
      }
      
      function dragged(event) {
        event.subject.fx = event.x
        event.subject.fy = event.y
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0)
        event.subject.fx = null
        event.subject.fy = null
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    }
  }
</script>

<div class="tree-container">
  <div class="relative" style="height: 100vh; width: 100vw">
    {#if isLoading}
      <div class="absolute inset-0 flex items-center justify-center" style="background: var(--color-newspaper-parchment);">
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-4" style="border-color: var(--color-newspaper-brown);"></div>
          <p class="loading-text">Generating phylogenetic tree...</p>
        </div>
      </div>
    {:else if errorMessage}
      <div class="absolute inset-0 flex items-center justify-center" style="background: var(--color-newspaper-parchment);">
        <div class="text-center">
          <p class="error-text mb-4">{errorMessage}</p>
          <button
            class="btn-primary"
            on:click={() => dispatch('goBack')}
          >
            Go Back to Form
          </button>
        </div>
      </div>
    {:else}
      <svg bind:this={svgElement} class="w-full h-full cursor-grab"></svg>
        <div class="absolute bottom-12 right-8 border rounded-lg shadow-lg max-w-xs z-10" style="background: var(--color-newspaper-parchment); border-color: var(--color-newspaper-brown-light);">
        <!-- Card Header - Always Visible -->
        <button 
          type="button"
          class="w-full flex items-center justify-between p-3 cursor-pointer hover:bg-opacity-80 rounded-t-lg transition-colors duration-200"
          on:click={() => summaryCardCollapsed = !summaryCardCollapsed}
          aria-expanded={!summaryCardCollapsed}
          aria-controls="summary-card-content"
        >
          <h3 class="text-sm font-semibold" style="color: var(--color-newspaper-brown-dark);">Tree Summary</h3>
          <div class="transform transition-transform duration-200 {summaryCardCollapsed ? 'rotate-0' : 'rotate-180'}">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-newspaper-brown);">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
            </svg>
          </div>
        </button>
        
        <!-- Card Content - Collapsible -->
        {#if !summaryCardCollapsed}
          <div id="summary-card-content" class="p-3 space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="font-medium" style="color: var(--color-newspaper-ink);">{currentDate}</span>
            </div>
            <div class="flex justify-between">
              <span style="color: var(--color-newspaper-brown);">Total Nodes:</span>
              <span class="font-medium" style="color: var(--color-newspaper-ink);">{totalNodes}</span>
            </div>
            <div class="border-t pt-2" style="border-color: var(--color-newspaper-brown-light);">
              <div class="mb-1" style="color: var(--color-newspaper-brown);">User Input:</div>
              <div class="font-medium break-words text-xs p-2 rounded" style="color: var(--color-newspaper-ink); background: var(--color-newspaper-parchment);">
                {userText || 'No user input found'}
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
  <div class="tree-legend p-2">
    <div class="flex items-center justify-center gap-6 text-sm">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full" style="background: var(--color-tree-leaf);"></div>
        <span>Leaf nodes (sentences)</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full" style="background: var(--color-tree-internal);"></div>
        <span>Internal nodes</span>
      </div>
      <div class="text-xs">
        Drag nodes to rearrange • Scroll to zoom • Click and drag to pan
      </div>
    </div>
  </div>
</div>
