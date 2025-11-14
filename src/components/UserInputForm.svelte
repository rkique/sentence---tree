<script>
  import { createEventDispatcher, onDestroy } from "svelte";

  export let start = "";
  export let end = "";
  const dispatch = createEventDispatcher();

  let userResponse = "";
  let isSubmitting = false;
  let errorMessage = "";
  let isGrammatical = null;
  let perplexity = null;
  let grammarCheckTimeout;

  // Get current date in newspaper format
  function getNewspaperDate() {
    const now = new Date();
    const options = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return now.toLocaleDateString("en-US", options);
  }

  async function checkGrammaticality() {
    if (!userResponse.trim()) return;
    if (userResponse.trim() == "debug") {
      console.warn("input is debug, skipping grammar check");
      return;
    }
    //fetch grammaticality from API
    try {
      const response = await fetch("/api/check-grammar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: userResponse }),
      });

      if (response.ok) {
        const result = await response.json();
        isGrammatical = result.is_grammatical;
        perplexity = result.perplexity;
      }
    } catch (error) {
      console.error("Grammar check failed:", error);
    }
  }

  async function submitResponse() {
    if (!userResponse.trim()) {
      errorMessage = "Please enter a response";
      return;
    }
    //Here we clear the grammar check before submit-input API
    if (grammarCheckTimeout) {
      clearTimeout(grammarCheckTimeout);
      grammarCheckTimeout = null;
    }

    isSubmitting = true;
    errorMessage = "";

    try {
      const response = await fetch("/api/submit-input", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: userResponse }),
      });

      if (response.ok) {
        const result = await response.json();
        dispatch("submitted", { treeData: result.tree_data });
      } else {
        const error = await response.json();
        errorMessage = "Your sentence is not grammatical or exists already!";
      }
    } catch (error) {
      console.error("Submission failed:", error);
    } finally {
      //after await block
      isSubmitting = false;
    }
  }

  // onUserResponseTrue: set grammarCheck again
  $: if (userResponse) {
    clearTimeout(grammarCheckTimeout);
    grammarCheckTimeout = setTimeout(checkGrammaticality, 1000);
  }
</script>

<header class="text-center my-7">
  <h1 class="newspaper-title">sentence tree</h1>
      <div class="date-row">
      <div class="newspaper-date">{getNewspaperDate()}</div>
      <p class="newspaper-subtitle">A Collective Phylogenetics of Language</p>
      <div class="info-container">
        <svg
          class="info-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          role="img"
        >
          <!-- circle outline -->
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.6" fill="none" />
          <!-- vertical stem of 'i' -->
          <rect x="11" y="9" width="2" height="9" rx="1" fill="currentColor" />
          <!-- dot of the 'i' -->
          <circle cx="12" cy="7" r="1.2" fill="currentColor" />
        </svg>
        <div class="info-tooltip">
          Share your thoughts and see how they connect with others! Craft a unique response that expresses your perspective. Your answer will be visualized on a <em>phylogenetic tree</em> showing how different opinions branch and relate to each other.
        </div>
      </div>

      <style>
        .info-container {
          position: relative;
          display: inline-block;
        }
        
        .info-icon {
          cursor: help;
          color: #666;
          transition: color 0.2s;
        }
        
        .info-icon:hover {
          color: #333;
        }
        
        .info-tooltip {
          visibility: hidden;
          opacity: 0;
          position: absolute;
          top: 125%;
          left: 50%;
          transform: translateX(-50%);
          background-color: #333;
          color: white;
          text-align: center;
          padding: 12px;
          border-radius: 6px;
          width: 300px;
          z-index: 1000;
          transition: opacity 0.3s, visibility 0.3s;
          font-size: 14px;
          line-height: 1.4;
        }
        
        .info-tooltip::after {
          content: "";
          position: absolute;
          bottom: 100%;
          left: 50%;
          margin-left: -5px;
          border-width: 5px;
          border-style: solid;
          border-color: transparent transparent #333 transparent;
        }
        
        .info-container:hover .info-tooltip {
          visibility: visible;
          opacity: 1;
        }
      </style>
      <div class="newspaper-edition">Daily Edition • Vol. 1</div>
    </div>
</header>
<div class="mx-auto" style="min-height: calc(100vh - 18rem); display:flex; align-items:center; justify-content:center;">
  <div class="card-elevated animate-fade-in" style="width:100%;">
    <!-- Newspaper date header -->
    <div class="card-body space-y-1">
      <div>
        {#if start}
          <div class="form-group">
            <p class="start-end-word form-sibling">{start}</p>
            <input
              id="response"
              type="text"
              bind:value={userResponse}
              placeholder="..."
              class="form-input form-sibling p-4"
              disabled={isSubmitting}
            />
            <p class="start-end-word form-sibling">{end}</p>
          </div>
        {:else}
          <div class="loading-spinner w-8 h-8 mx-auto"></div>
        {/if}
      </div>
      {#if perplexity !== null}
        <div class="text-sm space-y-2 flex justify-around">
          <div class="flex items-center gap-2">
            {#if isGrammatical}
              <span class="text-green-600 font-medium">✓ looks good</span>
            {:else}
              <span class="text-yellow-600 font-medium">⚠ not grammatical</span
              >
            {/if}
          </div>
          <p class="color-brand-600">
            Perplexity score: {perplexity.toFixed(2)}
            <span class="text-xs">(lower is better)</span>
          </p>
        </div>
      {/if}

      {#if errorMessage}
        <div class="status-error">
          {errorMessage}
        </div>
      {/if}
      <div class="form-group">
        <div class="flex gap-4 mt-6 w-1/3 justify-center">
          <button
            class="btn-primary flex-1"
            on:click={submitResponse}
            disabled={isSubmitting || !userResponse.trim()}
          >
            {#if isSubmitting}
              <div class="loading-spinner w-5 h-5 mr-2"></div>
              Submitting...
            {:else}
              Submit
            {/if}
          </button>
        </div>
      </div>
      <p class="text-center text-sm text-gray-500 mt-4">A project by  <a href="https://eric-xia.com" target="_blank">(eric-xia.com)</a> Sc.B Math-CS, A.B. Linguistics '26</p>
    </div>
  </div>
</div>
