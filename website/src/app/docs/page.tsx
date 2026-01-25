import { redirect } from 'next/navigation';

export default function DocsPage() {
  // Redirect to SDK Reference by default
  redirect('/docs/sdk-reference');
}
