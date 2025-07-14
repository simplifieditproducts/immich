import { AppRoute } from '$lib/constants';
import { serverConfig } from '$lib/stores/server-config.store';
import { getFormatter } from '$lib/utils/i18n';
import { init } from '$lib/utils/server';

import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { loadUser } from '../lib/utils/auth';
import type { PageLoad } from './$types';
import { preferences as preferences$, user as user$, resetSavedUser } from '$lib/stores/user.store';

export const ssr = false;
export const csr = true;

console.log(`Loading routes/page.ts`);


export const load = (async ({ fetch }) => {
  try {
    console.log(`Calling 'load()' in web/src/routes/+page.ts`);

    // BEGIN auto-login logic added by Gavin.
    // To use auto-login, use `window.postMessage` to pass in `email` and `password` fields while opening the Immich Web UI.
    window.addEventListener("message", (event) => {



      const { autoEmail, autoPassword, autoUrl } = event.data;
      if (!autoEmail || !autoPassword) { return };

      const url = new URL(autoUrl);
      const cachedEmail = get(user$);

      console.log(`Page.ts 'message' event listener fired with autoEmail: ${autoEmail} and cachedEmail: ${cachedEmail.email}`)

      if(cachedEmail && cachedEmail.email != autoEmail) {
        console.log(`Trying to redirect to LOGIN`)
        redirect(302, `${AppRoute.AUTH_LOGIN}?continue=${encodeURIComponent(url.pathname + url.search)}`);
      }



      //email = autoEmail;
      //password = autoPassword;

      console.log(`Page.ts auto-login started with email: ${autoEmail}`);
      // TODO: I need to somehow pass the email and password found above into the LOGIN page.
      //handleLogin().catch((error) => console.error("Auto-login failed", error));
    });
    // END auto-login logic added by Gavin.



    await init(fetch);

    // const authenticated = await loadUser();
    // if (authenticated) {
    //   //console.log(`Redirecting to PHOTOS page from web/src/routes/+page.ts, as user is authenticated`);
    //   // TODO: I've commented this out to prevent an already logged in user from being logged in automatically without checking for updated credentials passed from PKC app.
    //   //redirect(302, AppRoute.PHOTOS);
    // }

    const { isInitialized } = get(serverConfig);
    if (isInitialized) {
      // Redirect to login page if there exists an admin account (i.e. server is initialized)
      console.log(`Redirecting to LOGIN page from web/src/routes/+page.ts, as user is unauthenticated but an admin account exists on the server`);
      redirect(302, AppRoute.AUTH_LOGIN);
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (redirectError: any) {
    if (redirectError?.status === 302) {
      throw redirectError;
    }
  }

  const $t = await getFormatter();

  return {
    meta: {
      title: $t('welcome') + ' 🎉',
      description: $t('immich_web_interface'),
    },
  };
}) satisfies PageLoad;
