<script lang="ts">
  import { browser } from '$app/environment';

  import { isSelectingAllAssets } from '$lib/stores/assets-store.svelte';
  import { mdiClose } from '@mdi/js';
  import { onDestroy, onMount, type Snippet } from 'svelte';
  import { t } from 'svelte-i18n';
  import { mobileDevice } from '$lib/stores/mobile-device.svelte';
  import { fly } from 'svelte/transition';
  import CircleIconButton from '../elements/buttons/circle-icon-button.svelte';

  interface Props {
    showBackButton?: boolean;
    backIcon?: string;
    tailwindClasses?: string;
    forceDark?: boolean;
    multiRow?: boolean;
    onClose?: () => void;
    leading?: Snippet;
    children?: Snippet;
    trailing?: Snippet;
  }

  let {
    showBackButton = true,
    backIcon = mdiClose,
    tailwindClasses = '',
    forceDark = false,
    multiRow = false,
    onClose = () => {},
    leading,
    children,
    trailing,
  }: Props = $props();

  let appBarBorder = $state('bg-light border border-transparent');

  const onScroll = () => {
    if (window.scrollY > 80) {
      appBarBorder = 'border border-gray-200 bg-gray-50 dark:border-gray-600';

      if (forceDark) {
        appBarBorder = 'border border-gray-600';
      }
    } else {
      appBarBorder = 'bg-light border border-transparent';
    }
  };

  const handleClose = () => {
    $isSelectingAllAssets = false;
    onClose();
  };

  onMount(() => {
    if (browser) {
      document.addEventListener('scroll', onScroll);
    }
  });

  onDestroy(() => {
    if (browser) {
      document.removeEventListener('scroll', onScroll);
    }
  });

  let buttonClass = $derived(forceDark ? 'hover:text-immich-dark-gray' : undefined);
</script>

<!-- Gavin made space around the search bar white, as it solves visual issues with image de-loading when scrolling.
     The change Gavin made in `web/src/routes/(user)/search/[[photos=photos]]/[[assetId=id]]/+page.svelte` is related to this. -->
<div in:fly={{ y: 10, duration: 200 }} class="absolute top-0 w-full bg-white">
  <nav
    id="asset-selection-app-bar"
    class={[
      'grid',
      multiRow && 'grid-cols-[100%] md:grid-cols-[25%_50%_25%]',
      !multiRow && 'grid-cols-[10%_80%_10%] sm:grid-cols-[25%_50%_25%]',
      'justify-between lg:grid-cols-[25%_50%_25%]',
      appBarBorder,
      'mx-2 mt-2 place-items-center rounded-lg p-2 max-md:p-0 transition-all',
      tailwindClasses,
      forceDark ? 'bg-immich-dark-gray! text-white' : 'bg-subtle dark:bg-immich-dark-gray',
    ]}
  >
    <div class="flex place-items-center sm:gap-6 justify-self-start dark:text-immich-dark-fg">
      {#if showBackButton}
        <CircleIconButton title={$t('close')} onclick={handleClose} icon={backIcon} size="24" class={buttonClass} />
      {/if}
      {@render leading?.()}
    </div>

    <div class="w-full">
      {@render children?.()}
    </div>

    <div class="me-4 flex place-items-center gap-1 justify-self-end">
      {@render trailing?.()}
    </div>
  </nav>
</div>
