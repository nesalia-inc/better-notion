import { source } from '@/lib/source';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/lib/layout.shared';

export default function Layout({ children }: LayoutProps<'/docs'>) {
  return (
    <DocsLayout
      tree={source.getPageTree()}
      {...baseOptions()}
      sidebar={{
        ...baseOptions().sidebar,
        tabs: [
          {
            title: 'SDK Reference',
            description: 'High-level NotionClient SDK with rich entities',
            url: '/docs/sdk-reference',
          },
          {
            title: 'API Reference',
            description: 'Low-level NotionAPI reference',
            url: '/docs/api-reference',
          },
        ],
      }}
    >
      {children}
    </DocsLayout>
  );
}
