<script>
  import { createEventDispatcher } from 'svelte'
  
  export let prompt = ''
  
  const dispatch = createEventDispatcher()
  
  function proceedToInput() {
    dispatch('complete')
  }
</script>

<div class="card-elevated animate-fade-in">
  <div class="card-body text-center">
    <h2 class="text-2xl font-semibold color-brand-800 mb-6">Today's Prompt</h2>
    
    {#if prompt}
      <div class="status-success mb-8">
        <p class="text-lg leading-relaxed">
          {prompt}
        </p>
      </div>
    {:else}
      <div class="bg-gray-50 p-6 mb-8 rounded animate-pulse">
        <div class="loading-spinner w-6 h-6 mx-auto mb-2"></div>
        <p class="color-brand-500">Loading today's prompt...</p>
      </div>
    {/if}
    
    <div class="space-y-4">
      <p class="color-brand-600">
        When you're ready, you'll write a response that will be added to our semantic tree.
      </p>
      
      <button 
        class="btn-primary"
        on:click={proceedToInput}
        disabled={!prompt}
      >
        I'm Ready to Respond
      </button>
    </div>
  </div>
</div>
