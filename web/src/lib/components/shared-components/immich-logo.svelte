<script lang="ts">
  import logoDarkUrl from '$lib/assets/pk-logo-inline-light.svg';
  import logoLightUrl from '$lib/assets/pk-logo-inline-light.svg';
  import logoNoText from '$lib/assets/pk-logo.svg';
  import { Theme } from '$lib/constants';
  import { colorTheme } from '$lib/stores/preferences.store';
  import { DateTime } from 'luxon';
  import type { HTMLImgAttributes } from 'svelte/elements';
  import { t } from 'svelte-i18n';

  interface Props extends HTMLImgAttributes {
    noText?: boolean;
    draggable?: boolean;
  }

  let { noText = false, draggable = false, ...rest }: Props = $props();

  const today = DateTime.now().toLocal();
</script>

  <img
    src={noText ? logoNoText : $colorTheme.value == Theme.LIGHT ? logoLightUrl : logoDarkUrl}
    alt={$t('logo')}
    {draggable}
    {...rest}
  />