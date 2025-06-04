<script lang="ts">
  import type { HTMLImgAttributes } from 'svelte/elements';
  import { t } from 'svelte-i18n';
  import logoDarkUrl from '$lib/assets/pk-logo-inline-dark.svg';
  import logoLightUrl from '$lib/assets/pk-logo-inline-light.svg';
  import logoNoText from '$lib/assets/pk-logo.svg';

  interface Props extends HTMLImgAttributes {
    noText?: boolean;
    draggable?: boolean;
  }

  let { noText = false, draggable = false, ...rest }: Props = $props();

  const logoUrl = $derived(
    noText ? logoNoText : logoLightUrl,
  );

</script>

<img src={logoUrl} alt={$t('immich_logo')} {draggable} {...rest} />
