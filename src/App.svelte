<script>
  import UserInputForm from './components/UserInputForm.svelte'
  import TreeVisualization from './components/TreeVisualization.svelte'
  import { treeData } from './stores/dataStore.js'

  let currentView = 'input' // 'input', 'tree'
  let start = ''
  let end = ''

  async function loadDailyPrompt() {
    try {
      const response = await fetch('/api/daily-prompt')
      if (response.ok) {
        let p = await response.text();
        [start, end] = p.split(',').map(part => part.trim())
      }
    } catch (error) {
      console.error('Failed to load daily prompt:', error)
    }
  }

  function handleInputSubmitted(event) {
    console.log('Navigating from input to tree')
    const { treeData: newTreeData } = event.detail
    if (newTreeData) {
      console.log('Received tree data:', newTreeData)
      treeData.set(newTreeData)
    }
    currentView = 'tree'
  }

  function handleGoBack() {
    console.log('Going back to input form')
    currentView = 'input'
  }

  loadDailyPrompt()
</script>

<main class="main-bg">
    {#if currentView === 'input'}
  <div class="container mx-auto">
        <UserInputForm 
          start={start} end={end}
          on:submitted={handleInputSubmitted}
        />
  </div>
    {:else if currentView === 'tree'}
    <div class="">
          <TreeVisualization on:goBack={handleGoBack} />
    </div>
      {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>
