<script lang="ts">
  import { Card, CardBody, CardHeader, Heading, VStack } from '@immich/ui';
  import type { Snippet } from 'svelte';
  import shieldLogo from '$lib/assets/shield-logo-with-text.png';
  
  interface Props {
    title?: string;
    children?: Snippet;
    withHeader?: boolean;
  }

  let { title, children, withHeader = true }: Props = $props();
</script>

<section class="min-w-dvw flex min-h-dvh items-center justify-center relative">
  <div class="absolute -z-10 w-full h-full flex place-items-center place-content-center">
    <img
      src={shieldLogo}
      class="max-w-(--breakpoint-md) mx-auto h-full mb-2 antialiased overflow-hidden"
      alt="Shield Logo"
    />
    <div
      class="w-full h-[99%] absolute start-0 top-0 backdrop-blur-[200px] bg-transparent dark:bg-immich-dark-bg/20"
    ></div>
  </div>

  <Card color="secondary" class="w-full max-w-lg border m-2">
    {#if withHeader}
      <CardHeader class="mt-6">
        <VStack class="gap-5">
          <img src={shieldLogo} alt="Shield Logo" class="w-38 mx-auto" />
          <Heading size="large" class="font-semibold" color="primary" tag="h1">{title}</Heading>
        </VStack>
      </CardHeader>
    {/if}

    <CardBody class="p-8">
      {@render children?.()}
    </CardBody>
  </Card>
</section>
