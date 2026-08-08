import type { Preview } from '@storybook/react-vite';
import { withThemeByClassName } from '@storybook/addon-themes';
import React, { Suspense } from 'react';
import { I18nextProvider } from 'react-i18next';
import '../src/index.css';
import '../src/styles/themes.css';
import i18n from '../src/i18n';
import { applyTokens } from '../src/tokens/index.ts';
import { I18nWrapper } from './I18nWrapper';

applyTokens();

export const globalTypes = {
  locale: {
    name: 'Locale',
    description: 'Internationalization locale',
    toolbar: {
      icon: 'globe',
      items: [
        { value: 'en', title: 'English' },
        { value: 'de', title: 'Deutsch' }
      ],
      showName: true
    }
  }
};

const withI18next = (Story: React.ComponentType, context: { globals: { locale?: string } }) => {
  const locale = context.globals.locale ?? 'en';

  return (
    <Suspense fallback={null}>
      <I18nextProvider i18n={i18n}>
        <I18nWrapper locale={locale}>
          <Story />
        </I18nWrapper>
      </I18nextProvider>
    </Suspense>
  );
};

const preview: Preview = {
  decorators: [
    withThemeByClassName({
      themes: {
        light: 'theme-light',
        dark: 'theme-dark',
        print: 'theme-print',
        cosmic: 'theme-cosmic',
      },
      defaultTheme: 'cosmic',
    }),
    withI18next,
  ],

  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo',
      element: '#storybook-root',
      config: {},
      options: {}
    }
  },
};

export default preview;
